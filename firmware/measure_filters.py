#!/usr/bin/env python

def measure_filter(
    start_frequency = 4.0e6,
    stop_frequency = 32.0e6,
    step = 1.0e6):

    frequency = start_frequency
    frequencies = []
    while frequency <= stop_frequency:
        frequencies.append(frequency)
        frequency += step
    raw_input()
    powers = xcvr.scan(frequencies)
    return frequencies, np.array(powers)


import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr

xcvr = Xcvr("/dev/ttyUSB2")

xcvr.set_mode(2)
xcvr.set_squelch(0)
xcvr.set_gain(0)
xcvr.set_test_signal(1)

f0, p0 = measure_filter(0.5e6, 8e6, 0.125e6)
f1, p1 = measure_filter(1e6, 16e6, 0.25e6)
f2, p2 = measure_filter(2e6, 32e6, 0.5e6)
f3, p3 = measure_filter(4e6, 64e6, 1.0e6)

xcvr.set_test_signal(0)

plt.plot(f0, p0, 'b-', f1, p1, 'r-', f2, p2, 'g-', f3, p3, 'm-')
plt.xscale("log")
plt.yscale("log")
plt.show()


