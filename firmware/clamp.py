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


def clamp(clk, data, stb, bits):

    #hard clamp
    maxval = (2**(bits-1))-1
    minval = -maxval

    positive_overflow = data > maxval
    data = data.subtype.select(positive_overflow, data, maxval)
    negative_overflow = data < minval
    data = data.subtype.select(negative_overflow, data, minval)
    
    data = data.resize(bits)
    data = data.subtype.register(clk, d=data, init=0, en=stb)
    stb = stb.subtype.register(clk, d=stb)

    return data, stb

if __name__ == "__main__" and "sim" in sys.argv:

    clk = Clock("clk")
    audio_in = Signed(16).input("magnitude")
    stb_in = Boolean().input("stb")

    audio_out, stb_out, _ = audio_agc(clk, audio_in, stb_in, Unsigned(8).constant(0), Unsigned(8).constant(0))

    clk.initialise()
    response = []

    for i in range(100):
        audio_in.set(100)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            if stb_out.get():
                x = audio_out.get()
                response.append(x)
        audio_in.set(-100)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            if stb_out.get():
                x = audio_out.get()
                response.append(x)
    for i in range(100):
        audio_in.set(0)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            if stb_out.get():
                x = audio_out.get()
                response.append(x)
    for i in range(100):
        audio_in.set(100)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            if stb_out.get():
                x = audio_out.get()
                response.append(x)
        audio_in.set(-100)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            if stb_out.get():
                x = audio_out.get()
                response.append(x)

    plt.plot(response)
    plt.show()
