from baremetal import *
from math import pi, sin, cos
import sys
from scale import scale
from settings import *



def modulator(clk, audio, audio_stb, settings):
    magnitude = Unsigned(12).constant(0) + audio + 2048
    phase = Unsigned(12).constant(0)
    return magnitude, phase, audio_stb

import numpy as np
from matplotlib import pyplot as plt

def test_modulator(stimulus, mode):

    settings = Settings()
    settings.mode = Unsigned(3).input("filter_mode")

    clk = Clock("clk")
    audio_in = Signed(8).input("i_data_in")
    audio_stb_in = Boolean().input("stb_in")

    i, q, stb = modulator(clk, audio_in, audio_stb_in, settings) 

    #simulate
    clk.initialise()
    settings.mode.set(mode)

    response = []
    for data in stimulus:
        for j in range(5):
            audio_stb_in.set(j==4)
            audio_in.set(data)
            clk.tick()
            if stb.get():
                print i.get(), q.get()
                response.append(i.get()+1j*q.get())

    response = np.array(response)
    plt.title("Modulator")
    plt.xlabel("Time (samples)")
    plt.ylabel("Value")
    a, = plt.plot(np.real(response), label="I")
    b, = plt.plot(np.imag(response), label="Q")
    c, = plt.plot(stimulus, label="Audio Input")
    plt.legend(handles=[a, b, c])
    plt.show()




if __name__ == "__main__" and "sim" in sys.argv:

    #mode am stim am
    stimulus=(
        np.sin(np.arange(10000)*2.0*pi*0.01)>0#*
        #((2**7)-1)-1#scale to 16 bits
    )
    test_modulator(stimulus, AM)
    #test_modulator(stimulus, FM)
    #test_modulator(stimulus, NBFM)
    #test_modulator(stimulus, SSB)
