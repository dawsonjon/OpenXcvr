from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain
from slow_barrel_shifter import slow_barrel_shifter


def mic_compression(clk, data, stb):

    half_way = (2**(data.subtype.bits-2))-1

    maxval = half_way
    minval = -half_way

    positive_overflow = data > maxval
    positive_excess = (data - maxval) >> 1
    data = data.subtype.select(positive_overflow, data, positive_excess+maxval)

    negative_overflow = data < minval
    negative_excess = (data.subtype.constant(minval) - data) >> 1
    data = data.subtype.select(negative_overflow, data, -negative_excess+minval)

    data = data.subtype.register(clk, d=data, init=0, en=stb)
    stb = stb.subtype.register(clk, d=stb)

    return data, stb

if __name__ == "__main__" and "sim" in sys.argv:

    clk = Clock("clk")
    audio_in = Signed(8).input("magnitude")
    stb_in = Boolean().input("stb")

    audio_out, stb_out = mic_compress(clk, audio_in, stb_in)

    clk.initialise()
    response = []

    for j in range(-128, 127):
        audio_in.set(j)
        stb_in.set(1)
        for i in range(100):
            clk.tick()
            if stb_out.get():
                x = audio_out.get()
                response.append(x)

    plt.plot(response)
    plt.show()
