import numpy as np
import matplotlib.pyplot as plt

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

f, response = read_response("noise_floor")

d, = plt.plot(f/1e6, response)
plt.grid(True)
plt.title("Magnitude Response")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Gain (dB)")
plt.xscale("log")
plt.show()
