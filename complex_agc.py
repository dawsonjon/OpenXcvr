from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain


def complex_agc(clk, i, q, stb, gain):

    """
    The ADC has 24 bits, but to reduce the number of multipliers only
    keep 18 bits for the rest of the DSP processing. 18 bits still
    gives 108dB dynamic range

    """

    assert i.subtype.bits == 24
    assert q.subtype.bits == 24

    maxval = (2**23)-1
    minval = -(2**23)

    i = i.resize(30)
    i <<= gain
    i = i.subtype.select(i > maxval, i, maxval)
    i = i.subtype.select(i < minval, i, minval)
    i = i[23:6]

    q = q.resize(30)
    q <<= gain
    q = q.subtype.select(q > maxval, q, maxval)
    q = q.subtype.select(q < minval, q, minval)
    q = q[23:6]

    i = i.subtype.register(clk, d=i, init=0, en=stb)
    q = q.subtype.register(clk, d=q, init=0, en=stb)
    stb = stb.subtype.register(clk, d=stb)

    return i, q, stb
