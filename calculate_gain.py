from baremetal import *
from settings import Settings
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil, floor

def calculate_gain(clk, magnitude, setpoint):

    width = magnitude.subtype.bits
    t_data = magnitude.subtype
    setpoint_constant = t_data.constant(setpoint)

    count, last = counter(clk, 0, width-1, 1)
    first = (count==0)
    magnitude = t_data.register(clk, init=2**(width-2), en=last, d=magnitude)

    remainder = t_data.register(clk, init=0)
    gain      = t_data.register(clk, init=0)
    setpoint  = t_data.register(clk, init=0)

    shifter = remainder[width-2:0].cat(setpoint[width-2])
    difference = shifter - magnitude
    shifter_gt_magnitude = ~difference[width-1]

    next_remainder = t_data.select(shifter_gt_magnitude, shifter, difference)
    next_gain      = t_data.select(shifter_gt_magnitude, gain<<1, (gain<<1)|1)
    next_setpoint  = setpoint << 1

    next_remainder = t_data.select(first, next_remainder, 0)
    next_gain      = t_data.select(first, next_gain, 0)
    next_setpoint  = t_data.select(first, next_setpoint, setpoint_constant)

    remainder.d(next_remainder)
    gain.d(next_gain)
    setpoint.d(next_setpoint)

    gain = t_data.register(clk, init=0, en=first, d=gain)

    return gain

if __name__ == "__main__" and "sim" in sys.argv:

    clk = Clock("clk")
    magnitude = Signed(16).input("magnitude")

    gain = calculate_gain(clk, magnitude, 100)
    magnitude.set(5)

    clk.initialise()
    for i in range(50):
        clk.tick()
        print gain.get()
    magnitude.set(10)
    for i in range(50):
        clk.tick()
        print gain.get()
