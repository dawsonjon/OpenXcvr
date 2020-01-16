#!/usr/bin/env python


import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr

xcvr = Xcvr("/dev/ttyUSB1")

xcvr.set_mode(1)
xcvr.set_squelch(0)
xcvr.set_gain(4)

start_frequency = 0.1e6
stop_frequency = 2.0e6
step = 0.005e6

frequency = start_frequency
frequencies = []
while frequency <= stop_frequency:
    frequencies.append(frequency)
    frequency += step

powers = xcvr.scan(frequencies)

plt.plot(frequencies, powers, 'b-')
plt.show()


