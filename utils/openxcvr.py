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

modes = {
"AM": "\x00",
"NFM":"\x01",
"FM": "\x02",
"LSB":"\x03",
"USB":"\x04",
"CW":"\x05",
}
agc_speeds = {
"FAST": "\x00",
"NORMAL":"\x01",
"SLOW": "\x02",
"VERY SLOW":"\x03"
}
steps = {
"10Hz":"\x00",
"50Hz": "\x01",
"100Hz": "\x02",
"1kHz":"\x03",
"5kHz":"\x04",
"10kHz":"\x05",
"12.5kHz":"\x06",
"25kHz":"\x07",
"50kHz":"\x08",
"100kHz":"\x09",
}

class Xcvr:

    def __init__(self, device="/dev/ttyUSB0"):
        self.port = serial.Serial(device, 2000000, timeout=2, rtscts=True)
        self.port.flush()

    def capture(self):
        self.port.flush()
        self.port.write("c\n")
        buf = self.port.read(16000)
        values = np.frombuffer(buf, dtype="int16")
        i_values = values[::2]
        q_values = values[1::2]
        return i_values, q_values

    def get_audio(self):
        self.port.flush()
        self.port.write("O\n")
        buf = self.port.read(1000)
        return buf

    def put_audio(self, data):
        if len(data) < 1000:
            return
        self.port.write("I")
        self.port.write(data[:1000])

    def store_memory(self, location, data):
        assert len(data) == 64
        assert location >= 1 <= 499
        self.port.write("S")
        self.port.write(chr(location>>8))
        self.port.write(chr(location&0xff))
        self.port.write(data)
        print self.port.read(1)

    def set_frequency(self, frequency):
        self.port.write("f%u\n"%int(frequency))

    def set_squelch(self, squelch):
        self.port.write("q%u\n"%squelch)

    def set_test_signal(self, state):
        self.port.write("T%u\n"%state)

    def set_TX(self, state):
        self.port.write("t%u\n"%state)

    def set_mode(self, mode):
        self.port.write("m%u\n"%mode)

    def set_gain(self, gain):
        self.port.write("g%u\n"%gain)

    def set_band(self, band):
        self.port.write("b%d\n"%(band|8))

    def set_AGC(self, gain):
        self.port.write("A%u\n"%gain)

    def get_ADC(self):
        self.port.write("a\n")
        channels = {}
        for i in range(10):
            data = self.port.readline()
            channel = int(data[0:4], 16)
            value = int(data[4:8], 16)
            channels[channel] = 3.3*value/4096.0
        return channels

    def get_batt_voltage(self):
        channels = self.get_ADC()
        return channels[5] * (11.5/1.5)

    def get_fwd_power(self):
        channels = self.get_ADC()
        rms_voltage = (channels[1]+0.401) * 10.0 * (1/np.sqrt(2.0))
        power = rms_voltage * rms_voltage / 50.0
        return power

    def get_rev_power(self):
        channels = self.get_ADC()
        rms_voltage = (channels[3]+0.401) * 10.0 * (1/np.sqrt(2.0))
        power = rms_voltage * rms_voltage / 50.0
        return power


    def set_USB_audio(self, gain):
        value = self.port.readline()
        value = int(value, 16)
        return value

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


    def __del__(self):
        self.port.close()
