from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil


def measure_magnitude(clk, data_in, stb_in, leakage_in):

    #sign extend input by 4 bits
    extra_bits = 17
    input_bits = data_in.subtype.bits
    data_in = data_in.resize(input_bits + extra_bits) << extra_bits
    
    #capture largest and smallest values
    t_data = data_in.subtype
    maxval = t_data.register(clk, init=0, en=stb_in)
    minval = t_data.register(clk, init=0, en=stb_in)
    leakage = t_data.register(clk, init=0)

    maxval.d(t_data.select(data_in > maxval, maxval-leakage, data_in))
    minval.d(t_data.select(data_in < minval, minval+leakage, data_in))

    #calculate dc
    dc = (maxval + minval) >> extra_bits + 1
    dc = dc.resize(input_bits-1)

    #calculate magnitude
    magnitude = (maxval - minval) >> 1
    leakage.d(magnitude >> leakage_in) #scale leakage
    magnitude = magnitude >> extra_bits
    magnitude = magnitude.resize(input_bits-1)

    return magnitude, dc

#make filter
clk = Clock("clk")
data_in = Signed(9).input("data_in")
stb_in = Boolean().input("data_in")
leakage = Signed(6).input("leakage")
magnitude, dc = measure_magnitude(clk, data_in, stb_in, leakage)

stimulus = [100, -60, 100, -60] + [0 for i in range(200000)]


if "sim" in sys.argv:

    #simulate
    clk.initialise()
    stb_in.set(1)
    leakage.set(17)

    i = 0
    for data in stimulus:
        data_in.set(data)
        clk.tick()
        print(i, magnitude.get(), dc.get())
        if magnitude.get() < 40:
            break
        i+=1
