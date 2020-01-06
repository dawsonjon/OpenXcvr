from baremetal import *
from settings import *

from math import log, pi, ceil
from matplotlib import pyplot as plt
import numpy as np
import sys

def make_kernel(taps, kernel_bits):

    #each step represents 1/512 of 100kHz ~200Hz
    usb_response_0 = np.concatenate([np.zeros(256), np.ones(28), np.zeros(226)]) #~3KHz SSB
    usb_response_1 = np.concatenate([np.zeros(225), 1*np.ones(62), np.zeros(225)]) #~6KHz  AM
    usb_response_2 = np.concatenate([np.zeros(179), 0.9*np.ones(154), np.zeros(179)]) #~15KHz   FM
    usb_response_3 = np.concatenate([np.zeros(209), 1*np.ones(94), np.zeros(209)]) #~9KHz    NFM

    #In Max10 9k block ram supports 512*18 so 1 BRAM can store 128
    return np.concatenate([
        create_filter(usb_response_0, taps, kernel_bits), [0], 
        create_filter(usb_response_1, taps, kernel_bits), [0], 
        create_filter(usb_response_2, taps, kernel_bits), [0], 
        create_filter(usb_response_3, taps, kernel_bits), [0] 
        ]
    )

def create_filter(frequency_response, taps=511, kernel_bits=18):

    #take inverse fft of desired response
    frequency_response = np.fft.fftshift(frequency_response)

    #create a filter kernel by windowing the desired response
    impulse_response = np.fft.ifft(frequency_response)
    impulse_response = np.concatenate([impulse_response[-taps/2:], impulse_response[0:taps/2]])
    kernel = impulse_response * np.blackman(taps)

    #quantise kernel
    kernel = np.round(kernel*(2**kernel_bits - 1)) 
    #padded_kernel = np.concatenate([np.zeros(1024), kernel, np.zeros(1024)])
    #plt.plot(np.linspace(-25000, 25000, len(padded_kernel)), 20*np.log10(abs(np.fft.fftshift(np.fft.fft(padded_kernel)))))
    #plt.show()

    return kernel

def multiply(clk, data, kernel):
    data = data.resize(data.subtype.bits+kernel.subtype.bits-1)
    product = data * kernel
    product = product.subtype.register(clk, d=product)
    return product

def filter(clk, data_i, data_q, stb, settings):

    taps = 255 #chose a power of 2 - 1
    kernel_type = Signed(settings.filter_kernel_bits)
    kernel = make_kernel(taps, settings.filter_kernel_bits)
    kernel_i = np.real(kernel)
    kernel_q = np.imag(kernel)

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
    count = count.label("read_address")
    data_i = data_i.label("read_data_i")
    data_q = data_q.label("read_data_q")
    kernel_i = kernel_type.rom(settings.mode.cat(count), *kernel_i)
    kernel_q = kernel_type.rom(settings.mode.cat(count), *kernel_q)

    data_i = data_i.subtype.register(clk, d=data_i)
    data_q = data_q.subtype.register(clk, d=data_q)
    kernel_i = kernel_i.subtype.register(clk, d=kernel_i)
    kernel_q = kernel_q.subtype.register(clk, d=kernel_q)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #select sideband
    #0=lsb
    #1=usb
    t_i = kernel_type.select(settings.sideband, kernel_i, kernel_q)
    t_q = kernel_type.select(settings.sideband, kernel_q, kernel_i)
    kernel_i = t_i
    kernel_q = t_q

    data_i = data_i.subtype.register(clk, d=data_i)
    data_q = data_q.subtype.register(clk, d=data_q)
    kernel_i = kernel_i.subtype.register(clk, d=kernel_i)
    kernel_q = kernel_q.subtype.register(clk, d=kernel_q)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #multiply kernel by data
    product_i_0 = multiply(clk, data_i, kernel_i)
    product_i_1 = multiply(clk, data_q, kernel_q)
    product_q_0 = multiply(clk, data_i, kernel_q)
    product_q_1 = multiply(clk, data_q, kernel_i)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #product_bits = product_i_0.subtype.bits
    product_i = product_i_0 - product_i_1
    product_q = product_q_0 + product_q_1
    product_i = product_i.subtype.register(clk, d=product_i)
    product_q = product_q.subtype.register(clk, d=product_q)
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
    accumulator_i = (accumulator_i>>(settings.filter_kernel_bits+1)).resize(data_i.subtype.bits)
    accumulator_q = (accumulator_q>>(settings.filter_kernel_bits+1)).resize(data_q.subtype.bits)
    return  accumulator_i, accumulator_q, eop

