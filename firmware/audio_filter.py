from baremetal import *
from settings import *

from math import log, pi, ceil
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
import sys

def make_kernel(taps, kernel_bits):
    kernel = signal.firwin(taps, [0.6/50, 6.0/50], window="blackman", pass_zero=False)
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
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Gain (dB)")
    plt.plot(
            np.linspace(-25.0, 25.0, len(response_0)), 
            response_0
    )
    plt.show()


def multiply(clk, data, kernel):
    data = data.resize(data.subtype.bits+kernel.subtype.bits-1)
    product = data * kernel
    product = product.subtype.register(clk, d=product)
    return product

def audio_filter(clk, data, stb):

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
    buf = data.subtype.ram(clk=clk, depth=taps)

    #write data into RAM
    write_enable = (~read & stb)
    buf.write(address, data, write_enable) 

    #read_data_from_RAM
    data = buf.read(address)
    kernel = kernel_type.rom(count, *kernel)

    data = data.subtype.register(clk, d=data)
    kernel = kernel.subtype.register(clk, d=kernel)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #multiply kernel by data
    product = multiply(clk, data, kernel)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #accumulate products
    s = Signed(product.subtype.bits+int(ceil(log(taps, 2))))
    accumulator = s.register(clk, init=0)
    accumulator.d(s.select(sop, accumulator+product, product))
    eop = eop.subtype.register(clk, d=eop)

    #remove excess bits
    accumulator = (accumulator>>kernel_bits-2).resize(data.subtype.bits)
    return  accumulator, eop

def test_filter(stimulus):

    settings = Settings()
    settings.filter_kernel_bits = 18 

    taps = 255

    clk = Clock("clk")
    stb_in = Boolean().input("stb")
    data_i_in = Signed(16).input("data_i_in")
    data_q_in = Signed(16).input("data_q_in")
    data_out, stb_out = audio_filter(clk, data_in, stb_in)

    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.show()
    stimulus = iter(stimulus)

    #simulate
    clk.initialise()

    input_value = 0
    data_in.set(next(stimulus))
    stb_in.set(0)
    output_i = []
    output_q = []

    for x in range(3000):
        for j in range(taps+2):

            if j == taps+1:
                data_in.set(next(stimulus))
                input_value += 1

            if stb_out.get():
                print(data_i_out.get())
                sample = data_out.get()
                if sample is not None:
                    output.append(sample)

            clk.tick()
            stb_in.set(int(j==taps+1))

    plt.plot(output)
    plt.show()

    output = np.array(output[500:])
    stimulus = np.array(stimulus[500:])
    stimulus = stimulus[:len(output)]

    plt.plot(
        np.linspace(-6, 6, len(response_1)), 
        20*np.log10(abs(np.fft.fftshift(np.fft.fft(stimulus))))
    )
    plt.plot(
        np.linspace(-6, 6, len(response_1)), 
        20*np.log10(abs(np.fft.fftshift(np.fft.fft(output))))
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

    if "plot" in sys.argv:
        plot_kernel(255, 18)

