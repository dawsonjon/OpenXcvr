from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys

def create_filter(frequency_response, taps=511):

    #take inverse fft of desired response
    frequency_response = np.fft.fftshift(frequency_response)

    #create a filter kernel by windowing the desired response
    impulse_response = np.fft.ifft(frequency_response)
    impulse_response = np.concatenate([impulse_response[-taps/2:], impulse_response[0:taps/2]])
    kernel = impulse_response * np.blackman(taps)

    #quantise kernel
    kernel = kernel
    kernel = np.round(kernel*(2**17)) 

    padded_kernel = np.concatenate([np.zeros(1024), kernel, np.zeros(1024)])
    gain = max(abs(np.fft.fft(padded_kernel)))
    print gain/2**23
    plt.plot(np.linspace(-48000, 48000, len(padded_kernel)), 20*np.log10(abs(np.fft.fftshift(np.fft.fft(padded_kernel)))))
    plt.show()

    return kernel

taps = 127

usb_response    = np.concatenate([np.zeros(256), np.ones(256)*(0.7+0.7j)])
lsb_response    = np.concatenate([np.ones(256)*(0.7+0.7j), np.zeros(256)])
#lsb_response    = np.concatenate([np.zeros(240), np.ones(16)*(0.7+0.7j), np.zeros(256)])
narrow_response = np.concatenate([np.zeros(240), np.ones(32)*(0.7+0.7j), np.zeros(240)])
wide_response   = np.concatenate([np.zeros(224), np.ones(64)*(0.7+0.7j), np.zeros(224)])

usb_kernel    = create_filter(usb_response, taps)
lsb_kernel    = create_filter(lsb_response, taps)
narrow_kernel = create_filter(narrow_response, taps)
wide_kernel   = create_filter(wide_response, taps)


print(np.max(usb_kernel))

def multiply(clk, data, kernel):
    data = data.resize(data.subtype.bits+kernel.subtype.bits-1)
    product = data * kernel
    product = product.subtype.register(clk, d=product)
    return product

def filter(clk, data_i, data_q, stb, n, kernel_bits, kernel_i, kernel_q):
    kernel_type = Signed(kernel_bits)

    #generate addresses
    en = Boolean().wire()
    count, _ = counter(clk, 0, n, 1, en)
    address, _ = counter(clk, 0, n-1, 1, en)
    read = count != n
    en.drive(read|stb)#wait for a strobe
    sop = count == 0
    eop = count == n-1

    #create RAM
    buf_i = data_i.subtype.ram(clk=clk, depth=n)
    buf_q = data_q.subtype.ram(clk=clk, depth=n)

    #write data into RAM
    buf_i.write(address, data_i, ~read & stb) 
    buf_q.write(address, data_q, ~read & stb) 

    #read_data_from_RAM
    data_i = buf_i.read(address)
    data_q = buf_q.read(address)
    kernel_i = kernel_type.rom(count, *kernel_i)
    kernel_q = kernel_type.rom(count, *kernel_q)

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

    product_bits = product_i_0.subtype.bits
    product_i = product_i_0.resize(product_bits+1) - product_i_1
    product_q = product_q_0.resize(product_bits+1) + product_q_1
    product_i = product_i.subtype.register(clk, d=product_i)
    product_q = product_q.subtype.register(clk, d=product_q)
    sop = sop.subtype.register(clk, d=sop)
    eop = eop.subtype.register(clk, d=eop)

    #accumulate products
    s = Signed(product_i.subtype.bits+int(log(n, 2)))
    accumulator_i = s.register(clk, init=0)
    accumulator_q = s.register(clk, init=0)
    accumulator_i.d(s.select(sop, accumulator_i+product_i, product_i))
    accumulator_q.d(s.select(sop, accumulator_q+product_q, product_q))
    eop = eop.subtype.register(clk, d=eop)

    #remove excess bits
    accumulator_i = (accumulator_i>>(kernel_bits-2)).resize(data_i.subtype.bits)
    accumulator_q = (accumulator_q>>(kernel_bits-2)).resize(data_q.subtype.bits)
    return  accumulator_i, accumulator_q, eop

#make filter
clk = Clock("clk")
stb_in = Boolean().input("stb")
data_i_in = Signed(16).input("data_i_in")
data_q_in = Signed(16).input("data_q_in")
data_i_out, data_q_out, stb_out = filter(clk, data_i_in, data_q_in, stb_in, taps, 18, np.real(lsb_kernel), np.imag(lsb_kernel))

if "sim" in sys.argv:
    stimulus =np.sin(np.arange(3000)*2.0*pi*0.1)*((2**15)-1)

    plt.plot(np.real(stimulus))
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

    for x in range(2000):
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

    plt.plot(20*np.log10(abs(np.fft.fftshift(np.fft.fft(output_i[500:] + 1.0j*np.array(output_q[500:]))))))
    plt.show()

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
