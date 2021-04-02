#!/usr/bin/env python3


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

address_idx = {
"frequency": b"\x00",
"mode": b"\x01",
"agc_speed": b"\x02",
"step": b"\x03",
"squelch": b"\x04",
"volume": b"\x05",
"max_frequency": b"\x06",
"min_frequency": b"\x07",
"mic_gain": b"\x08",
"cw_speed": b"\x09",
"pps_count": b"\x0a",
"band": b"\x0b",
"test_signal": b"\x0c",
"USB_audio": b"\x0d",
"tx": b"\x0e",
"mute": b"\x0f",
}
modes = {
"AM": b"\x00",
"NFM":b"\x01",
"FM": b"\x02",
"LSB":b"\x03",
"USB":b"\x04",
"CW":b"\x05",
"PKTLSB":b"\x03",
"PKTUSB":b"\x04",
}
agc_speeds = {
"FAST": b"\x00",
"NORMAL":b"\x01",
"SLOW": b"\x02",
"VERY SLOW":b"\x03"
}
steps = {
"10Hz":b"\x00",
"50Hz": b"\x01",
"100Hz": b"\x02",
"1kHz":b"\x03",
"5kHz":b"\x04",
"10kHz":b"\x05",
"12.5kHz":b"\x06",
"25kHz":b"\x07",
"50kHz":b"\x08",
"100kHz":b"\x09",
}

def checksum(string):
    checksum = 0
    for c in string:
        checksum += int(c)
        checksum &= 0xff
    return string+bytes([checksum])

class CommandFailed(Exception):
    pass

class BadCatResponse(Exception):
    pass

