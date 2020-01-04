#!/usr/bin/env python

import serial
import struct
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
import time
import sys
import threading

def get_data_value():
    value = port.readline()
    value = int(value, 16)
    if value > 0xffff:
        value |= (~0xffff)
    return value

def capture():
    port.flush()
    port.write("c\n")
    values = []
    for i in range(1000):
        values.append(float(get_data_value()))
    return values

def set_frequency(frequency):
    port.flush()
    port.write("f%u\n"%frequency)
    print "f%u\n"%frequency
    print port.readline()
    print port.readline()

def set_mode(mode):
    port.flush()
    port.write("m%u\n"%mode)
    print port.readline()
    print port.readline()

device = "/dev/ttyUSB2"
port = serial.Serial(device, 115200, timeout=2)

set_frequency(1.215e6)
set_mode(0)
values = capture()
plt.plot(values)
plt.show()

values = np.array(values)*np.hamming(len(values))
spectrum = abs(np.fft.fftshift(np.fft.fft(values)))
frequency_range = np.linspace(-50e3, 50e3,  len(spectrum))
plt.plot(frequency_range, spectrum)
#plt.xlim(-50e3, 50e3)
plt.show()

port.close()

