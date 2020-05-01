import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

def compensated(x):
    return 1-np.sin(np.arccos(x))

def modulate(x, magnitude):
    threshold = 1.0-magnitude
    return [+1 if i > threshold else -1 if i < -threshold else 0 for i in x]

def plot_spectrum(x):
    plt.plot(abs(np.fft.fftshift(np.fft.fft(x))))
    plt.show()

def harmonic_magnitude(x, f):
    zeros = np.zeros(16383)
    zeros[:len(x)] = x
    x = zeros
    fftx = np.abs(np.fft.fft(x))
    indices = [int(round(len(fftx)*f*i)) for i in range(1, 8)]
    harmonics = [np.max(fftx[i-2:i+2]) for i in indices]
    
    return harmonics


f = 0.01
t = np.arange(0, 8192)*2*np.pi*float(f)
sinx = signal.sawtooth(t, 0.5)


all_harmonics = dict(zip(range(7), [[] for i in range(7)]))
for magnitude in range(100):
    magnitude = magnitude/100.0
    modulated = modulate(sinx, magnitude)
    harmonics = harmonic_magnitude(modulated, f)
    print harmonics
    for i in range(7):
        all_harmonics[i].append(
                harmonics[i])

for harmonics in all_harmonics.values():
    plt.plot(harmonics)
plt.show()

