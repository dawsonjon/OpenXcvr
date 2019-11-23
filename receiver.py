from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from audio_agc import audio_agc
from filter import filter


def receiver(clk, af_i, af_q, af_stb, squelch, lut_bits, fraction_bits, frame_size, frames, taps, kernel_bits):
    audio, _, audio_stb = filter(clk, af_i, af_q, af_stb, taps, kernel_bits)
    audio, audio_stb = audio_agc(clk, audio, audio_stb, squelch, lut_bits, fraction_bits, frame_size, frames)

    return audio, audio_stb



if __name__ == "__main__" and "sim" in sys.argv:
    taps = 127
    kernel_bits = 18
    frame_size = 800
    frames = 2
    lut_bits = 7
    lut_fraction_bits = 8

    clk = Clock("clk")
    i_data_in = Signed(16).input("i_data_in")
    q_data_in = Signed(16).input("q_data_in")
    stb_in = Boolean().input("stb_in")
    squelch_in = Signed(16).input("squelch")

    audio, audio_stb = receiver(clk, i_data_in, q_data_in, stb_in, 
            squelch_in, lut_bits, lut_fraction_bits, frame_size,
            frames, taps, kernel_bits)

    stimulus=np.exp(-1.0j*np.arange(3000)*2.0*pi*0.05)*((2**15)-1)*0.25+0.5

    #simulate
    clk.initialise()
    squelch_in.set(0)

    response = []
    for data in stimulus:
        for j in range(taps+2):
            stb_in.set(j==taps+1)
            i_data_in.set(np.real(data))
            q_data_in.set(np.imag(data))
            clk.tick()
            if audio_stb.get():
                print audio.get()
                response.append(audio.get())

    response = np.array(response)
    plt.plot(response)
    plt.show()
