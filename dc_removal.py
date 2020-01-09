from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain


def dc_removal(clk, audio, audio_stb, factor=7):

    factor = 7 #higher number == slower decay
    audio_bits = audio.subtype.bits

    #add extra bits for decay calculation
    long_audio = audio.resize(audio_bits+factor) << factor

    #implement IIR low pass filter
    dc = long_audio.subtype.register(clk, init=0, en=audio_stb)
    dc.d((long_audio >> factor) + (dc - (dc >> factor)))

    #remove extra bits
    dc = (dc >> factor).resize(audio_bits)

    audio = audio - dc

    return audio, audio_stb
