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

xcvr.set_frequency(1.215e6)
xcvr.set_mode(1)
xcvr.set_squelch(0)
xcvr.set_gain(4)
xcvr.set_band(4)
xcvr.set_AGC(3)

while 1:
    data = xcvr.get_audio()
    sys.stdout.write(data)
