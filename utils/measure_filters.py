#!/usr/bin/env python

import sys
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr
import time

xcvr = Xcvr("/dev/ttyUSB0")

xcvr.set_mode(1)
xcvr.set_squelch(0)
xcvr.set_gain(0)
xcvr.set_test_signal(1)

start_frequency = 1.0e6
stop_frequency = 40.0e6

frequencies = np.logspace(np.log10(start_frequency),np.log10(stop_frequency), 100)



outf = open("baseline", "w")
xcvr.set_band(4)
time.sleep(1)
powers = xcvr.scan(frequencies)
powers = np.array(powers)
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()

outf = open("f_2_4", "w")
xcvr.set_band(3)
time.sleep(1)
powers = xcvr.scan(frequencies)
powers = np.array(powers)
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()

outf = open("f_4_8", "w")
xcvr.set_band(2)
time.sleep(1)
powers = xcvr.scan(frequencies)
powers = np.array(powers)
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()

outf = open("f_8_16", "w")
xcvr.set_band(1)
time.sleep(1)
powers = xcvr.scan(frequencies)
powers = np.array(powers)
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()

outf = open("f_16_30", "w")
xcvr.set_band(0)
time.sleep(1)
powers = xcvr.scan(frequencies)
powers = np.array(powers)
for frequency, power in zip(frequencies, powers):
    outf.write("%f %f\n"%(frequency, power))
outf.close()

xcvr.set_test_signal(0)
