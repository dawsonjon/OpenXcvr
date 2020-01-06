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
    if value & 0x8000:
        value |= (~0xffff)
    return value

def capture():
    port.flush()
    port.write("c\n")
    i_values = []
    q_values = []
    for i in range(1000):
        i_values.append(float(get_data_value()))
        q_values.append(float(get_data_value()))
    return i_values, q_values

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

set_frequency(1.2151e6-7e3)
set_mode(1)
i_values, q_values = capture()
values = np.array(i_values)+1.0j*np.array(q_values)
plt.plot(range(len(i_values)), i_values, range(len(q_values)), q_values)
plt.show()

values = np.array(values)*np.hamming(len(values))
spectrum = 20*np.log10(abs(np.fft.fftshift(np.fft.fft(values))))
frequency_range = np.linspace(-18.311e3*2, 18.311e3*2,  len(spectrum))
plt.plot(frequency_range, spectrum)
#plt.xlim(-50e3, 50e3)
plt.show()

port.close()

