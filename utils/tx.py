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

xcvr.set_frequency(29.6e6)
xcvr.set_mode(1)
xcvr.set_USB_audio(1)
xcvr.set_TX(1)

stimulus=(
    np.sin(np.arange(1000000)*2.0*np.pi*0.006)*
    ((2**7)-1)
)

for i in range(len(stimulus)/1000):
    print i
    data = stimulus[i*1000:i*1000+1000]
    data = data.astype("int8")
    data = data.tobytes()
    xcvr.put_audio(data)

xcvr.set_TX(0)
xcvr.set_USB_audio(0)
