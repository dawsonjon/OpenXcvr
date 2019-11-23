from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain


def audio_agc(clk, audio, leakage, lut_bits, fraction_bits):

    #calculate magnitude and DC
    magnitude, dc = measure_magnitude(clk, audio, leakage)

    #remove DC
    audio = audio - dc
    audio = audio.subtype.register(clk, d=audio)

    #rescale the data 
    gain_m, gain_e = calculate_gain(clk, magnitude, lut_bits, fraction_bits)

    #scale by 2**e
    audio = audio << gain_e
    audio = audio.subtype.register(clk, d=audio)

    #scale by m
    input_bits = data_in.subtype.bits
    audio = audio.resize(input_bits + lut_bits + fraction_bits)
    audio = audio * gain_m
    audio >>= fraction_bits
    audio = audio.resize(input_bits)
    audio = audio.subtype.register(clk, d=audio)

    return audio

#make filter
clk = Clock("clk")
data_in = Signed(8).input("data_in")
leakage = Signed(8).input("leakage")
magnitude, dc = measure_magnitude(clk, data_in, leakage)

stimulus = [20, -20, 20, -20, 0, 0, 0, 0, 0, 0, 0, 0]


if "sim" in sys.argv:

    #simulate
    clk.initialise()
    leakage.set(16)

    for data in stimulus:
        data_in.set(data)
        clk.tick()
        print(magnitude.get(), dc.get(), maxval.get(), minval.get())
