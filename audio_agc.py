from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain


def audio_agc(clk, data, stb):

    #calculate magnitude and DC
    magnitude = measure_magnitude(clk, data, stb)

    #rescale the data 
    setpoint = (2**(data.subtype.bits-1)) * 0.67
    gain = calculate_gain(clk, magnitude, setpoint)
    gain = gain.subtype.select(gain < 1, gain, 1)

    #scale by 2**e
    data = data * gain
    data = data.subtype.register(clk, d=data, init=0, en=stb)
    stb = stb.subtype.register(clk, d=stb)

    return data, stb, gain, magnitude

if __name__ == "__main__" and "sim" in sys.argv:

    clk = Clock("clk")
    audio_in = Signed(16).input("magnitude")
    stb_in = Boolean().input("stb")

    audio_out, stb_out, gain, magnitude = audio_agc(clk, audio_in, stb_in)

    clk.initialise()

    for i in range(100):
        audio_in.set(100)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            print magnitude.get(), gain.get(), audio_out.get(), stb_out.get()
        audio_in.set(-100)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            print magnitude.get(), gain.get(), audio_out.get(), stb_out.get()
        audio_in.set(0)
        for i in range(100):
            stb_in.set(i==0)
            clk.tick()
            print magnitude.get(), gain.get(), audio_out.get(), stb_out.get()
        audio_in.set(-100)
        for i in range(0):
            stb_in.set(i==0)
            clk.tick()
            print magnitude.get(), gain.get(), audio_out.get(), stb_out.get()
