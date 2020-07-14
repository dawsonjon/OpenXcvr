#!/usr/bin/env python

import serial
import struct
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr, modes, agc_speeds, steps
import sys
from readchar import readkey

xcvr = Xcvr("/dev/ttyUSB0")

def program(page, name, frequency, min_frequency, max_frequency, mode, agc_speed, step, squelch):
    assert len(name) == 16

    #split frequency into bytes
    f =  chr(frequency  & 0xff)
    f += chr(frequency >> 8 & 0xff)
    f += chr(frequency >> 16 & 0xff)
    f += chr(frequency >> 24 & 0xff)

    f_min =  chr(min_frequency  & 0xff)
    f_min += chr(min_frequency >> 8 & 0xff)
    f_min += chr(min_frequency >> 16 & 0xff)
    f_min += chr(min_frequency >> 24 & 0xff)

    f_max =  chr(max_frequency  & 0xff)
    f_max += chr(max_frequency >> 8 & 0xff)
    f_max += chr(max_frequency >> 16 & 0xff)
    f_max += chr(max_frequency >> 24 & 0xff)

    data = (
    f+
    modes[mode]+"\x00\x00\x00"+
    agc_speeds[agc_speed]+"\x00\x00\x00"+
    steps[step]+"\x00\x00\x00"+
    chr(squelch)+"\x00\x00\x00"+
    "\x00\x00\x00\x00"+
    f_max+
    f_min+
    "\x00\x00\x00\x00"+
    "\x00\x00\x00\x00"+
    "\x00\x00\x00\x00"+
    name +
    "\x00\x00\x00\x00") #indicate in use
    xcvr.store_memory(page, data)

