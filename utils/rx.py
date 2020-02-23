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
import sys
from readchar import readkey

xcvr = Xcvr("/dev/ttyUSB0")

xcvr.set_frequency(7.010e6)
xcvr.set_mode(0)
xcvr.set_squelch(0)
xcvr.set_gain(6)
xcvr.set_AGC(3)

while 1:
    data = xcvr.get_audio()
    #data = np.frombuffer(data, "int16")
    #plt.plot(data)
    #plt.show()
    sys.stdout.write(data)
    print >> sys.stderr, readkey()
