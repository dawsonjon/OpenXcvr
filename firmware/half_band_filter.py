from baremetal import *
from settings import *

from math import log, pi, ceil
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
import sys

def make_kernel(taps, kernel_bits):
    kernel = signal.firwin(taps, 0.5, window="blackman")
    kernel = np.round(kernel * (2.0**(kernel_bits-1.0)))
    return kernel

def frequency_response(kernel, kernel_bits):
    response = np.concatenate([kernel, np.zeros(1024)])
    response /= (2.0**kernel_bits - 1.0) 
    response = 20*np.log10(abs(np.fft.fftshift(np.fft.fft(response))))
    return response

def plot_kernel(taps, kernel_bits):
    response_0 = frequency_response(make_kernel(taps, kernel_bits), kernel_bits)  #Narrow

    plt.figure()

    plt.grid(True)
    plt.title("Narrow")
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Gain (dB)")
    plt.plot(
            np.linspace(-12.5, 12.5, len(response_0)), 
            response_0
    )
    plt.show()


def multiply(clk, data, kernel):
    data = data.resize(data.subtype.bits+kernel.subtype.bits-1)
    product = data * kernel
    product = product.subtype.register(clk, d=product)
    return product

def half_band_filter(clk, data_i, data_q, stb):

    taps = 255 #choose a power of 2 - 1
    kernel_bits = 18
    kernel_type = Signed(kernel_bits)
    kernel = make_kernel(taps, kernel_bits)
    kernel = [int(i) for i in kernel]

    #generate addresses
    en = Boolean().wire()
    count, _ = counter(clk, 0, taps, 1, en)
    address, _ = counter(clk, 0, taps-1, 1, en)
    read = count != taps
    en.drive(read|stb)#wait for a strobe
    sop = count == 0
    eop = count == taps-1

    #create RAM
    buf_i = data_i.subtype.ram(clk=clk, depth=taps)
    buf_q = data_q.subtype.ram(clk=clk, depth=taps)

    #write data into RAM
    address = address.label("write_address")
    data_i = data_i.label("write_data_i")
    data_q = data_q.label("write_data_q")
    write_enable = (~read & stb).label("write_enable")
    buf_i.write(address, data_i, write_enable) 
    buf_q.write(address, data_q, write_enable) 

    #read_data_from_RAM
    data_i = buf_i.read(address)
    data_q = buf_q.read(address)
    kernel = kernel_type.rom(count, *kernel)

    data_i = data_i.subtype.register(clk, d=data_i)
    data_q = data_q.subtype.register(clk, d=data_q)
    kernel = kernel.subtype.register(clk, d=kernel)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #multiply kernel by data
    product_i = multiply(clk, data_i, kernel)
    product_q = multiply(clk, data_q, kernel)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #accumulate products
    s = Signed(product_i.subtype.bits+int(ceil(log(taps, 2))))
    accumulator_i = s.register(clk, init=0)
    accumulator_q = s.register(clk, init=0)
    accumulator_i.d(s.select(sop, accumulator_i+product_i, product_i))
    accumulator_q.d(s.select(sop, accumulator_q+product_q, product_q))
    eop = eop.subtype.register(clk, d=eop)

    #remove excess bits
    accumulator_i = (accumulator_i>>kernel_bits-2).resize(data_i.subtype.bits)
    accumulator_q = (accumulator_q>>kernel_bits-2).resize(data_q.subtype.bits)
    return  accumulator_i, accumulator_q, eop

def test_filter(stimulus):

    settings = Settings()
    settings.filter_kernel_bits = 18 

    taps = 127

    clk = Clock("clk")
    stb_in = Boolean().input("stb")
    data_i_in = Signed(16).input("data_i_in")
    data_q_in = Signed(16).input("data_q_in")
    data_i_out, data_q_out, stb_out = half_band_filter(clk, data_i_in, data_q_in, stb_in)

    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.show()
    stimulus_i = iter(np.real(stimulus))
    stimulus_q = iter(np.imag(stimulus))

    #simulate
    clk.initialise()

    input_value = 0
    data_i_in.set(next(stimulus_i))
    data_q_in.set(next(stimulus_q))
    stb_in.set(0)
    output_i = []
    output_q = []

    for x in range(3000):
        for j in range(taps+2):

            if j == taps+1:
                data_i_in.set(next(stimulus_i))
                data_q_in.set(next(stimulus_q))
                input_value += 1

            if stb_out.get():
                print(data_i_out.get(), data_q_out.get())
                sample_i = data_i_out.get()
                sample_q = data_q_out.get()
                if sample_i is not None:
                    output_i.append(sample_i)
                    output_q.append(sample_q)

            clk.tick()
            stb_in.set(int(j==taps+1))

    plt.plot(output_i)
    plt.plot(output_q)
    plt.show()

    output_i = np.array(output_i[500:])
    output_q = np.array(output_q[500:])
    stimulus = np.array(stimulus[500:])
    stimulus = stimulus[:len(output_i)]

    plt.plot(
        np.linspace(-6, 6, len(response_1)), 
        20*np.log10(abs(np.fft.fftshift(np.fft.fft(stimulus))))
    )
    plt.plot(
        np.linspace(-6, 6, len(response_1)), 
        20*np.log10(abs(np.fft.fftshift(np.fft.fft(output_i + 1.0j*output_q))))
    )
    plt.show()

if __name__ == "__main__":

    if "sim" in sys.argv:

        #mode usb stim usb
        stimulus=(
            (
                np.sin(np.arange(4000)*2.0*pi*0.01)+
                np.sin(np.arange(4000)*2.0*pi*0.02)+
                np.sin(np.arange(4000)*2.0*pi*0.03)
            ) * ((2**13)-1)#scale to 16 bits
        )
        test_filter(stimulus)


    if "gen" in sys.argv:

        data_i_out = data_i_out.subtype.output("data_i_out", data_i_out)
        data_q_out = data_q_out.subtype.output("data_q_out", data_q_out)
        stb_out = stb_out.subtype.output("stb_out", stb_out)

        netlist = Netlist(
            "filter",
            [clk], 
            [data_i_in, data_q_in, stb_in],
            [data_i_out, data_q_out, stb_out],
        )
        f = open("filter.v", "w")
        f.write(netlist.generate())

    if "plot" in sys.argv:
        plot_kernel(255, 18)