program(1,  "MW Broadcast    ", 1215000,  531000,   1602000,  "AM", "VERY SLOW", "1kHz", 0)
program(2,  "LW Broadcast    ", 198000,   153000,   279000,   "AM", "VERY SLOW", "1kHz", 0)
program(3,  "20m SSB         ", 14101000, 14101000, 14350000, "USB", "SLOW", "100Hz", 0)
program(4,  "40m SSB         ", 7060000,  7060000,  7200000,  "LSB", "SLOW", "100Hz", 0)
program(5,  "80m SSB         ", 3620000,  3620000,  3800000,  "LSB", "SLOW", "100Hz", 0)
program(6,  "160m SSB        ", 1843000,  1843000,  2000000,  "LSB", "SLOW", "100Hz", 0)
program(7,  "20m CW          ", 14000000, 14000000, 14099000, "CW", "SLOW", "10Hz", 0)
program(8,  "40m CW          ", 7000000,  7000000,  7060000,  "CW", "SLOW", "10Hz", 0)
program(9,  "80m CW          ", 3500000,  3500000,  3620000,  "CW", "SLOW", "10Hz", 0)
program(10, "160m CW         ", 1810000,  1810000,  1843000,  "CW", "SLOW", "10Hz", 0)
program(11, "SHORTWAVE 120m  ", 2300000,  2300000,  2495000,  "AM", "VERY SLOW", "1kHz", 0)
program(12, "SHORTWAVE  90m  ", 3200000,  3200000,  3400000,  "AM", "VERY SLOW", "1kHz", 0)
program(13, "SHORTWAVE  75m  ", 3900000,  3900000,  4000000,  "AM", "VERY SLOW", "1kHz", 0)
program(14, "SHORTWAVE  60m  ", 4750000,  4750000,  4995000,  "AM", "VERY SLOW", "1kHz", 0)
program(15, "SHORTWAVE  49m  ", 5900000,  5900000,  6200000,  "AM", "VERY SLOW", "1kHz", 0)
program(16, "SHORTWAVE  41m  ", 7200000,  7200000,  7450000,  "AM", "VERY SLOW", "1kHz", 0)
program(17, "SHORTWAVE  31m  ", 9400000,  9400000,  9900000,  "AM", "VERY SLOW", "1kHz", 0)
program(18, "SHORTWAVE  25m  ", 11600000, 11600000, 12100000, "AM", "VERY SLOW", "1kHz", 0)
program(19, "SHORTWAVE  22m  ", 13570000, 13570000, 13870000, "AM", "VERY SLOW", "1kHz", 0)
program(20, "SHORTWAVE  19m  ", 15100000, 15100000, 15800000, "AM", "VERY SLOW", "1kHz", 0)
program(21, "SHORTWAVE  16m  ", 17480000, 17480000, 17900000, "AM", "VERY SLOW", "1kHz", 0)
program(22, "SHORTWAVE  15m  ", 18900000, 18900000, 19020000, "AM", "VERY SLOW", "1kHz", 0)
program(23, "SHORTWAVE  13m  ", 21450000, 21450000, 21850000, "AM", "VERY SLOW", "1kHz", 0)
program(24, "SHORTWAVE  11m  ", 25670000, 25670000, 26100000, "AM", "VERY SLOW", "1kHz", 0)
program(30, "SHANNON VOLMET  ", 5505000,  5505000,  5505000,  "USB", "SLOW", "10Hz", 0)
program(40, "20m PSK         ", 14070000, 14000000, 14099000, "USB", "SLOW", "100Hz", 0)
program(41, "40m PSK         ", 7040000,  7000000,  7060000,  "USB", "SLOW", "100Hz", 0)
program(42, "80m PSK         ", 3580000,  3500000,  3620000,  "USB", "SLOW", "100Hz", 0)
program(43, "160m PSK        ",  1830000,  1810000,  1843000,  "USB", "SLOW", "100Hz", 0)
program(50, "20m FT8         ", 14074000, 14000000, 14099000, "USB", "SLOW", "100Hz", 0)
program(51, "40m FT8         ", 7074000,  7000000,  7060000,  "USB", "SLOW", "100Hz", 0)
program(52, "80m FT8         ", 3573000,  3500000,  3620000,  "USB", "SLOW", "100Hz", 0)
program(53, "160m FT8        ",  1840000,  1810000,  1843000,  "USB", "SLOW", "100Hz", 0)
program(60, "20m RTTY        ", 14083000, 14000000, 14099000, "LSB", "SLOW", "100Hz", 0)
program(61, "40m RTTY        ", 7043000,  7000000,  7060000,  "LSB", "SLOW", "100Hz", 0)
program(62, "80m RTTY        ", 3590000,  3500000,  3620000,  "LSB", "SLOW", "100Hz", 0)
program(70,  "BBC RADIO 5 Live", 693000,  531000,   1602000,  "AM", "VERY SLOW", "1kHz", 0)
program(71,  "BBC Her and worc", 738000,  531000,   1602000,  "AM", "VERY SLOW", "1kHz", 0)
program(72,  "855 Sunshine    ", 855000,  531000,   1602000,  "AM", "VERY SLOW", "1kHz", 0)
program(73,  "Talk Sport      ",1053000,  531000,   1602000,  "AM", "VERY SLOW", "1kHz", 0)
program(74,  "Absolute        ",1215000,  531000,   1602000,  "AM", "VERY SLOW", "1kHz", 0)
program(75,  "BBC Radio 4     ", 198000,   153000,   279000,   "AM", "VERY SLOW", "1kHz", 0)
program(75,  "RTE Radio 1     ", 252000,   153000,   279000,   "AM", "VERY SLOW", "1kHz", 0)

cb_start = 27601250
cb_stop = 27991250
cb_step = 10000
for channel in range(40):
    program(channel+100+1,"CB UK %2u        "%(channel+1), cb_start+(cb_step*channel),  cb_start,  cb_stop,  "NFM", "FAST", "5kHz", 0)

cb_start = 26965000
cb_stop = 27405000
cb_step = 10000
for channel in range(40):
    program(channel+140+1,"CB CEPT %2u      "%(channel+1), cb_start+(cb_step*channel),  cb_start,  cb_stop,  "NFM", "FAST", "5kHz", 0)

cb_start = 29100000
cb_stop = 29200000
cb_step = 10000
for channel in range(40):
    program(channel+200+1,"10m FM SIMPLEX%2u"%(channel+1), cb_start+(cb_step*channel),  cb_start,  cb_stop,  "NFM", "FAST", "5kHz", 0)
