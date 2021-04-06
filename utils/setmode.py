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
import time

xcvr = Xcvr("/dev/ttyUSB0")
#xcvr.enter_cat_mode()
xcvr.set_mode("FM")
xcvr.set_frequency(7000000)
xcvr.set_squelch(0)
xcvr.set_volume(0)
xcvr.set_TX(1)
time.sleep(1)
xcvr.set_TX(0)
xcvr.exit_cat_mode()
