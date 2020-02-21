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

class Xcvr:

    def __init__(self, device="/dev/ttyUSB0"):
        self.port = serial.Serial(device, 500000, timeout=2)
        self.port.flush()

    def get_data_value(self, line):
        value = int(line, 16)
        if value & 0x8000:
            value |= (~0xffff)
        return value

    def capture(self):
        self.port.flush()
        self.port.write("c\n")
        lines = []
        for i in range(1000):
            lines.append((self.port.readline(), self.port.readline()))
        i_values = []
        q_values = []
        for a, b in lines:
            i_values.append(float(self.get_data_value(a)))
            q_values.append(float(self.get_data_value(b)))
        return i_values, q_values

    def set_frequency(self, frequency):
        self.port.write("f%u\n"%int(frequency))
        self.port.readline()
        self.port.readline()

    def set_test_signal(self, state):
        self.port.write("T%u\n"%state)
        self.port.readline()
        self.port.readline()

    def set_mode(self, mode):
        self.port.write("m%u\n"%mode)
        self.port.readline()

    def set_gain(self, gain):
        self.port.write("g%u\n"%gain)
        self.port.readline()

    def get_power(self):
        self.port.write("p\n")
        value = self.port.readline()
        value = int(value, 16)
        return value

    def scan(self, frequencies):
        self.port.flush()
        #send frequencies
        command = ""
        values = []
        for frequency in frequencies:
            self.set_frequency(frequency)
            i, q = self.capture()
            value = np.array(i)+1.0j*np.array(q)
            value = sum(abs(value))
            values.append(value)
            print frequency, value
        return values

    def set_squelch(self, squelch):
        self.port.write("q%u\n"%squelch)
        self.port.readline()

    def __del__(self):
        self.port.close()
