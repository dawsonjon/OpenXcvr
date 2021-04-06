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

start_frequency = 3.0e6
stop_frequency = 30.0e6
frequencies = np.logspace(np.log10(start_frequency),np.log10(stop_frequency), 50)

for frequency in frequencies:
    xcvr.set_frequency(frequency)
    total = 0
    for i in range(5):
        total += xcvr.get_fwd_power()
    power = total/5
    print frequency, power
