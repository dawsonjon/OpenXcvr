#!/usr/bin/env python

import sys
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr

xcvr = Xcvr("/dev/ttyUSB1")

xcvr.set_mode(2)
xcvr.set_squelch(0)
xcvr.set_gain(0)
xcvr.set_test_signal(1)

start_frequency = 1.0e6
stop_frequency = 30.0e6

frequencies = np.logspace(np.log10(start_frequency),np.log10(stop_frequency), 50)
powers = xcvr.scan(frequencies)
powers = np.array(powers)

xcvr.set_test_signal(0)

outf = open(sys.argv[1], "w")
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()
