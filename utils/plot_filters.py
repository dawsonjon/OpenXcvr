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

f, baseline_p = read_response("baseline")
f, f_2_4 = read_response("f_2_4")
f, f_4_8 = read_response("f_4_8")
f, f_8_16 = read_response("f_8_16")
f, f_16_32 = read_response("f_16_30")
f, f_14 = read_response("f_14")

a, = plt.plot(f/1e6, f_2_4 - baseline_p, label="band 3")
b, = plt.plot(f/1e6, f_4_8 - baseline_p, label="band 2")
c, = plt.plot(f/1e6, f_8_16 - baseline_p, label="band 1")
d, = plt.plot(f/1e6, f_16_32 - baseline_p, label="band 0")
plt.grid(True)
plt.title("Magnitude Response")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Gain (dB)")
plt.xscale("log")
plt.legend(handles=[a, b, c, d])
plt.show()
