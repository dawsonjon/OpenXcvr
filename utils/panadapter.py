#!/usr/bin/env python3

#python modules
import sys
import time
import subprocess
from multiprocessing import Process, Queue
import atexit

#numpy etc
import numpy as np
import matplotlib.pyplot as plt

#open xcvr modules
from openxcvr import Xcvr
from cat_server import cat_server, command_queue

#user settings
plot_data = True
frequency = 7.074e6
mode = "USB"

sample_rate_for_modes = {
        "AM" : 12207,
        "LSB" : 6103,
        "USB" : 6103,
        "FM" : 24414,
        "NFM" : 24414,
        "CW" : 8138,
}


xcvr = Xcvr("/dev/ttyUSB1")
xcvr.set_frequency(frequency)
xcvr.set_mode(mode)
xcvr.set_volume(1)
xcvr.set_squelch(0)

waterfall = np.zeros([100, 2048])
fig, (ax1, ax2, ax3) = plt.subplots(3)
ax1.set_ylim(-100.0, 0.0)
ax3.set_ylim(-1.0, 1.0)

while 1:

    i_values, q_values = xcvr.capture()
    values = i_values+1.0j*q_values

    #create frequency domain representation
    spectrum = abs(np.fft.fft(values))
    points = len(spectrum)
    spectrum /= points
    spectrum = 20*np.log10(spectrum)
    spectrum = spectrum

    #plot frequency domain representation
    ax1.plot(spectrum)

    #waterfall plot
    waterfall[1:99] = waterfall[0:98]
    waterfall[0] = spectrum
    ax2.imshow(waterfall)

    #plot time domain signal
    ax3.plot(values/32768)

    plt.draw()
    plt.pause(0.01)
    ax1.clear()
    ax3.clear()
