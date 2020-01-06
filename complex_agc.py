from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain


def complex_agc(clk, i, q, stb, settings):

    #calculate magnitude and DC
    i_magnitude = measure_magnitude(clk, i, stb)
    q_magnitude = measure_magnitude(clk, i, stb)

    #rescale the data 
    i_gain = calculate_gain(clk, i_magnitude, 11000) #approx 2/3 full scale
    q_gain = calculate_gain(clk, q_magnitude, 11000)

    #squelch
    #mute = magnitude < settings.squelch
    #mute = mute.subtype.register(clk, d=mute)
    #audio = audio.subtype.select(mute, audio, 0)
    #audio = audio.subtype.register(clk, d=audio)
    #audio_stb = audio_stb.subtype.register(clk, d=audio_stb)

    #scale by 2**e
    i = i * i_gain
    q = q * q_gain

    return i, q, stb
