#!/usr/bin/env python

import serial
import struct
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr

xcvr = Xcvr("/dev/ttyUSB0")

xcvr.set_frequency(1.053e6)
xcvr.set_mode(0)
#xcvr.set_band(2)
#xcvr.set_squelch(0)
#xcvr.set_test_signal(1)

i_values, q_values = xcvr.capture()
i_values, q_values = xcvr.capture()
values = np.array(i_values)+1.0j*np.array(q_values)
plt.plot(range(len(i_values)), i_values, range(len(q_values)), q_values)
plt.show()

#values = np.array(values)*np.hamming(len(values))
spectrum = 20*np.log10(abs(np.fft.fftshift(np.fft.fft(values))))
frequency_range = np.linspace(-0.5, 0.5,  len(spectrum))
plt.plot(frequency_range, spectrum)
plt.xlim(-0.5, 0.5)
plt.show()
