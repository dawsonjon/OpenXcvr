import numpy as np
import matplotlib.pyplot as plt
import sys

def read_response(filename):
    inf = open(filename)
    frequencies = []
    powers = []
    for line in inf:
        frequency, power = line.split()
        frequency = float(frequency)
        power = float(power)
        frequencies.append(frequency)
        powers.append(power)

    return np.array(frequencies), 20*np.log10(np.array(powers))

handles = []
full_scale = 20*np.log10(1000*2**16)
for filename in sys.argv[1:]:
    f, p = read_response(filename)
    print full_scale
    print p
    a, = plt.plot(f/1e6, - (full_scale - p), label=filename)
    handles.append(a)

plt.grid(True)
plt.title("Magnitude Response")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Gain (dB)")
plt.xscale("log")
plt.legend(handles=handles)
plt.show()
