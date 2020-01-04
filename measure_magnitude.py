from baremetal import *
from baremetal.signed import number_of_bits_needed
from settings import Settings
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from numpy import log10


def measure_magnitude(clk, data_in, stb, settings):
    frame_size = settings.agc_frame_size
    frames = settings.agc_frames

    frame_count, eop = counter(clk, 0, frame_size-1, 1)
    sop = frame_count == 0

    #find the largest value in a frame
    t_data = data_in.subtype     
    maxval = t_data.register(clk, init=0, en=stb)
    minval = t_data.register(clk, init=0, en=stb)
    maxval.d(t_data.select(sop, t_data.select(data_in > maxval, maxval, data_in), data_in))
    minval.d(t_data.select(sop, t_data.select(data_in < minval, minval, data_in), data_in))
    stb = Boolean().register(clk, d=stb&eop, init=0)

    maxval.subtype.register(clk, d=maxval, en=stb, init=0)
    minval.subtype.register(clk, d=minval, en=stb, init=0)
    

    #calculate magnitude
    maxval = maxval.resize(t_data.bits+1)
    magnitude = (maxval - minval) >> 1
    dc = (maxval + minval) >> 1
    #magnitude = magnitude.resize(t_data.bits)
    dc = dc.resize(t_data.bits)


    return dc, magnitude

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