class Xcvr:

    def __init__(self, device="/dev/ttyUSB0"):
        self.port = serial.Serial(device, 2000000, timeout=2, rtscts=True)
        self.reset_cat()

    def reset_cat(self):
        print("cat interface reset", file=sys.stderr)
        #read out anything that might be left in the receive buffer.
        self.port.read(5000)
        #keep issuing a command until we get a positive acknowledgement
        #This might happen by chance, so look for a few positive acknowledgements in a row
        acks_seen = 0
        for i in range(10000): #give up after this many failed attempts
            self.port.write(checksum(b"s"+address_idx["tx"]+b"\x00\x00\x00\x00"))
            acknowledgement = self.port.read(1)
            print(acknowledgement, file=sys.stderr)
            if acknowledgement == b"K":
                acks_seen += 1
                if acks_seen == 10:
                    return
            else:
                acks_seen = 0
        self.port.flushInput()
        self.port.flushOutput()
        raise BadCatResponse


    def capture(self):
        self.port.write(b"c")
        buf = self.port.read(2048 * 4)
        values = np.frombuffer(buf, dtype="int16")
        i_values = values[::2]
        q_values = values[1::2]
        return i_values, q_values

    def request_audio_output(self):
        self.port.write(b"O")

    def get_audio(self):
        buf = self.port.read(2048)
        return buf

    def put_audio(self, data):
        if len(data) < 1024:
            return
        self.port.write(b"I")
        self.port.write(data[:1024])

    def store_memory(self, location, data):
        assert len(data) == 64
        assert location >= 1 <= 499
        self.port.write("S")
        self.port.write(chr(location>>8))
        self.port.write(chr(location&0xff))
        self.port.write(data)
        print(self.port.read(1))

    def set_frequency(self, frequency):
        print("setting cat frequency", frequency)
        frequency = int(frequency)
        frequency_string = bytes([
                frequency & 0xff,
                frequency >> 8  & 0xff,
                frequency >> 16 & 0xff,
                frequency >> 24 & 0xff,
        ])
        self.port.write(checksum(b"s"+address_idx["frequency"]+frequency_string))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_min_frequency(self, frequency):
        frequency = int(frequency)
        frequency_string = bytes([
                frequency & 0xff,
                frequency >> 8  & 0xff,
                frequency >> 16 & 0xff,
                frequency >> 24 & 0xff,
        ])
        self.port.write(checksum(b"s"+address_idx["min_frequency"]+frequency_string))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_max_frequency(self, frequency):
        frequency = int(frequency)
        frequency_string = bytes([
                frequency & 0xff,
                frequency >> 8  & 0xff,
                frequency >> 16 & 0xff,
                frequency >> 24 & 0xff,
        ])
        self.port.write(checksum(b"s"+address_idx["max_frequency"]+frequency_string))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_squelch(self, squelch):
        self.port.write(checksum(b"s"+address_idx["squelch"]+bytes([squelch])+b"\x00\x00\x00"))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_test_signal(self, state):
        self.port.write(checksum("s"+address_idx["test_signal"]+chr(state)+"\x00\x00\x00"))
        if self.port.read(1) != "K":
            raise CommandFailed

    def set_TX(self, state):
        print("setting cat TX", state)
        self.port.write(checksum(b"s"+address_idx["tx"]+bytes([state])+b"\x00\x00\x00"))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_mode(self, mode):
        print("setting cat mode", mode)
        self.port.write(checksum(b"s"+address_idx["mode"]+modes[mode]+b"\x00\x00\x00"))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_force_band(self, state):
        self.port.write(checksum("s"+address_idx["band"]+chr(state)+"\x00\x00\x00"))
        if self.port.read(1) != "K":
            raise CommandFailed

    def set_AGC(self, state):
        self.port.write(checksum("s"+address_idx["agc_speed"]+chr(state)+"\x00\x00\x00"))
        if self.port.read(1) != "K":
            raise CommandFailed

    def set_step(self, state):
        self.port.write(checksum("s"+address_idx["step"]+chr(steps[state])+"\x00\x00\x00"))
        if self.port.read(1) != "K":
            raise CommandFailed

    def set_volume(self, state):
        self.port.write(checksum(b"s"+address_idx["volume"]+bytes([state])+b"\x00\x00\x00"))
        if self.port.read(1) != b"K":
            raise CommandFailed

    def set_mic_gain(self, state):
        self.port.write(checksum("s"+address_idx["mic_gain"]+chr(steps[state])+"\x00\x00\x00"))
        if self.port.read(1) != "K":
            raise CommandFailed

    def set_cw_speed(self, state):
        self.port.write(checksum("s"+address_idx["cw_speed"]+chr(state)+"\x00\x00\x00"))
        if self.port.read(1) != "K":
            raise CommandFailed

    def set_USB_audio(self, state):
        self.port.write(checksum(b"s"+address_idx["USB_audio"]+bytes([state])+b"\x00\x00\x00"))
        if self.port.read(1) != b"K":
            raise CommandFailed

    #def get_ADC(self):
        #self.port.write("a\n")
        #channels = {}
        #for i in range(10):
            #data = self.port.readline()
            #channel = int(data[0:4], 16)
            #value = int(data[4:8], 16)
            #channels[channel] = 3.3*value/4096.0
        #return channels

    #def get_batt_voltage(self):
        #channels = self.get_ADC()
        #return channels[5] * (11.5/1.5)

    #def get_fwd_power(self):
        #channels = self.get_ADC()
        #rms_voltage = (channels[1]+0.401) * 10.0 * (1/np.sqrt(2.0))
        #power = rms_voltage * rms_voltage / 50.0
        #return power
#
    #def get_rev_power(self):
        #channels = self.get_ADC()
        #rms_voltage = (channels[3]+0.401) * 10.0 * (1/np.sqrt(2.0))
        #power = rms_voltage * rms_voltage / 50.0
        #return power



    #def get_power(self):
        #self.port.write("p\n")
        #value = self.port.readline()
        #value = int(value, 16)
        #return value

    #def scan(self, frequencies):
        #self.port.flush()
        ##send frequencies
        #command = ""
        #values = []
        #for frequency in frequencies:
            #self.set_frequency(frequency)
            #i, q = self.capture()
            #value = np.array(i)+1.0j*np.array(q)
            #value = sum(abs(value))
            #values.append(value)
            #print frequency, value
        #return values


    def __del__(self):
        self.port.close()
