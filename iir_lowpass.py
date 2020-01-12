from baremetal import *
from math import log, pi, exp, floor, ceil
from matplotlib import pyplot as plt
import numpy as np
import sys
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain



def iir_lowpass(clk, audio, audio_stb, factor=4):

    sampling_frequency = 100.0e3
    actual_fc = -log(1-(2.0**-factor)) * sampling_frequency
    print actual_fc

    audio_bits = audio.subtype.bits

    #add extra bits for decay calculation
    long_audio = audio.resize(audio_bits+factor) << factor

    #implement IIR low pass filter
    output = long_audio.subtype.register(clk, init=0, en=audio_stb)
    output.d((long_audio >> factor) + (output - (output >> factor)))
    stb = Boolean().register(clk, d=audio_stb, init=0)

    #remove extra bits
    output = (output >> factor).resize(audio_bits)

    return output, stb

