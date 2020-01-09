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

    """
    The ADC has 24 bits, but to reduce the number of multipliers only
    keep 18 bits for the rest of the DSP processing. 18 bits still
    gives 108dB dynamic range

    """

    assert i.subtype.bits == 24
    assert q.subtype.bits == 24

    #calculate magnitude
    magnitude = measure_magnitude(clk, i, stb)

    #calculate gain
    setpoint = 0.67 * (2**23)
    gain = calculate_gain(clk, magnitude, setpoint)
    gain = gain.subtype.select(gain < 1, gain, 1)
    gain = gain.subtype.register(clk, d=gain, init=0, en=stb)

    #scale by 2**e

    #room for improvement here, could use one multiplier to calculate I
    #and Q in turn
    i = i * gain
    q = q * gain
    i = i.subtype.register(clk, d=i, init=0, en=stb)
    q = i.subtype.register(clk, d=q, init=0, en=stb)
    stb = stb.subtype.register(clk, d=stb)

    return i[23:6], q[23:6], stb
