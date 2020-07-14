from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from accumulator import accumulator
from dither import dither
from math import sin, cos, pi

def nco(clk, frequency, channels):
    bits = frequency.subtype.bits

    lo = accumulator(clk, frequency, channels)
    lo = [i.subtype.register(clk, d=i) for i in lo]
    lo = [i.subtype.register(clk, d=i) for i in lo]

    #add phase shift to I output
    pi_over_4 = (2**bits)/4
    lo_i = lo
    lo_q = [i - pi_over_4 for i in lo]

    #register outputs
    lo_i = [i.subtype.register(clk, d=i) for i in lo_i]
    lo_q = [i.subtype.register(clk, d=i) for i in lo_q]

    return lo_i, lo_q

