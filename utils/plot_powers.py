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

    return np.array(frequencies), np.array(powers)

handles = []
for filename in sys.argv[1:]:
    f, p = read_response(filename)
    a, = plt.plot(f/1e6, p, label=filename)
    handles.append(a)

plt.grid(True)
plt.title("Power Output")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Power (W)")
plt.legend(handles=handles)
plt.show()
