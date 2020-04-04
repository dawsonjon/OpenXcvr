#!/usr/bin/env python

import sys
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr

xcvr = Xcvr("/dev/ttyUSB0")

parameters = []
for parameter in sys.argv[1:-1]:
    if "=" in parameter:
        key, value = parameter.split("=")
        parameters.append((key, value))

parameters = dict(parameters)

xcvr.set_mode(int(parameters.get("m", 1)))
xcvr.set_gain(int(parameters.get("g", 0)))

start_frequency = 7.0e6
stop_frequency = 7.3e6

#frequencies = np.logspace(np.log10(start_frequency),np.log10(stop_frequency), 1000)
frequencies = np.linspace(start_frequency,stop_frequency, 300)
powers = xcvr.scan(frequencies)
powers = np.array(powers)


outf = open(sys.argv[-1], "w")
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()
