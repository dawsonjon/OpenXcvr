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
import logging
import struct

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
    "AM": 0,
    "NFM": 1,
    "FM": 2,
    "LSB": 3,
    "USB": 4,
    "CW": 5,
}
rmodes = {v: k for k, v in modes.items()}
agc_speeds = {"FAST": 0, "NORMAL": 1, "SLOW": 2, "VERY_SLOW": 3}
steps = {
    "10Hz": 0,
    "50Hz": 1,
    "100Hz": 2,
    "1kHz": 3,
    "5kHz": 4,
    "10kHz": 5,
    "12.5kHz": 6,
    "25kHz": 7,
    "50kHz": 8,
    "100kHz": 9,
}


def checksum(string):
    checksum = 0
    for c in string:
        checksum += int(c)
        checksum &= 0xFF
    return string + bytes([checksum])


class CommandFailed(Exception):
    pass


class BadCatResponse(Exception):
    pass

class InvalidMode(Exception):
    pass

class Xcvr:
    def __init__(self, device="/dev/ttyUSB0"):
        self.audio_sent_times = []
        self.port = serial.Serial(device, 1000000, timeout=1, rtscts=True)
        self.reset_cat()
        self.data_buffer = b""

    def reset_cat(self):
        logging.info("openxcvr: resetting cat interface")

        #if we were previously in the middle of a block, finish it off
        self.port.write(b"\x00" * 4000)

        # Read out anything that might be left in the receive buffer.
        # keep issuing a command until we get a positive acknowledgement
        # This might happen by chance, so look for a few positive acknowledgements in a row
        acks_seen = 0
        for i in range(100):  # give up after this many failed attempts
            self.send_command_message(checksum(b"s" + address_idx["tx"] + b"\x00\x00\x00\x00"))
            acknowledgement = self.port.read(3)
            logging.info("openxcvr: ack=%s", acknowledgement)
            if acknowledgement == b"U\x01K":
                acks_seen += 1
                if acks_seen == 10:
                    return
            else:
                acks_seen = 0
        raise BadCatResponse

    def get_status_message(self):
        header = self.port.read(1)
        length = self.port.read(1)[0]
        payload = self.port.read(length)
        return payload

    def send_command_message(self, message):
        assert len(message) < 256
        self.port.write(b"\x55"+bytes([len(message)])+message)

    def get_acknowledgement(self):
        if self.get_status_message() != b"K":
            raise CommandFailed

    def change_setting(self, setting, value):
        value = int(value)
        value_string = bytes(
            [
                value & 0xFF,
                value >> 8 & 0xFF,
                value >> 16 & 0xFF,
                value >> 24 & 0xFF,
            ]
        )
        self.send_command_message(checksum(b"s" + setting + value_string))
        self.get_acknowledgement()

    def request_setting(self, setting):
        self.send_command_message(b"g" + setting)

    def get_setting(self):
        settings = self.get_status_message()
        settings = struct.unpack("<i", settings)[0]
        return settings

    def capture(self):
        self.port.send_command_message(b"c")
        buf = self.port.read(2048 * 4)
        values = np.frombuffer(buf, dtype="int16")
        i_values = values[::2]
        q_values = values[1::2]
        return i_values, q_values

    def request_audio_output(self):
        self.send_command_message(b"O")

    def get_audio(self):
        buf = self.port.read(2049)
        return buf[1:]

    def put_audio(self, data):
        assert len(data) == 1024
        self.port.write(b"\xAA"+data)

    def wait_audio_in_ack(self):
        self.get_acknowledgement()

    def store_memory(self, location, data):
        assert len(data) == 64
        assert location >= 1 <= 499
        self.send_command_message(b"S"+bytes([location>>8, location & 0xff])+data)

    def set_frequency(self, frequency):
        logging.info("openxcvr: setting cat frequency %s", frequency)
        self.change_setting(address_idx["frequency"], frequency)

    def request_frequency(self):
        logging.info("openxcvr: getting cat frequency")
        self.request_setting(address_idx["frequency"])

    def get_frequency(self):
        value = self.get_setting()
        logging.info("openxcvr: got %s", value)
        return value

    def set_min_frequency(self, frequency):
        self.change_setting(address_idx["min_frequency"], frequency)

    def set_max_frequency(self, frequency):
        self.change_setting(address_idx["max_frequency"], frequency)

    def set_squelch(self, squelch):
        self.change_setting(address_idx["squelch"], squelch)

    def set_test_signal(self, state):
        self.change_setting(address_idx["test_signal"], state)

    def set_TX(self, state):
        self.change_setting(address_idx["tx"], state)

    def request_TX(self):
        logging.info("openxcvr: getting cat tx_rx")
        self.request_setting(address_idx["tx"])

    def get_TX(self):
        logging.info("openxcvr: getting cat tx_rx")
        tx_rx = self.get_setting()
        logging.info("openxcvr: got %s", tx_rx)
        return tx_rx

    def set_mode(self, mode):
        logging.info("openxcvr: setting cat mode %s", mode)
        try:
            self.change_setting(address_idx["mode"], modes[mode])
        except KeyError:
            raise InvalidMode

    def request_mode(self):
        logging.info("openxcvr: getting cat mode")
        self.request_setting(address_idx["mode"])

    def get_mode(self):
        mode = self.get_setting()
        logging.info("openxcvr: got %s", mode)
        return rmodes[mode]

    def set_force_band(self, state):
        self.change_setting(address_idx["band"], state)

    def set_AGC(self, state):
        self.change_setting(address_idx["agc_speed"], agc_speeds[state.upper()])

    def set_step(self, state):
        self.change_setting(address_idx["step"], steps[state])

    def set_volume(self, state):
        self.change_setting(address_idx["volume"], state)

    def set_mic_gain(self, state):
        self.change_setting(address_idx["mic_gain"], state)

    def set_cw_speed(self, state):
        self.change_setting(address_idx["cw_speed"], state)

    def set_USB_audio(self, state):
        self.change_setting(address_idx["USB_audio"], state)

    # def get_ADC(self):
    # self.port.write("a\n")
    # channels = {}
    # for i in range(10):
    # data = self.port.readline()
    # channel = int(data[0:4], 16)
    # value = int(data[4:8], 16)
    # channels[channel] = 3.3*value/4096.0
    # return channels

    # def get_batt_voltage(self):
    # channels = self.get_ADC()
    # return channels[5] * (11.5/1.5)

    # def get_fwd_power(self):
    # channels = self.get_ADC()
    # rms_voltage = (channels[1]+0.401) * 10.0 * (1/np.sqrt(2.0))
    # power = rms_voltage * rms_voltage / 50.0
    # return power
    #
    # def get_rev_power(self):
    # channels = self.get_ADC()
    # rms_voltage = (channels[3]+0.401) * 10.0 * (1/np.sqrt(2.0))
    # power = rms_voltage * rms_voltage / 50.0
    # return power

    # def get_power(self):
    # self.port.write("p\n")
    # value = self.port.readline()
    # value = int(value, 16)
    # return value

    # def scan(self, frequencies):
    # self.port.flush()
    ##send frequencies
    # command = ""
    # values = []
    # for frequency in frequencies:
    # self.set_frequency(frequency)
    # i, q = self.capture()
    # value = np.array(i)+1.0j*np.array(q)
    # value = sum(abs(value))
    # values.append(value)
    # print frequency, value
    # return values

    def __del__(self):
        self.port.close()
