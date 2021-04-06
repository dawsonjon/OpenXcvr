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


tone=np.sin(np.arange(1024)*2.0*np.pi*1/32)*127
tone=tone.astype("int8")
plt.plot(tone)
plt.show()
