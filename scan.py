#!/usr/bin/env python


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

start_frequency = 1.0e6
stop_frequency = 8.0e6
step = 0.25e6

frequency = start_frequency
frequencies = []
while frequency <= stop_frequency:
    frequencies.append(frequency)
    frequency += step

powers = xcvr.scan(frequencies)
powers = np.array(powers)

xcvr.set_test_signal(0)

plt.plot(frequencies, powers, 'b-')
plt.xscale("log")
plt.yscale("log")
plt.show()


