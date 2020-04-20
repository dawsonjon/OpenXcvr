from baremetal import *

def decimate(clk, i, q, stb, ratio):
    _, last = counter(clk, 0, ratio-1, 1, en=stb)
    i = i.subtype.register(clk, d=i, init=0, en=stb&last)
    q = q.subtype.register(clk, d=q, init=0, en=stb&last)
    stb = stb.subtype.register(clk, d=stb&last, init=0)

    return i, q, stb

import sys
import numpy as np
from math import pi
from matplotlib import pyplot as plt
if __name__ == "__main__" and "sim" in sys.argv:


    rx_i_in = Signed(16).input("i_data_in")
    rx_q_in = Signed(16).input("q_data_in")
    rx_stb_in = Boolean().input("stb_in")
    clk = Clock("clk")

    rx_i_out, rx_q_out, rx_stb = decimate(clk, rx_i_in, rx_q_in, rx_stb_in, 4) 

    #mode am stim tx
    stimulus=(
        np.exp(1.0j*np.arange(1000)*2.0*pi*0.01)*
        ((2**7)-1)#scale to 16 bits
    )

    #simulate
    clk.initialise()

    i_response  = []
    q_response  = []
    for data in stimulus:
        for j in range(10):
            rx_stb_in.set(j==9)
            rx_i_in.set(np.real(data))
            rx_q_in.set(np.imag(data))
            clk.tick()
            if rx_stb.get():
                print rx_i_out.get(), rx_q_out.get()
                i_response.append(rx_i_out.get())
                q_response.append(rx_q_out.get())

    response = np.array(i_response)+1.0j*np.array(q_response)

    #response = np.array(response)
    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.plot(np.real(response))
    plt.plot(np.imag(response))
    plt.show()
    plt.plot(abs(np.fft.fftshift(np.fft.fft(response))))
    plt.show()
