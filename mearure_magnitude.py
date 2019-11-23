from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil

def calculate_gain(clk, magnitude, lut_bits, lut_fraction_bits):

    """Calculate the required gain needed to give full scale signal
    given the magnitude of the signal.
    
    For efficiency the gain is split into two parts:
        e the number of bits to shift the signal right by.
        m a value to multiply the signal by.

    A lookup table is used to calculate m, the lookup table has
    2**lut_bits entries.
    The m output has lut_bits integer bits and lut_fraction_bits 
    fraction bits"""

    shift_bits = magnitude.subtype.bits - lut_bits
    m_type = magnitude.subtype
    e_type = Unsigned(int(ceil(log(shift_bits+1, 2))))

    count, last_count = counter(clk, 0, shift_bits, 1)
    m = m_type.register(clk)
    e = e_type.register(clk)
    msb_high = m[m_type.bits-1]
    m.d(m_type.select(last_count, m_type.select(msb_high, m<<1, m), magnitude))
    e.d(e_type.select(last_count, e_type.select(msb_high, e+1, e), 0))

    m = m_type.register(clk, d=m[m_type.bits-1:m_type.bits-(lut_bits)], en=last_count)
    e = e_type.register(clk, d=e, en=last_count)

    lut_depth = 2**lut_bits
    scaling_factor = lut_depth*(2**lut_fraction_bits)
    lookup_table = [scaling_factor-1] + [(scaling_factor-1)/i for i in range(1, lut_depth)]
    m = Unsigned(lut_bits+lut_fraction_bits).rom(m, *lookup_table)

    return m, e

#make filter
clk = Clock("clk")
data_in = Unsigned(8).input("data_in")
m, e = calculate_gain(clk, data_in, 4, 8)

if "sim" in sys.argv:

    #simulate
    clk.initialise()

    for data in stimulus:
        data_in.set(data)
        clk.tick()
        print(m.get(), e.get())
