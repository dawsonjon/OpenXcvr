from baremetal import *
from baremetal.signed import number_of_bits_needed
from settings import Settings
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from numpy import log10


def measure_magnitude(clk, audio, audio_stb):

    #use a leaky max hold
    factor = 16 #T=~0.5s @ fs=100e-3
    audio_bits = audio.subtype.bits

    #add extra bits for decay calculation
    audio = audio.resize(audio_bits+factor) << factor

    #implement leaky max/min hold
    max_hold = audio.subtype.register(clk, init=0, en=audio_stb)
    max_hold.d(audio.subtype.select(audio > max_hold, max_hold - (max_hold >> factor), audio))

    #remove extra bits (except one to allow for addition)
    max_hold = (max_hold >> factor).resize(audio_bits)

    return max_hold

if __name__ == "__main__" and "sim" in sys.argv:

    settings = Settings()
    settings.agc_frame_size = 100
    settings.agc_frames = 4
    clk = Clock("clk")
    data_in = Signed(9).input("data_in")
    stb_in = Boolean().input("stb_in")
    dc, magnitude = measure_magnitude(clk, data_in, stb_in, settings)

    stimulus = []
    for i in range(1000):
        stimulus.append(0)
    for i in range(100):
        stimulus.append(0)
        stimulus.append(22)
        stimulus.append(-18)
    for i in range(300):
        stimulus.append(0)
    for i in range(100):
        stimulus.append(0)
        stimulus.append(22)
        stimulus.append(-18)
    for i in range(1000):
        stimulus.append(0)
    for i in range(100):
        stimulus.append(0)
        stimulus.append(200)
        stimulus.append(-200)
    for i in range(1000):
        stimulus.append(0)

    response = []

    #simulate
    clk.initialise()

    stb_in.set(1)
    i = 0
    for data in stimulus:
        data_in.set(data)
        clk.tick()
        response.append(magnitude.get())
        i+=1

    response = np.array(response)

    plt.plot(response)
    plt.plot(stimulus)
    plt.show()
