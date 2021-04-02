#!/usr/bin/env python
from __future__ import print_function

import struct
import numpy as np
import math
from numpy import array, zeros, ones, around, unwrap, log10, angle, mean
from scipy.signal import lfilter, freqz, remez
from scipy import signal
import matplotlib.pyplot as plt
from openxcvr import Xcvr
import sys
import time

frequency = 1.125e6
mode = "AM"

sample_rate_for_modes = {
        "AM" : 12207,
        "LSB" : 6103,
        "USB" : 6103,
        "FM" : 24414,
        "NFM" : 24414,
        "CW" : 8138,
}


xcvr = Xcvr("/dev/ttyUSB0")
xcvr.set_frequency(frequency)
xcvr.set_mode(mode)
xcvr.set_volume(1)
xcvr.set_squelch(0)
xcvr.enable_audio_output()

while 1:
    data = xcvr.get_audio()
    sys.stdout.write(data)
    #print(len(data), time.time()-t0, len(data)/(time.time()-t0), max(values), file=sys.stderr)