def test_filter(stimulus, filt, sideband):

    settings = Settings()
    settings.filter_kernel_bits = 18 
    settings.mode   = Unsigned(2).input("mode")
    settings.sideband               = Unsigned(2).input("sideband_select")

    taps = 255

    clk = Clock("clk")
    stb_in = Boolean().input("stb")
    data_i_in = Signed(16).input("data_i_in")
    data_q_in = Signed(16).input("data_q_in")
    data_i_out, data_q_out, stb_out = filter(clk, data_i_in, data_q_in, stb_in, settings)

    settings.mode.set(filt)
    settings.sideband.set(sideband)

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

    plt.plot(20*np.log10(abs(np.fft.fftshift(np.fft.fft(stimulus)))))
    plt.plot(20*np.log10(abs(np.fft.fftshift(np.fft.fft(output_i + 1.0j*output_q)))))
    plt.show()

if __name__ == "__main__":

    if "sim" in sys.argv:

        #mode wbfm
        audio=np.sin(np.arange(4000)*2.0*pi*0.01)
        frequency = audio * 0.05 * pi#0.1*+/-50kHZ = +/-5KHz
        phase = np.cumsum(frequency)
        stimulus = (
            np.exp(1.0j*phase)*
            ((2**7)-1)#scale to 16 bits
        )
        test_filter(stimulus, FM, USB)

        #mode nfm
        audio=np.sin(np.arange(4000)*2.0*pi*0.01)
        frequency = audio * 0.025 * pi#0.1*+/-50kHZ = +/-5KHz
        phase = np.cumsum(frequency)
        stimulus = (
            np.exp(1.0j*phase)*
            ((2**7)-1)#scale to 16 bits
        )
        test_filter(stimulus, NBFM, LSB)

        #mode usb stim dsb
        stimulus=(
            (np.sin(np.arange(4000)*2.0*pi*0.01)+1j*np.sin(np.arange(4000)*2.0*pi*0.01))*
            ((2**7)-1)#scale to 16 bits
        )
        test_filter(stimulus, SSB, USB)

        #mode am stim am
        stimulus=(
            np.exp(1j*np.arange(4000)*2.0*pi*0.0005)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
            (np.sin(np.arange(4000)*2.0*pi*0.01)*0.5+0.5)* #The signal a tone
            ((2**15)-1)#scale to 16 bits
        )
        test_filter(stimulus, AM, 0)

        #mode usb stim dsb
        stimulus=(
            np.sin(np.arange(4000)*2.0*pi*0.01)*
            ((2**15)-1)#scale to 16 bits
        )
        test_filter(stimulus, SSB, USB)

        #mode am tx
        stimulus=(
            ((np.sin(np.arange(4000)*2.0*pi*0.01)*0.5+0.5)+ #The signal a tone
            (1j*np.sin(np.arange(4000)*2.0*pi*0.01)*0.5+0.5j))* #The signal a tone
            ((2**15)-1)#scale to 16 bits
        )
        test_filter(stimulus, AM, LSB)

        #mode wbfm
        audio=np.sin(np.arange(4000)*2.0*pi*0.01)
        frequency = audio * 0.05 * pi#0.1*+/-50kHZ = +/-5KHz
        phase = np.cumsum(frequency)
        stimulus = (
            np.exp(1.0j*phase)*
            ((2**15)-1)#scale to 16 bits
        )
        test_filter(stimulus, FM, USB)

        #mode nfm
        audio=np.sin(np.arange(4000)*2.0*pi*0.01)
        frequency = audio * 0.025 * pi#0.1*+/-50kHZ = +/-5KHz
        phase = np.cumsum(frequency)
        stimulus = (
            np.exp(1.0j*phase)*
            ((2**15)-1)#scale to 16 bits
        )
        test_filter(stimulus, NBFM, LSB)


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
