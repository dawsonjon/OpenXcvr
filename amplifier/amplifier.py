import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

def compensated(x):
    return 1-np.sin(np.arccos(x))

def modulate(x, threshold):
    return [+1 if i > threshold else -1 if i < -threshold else 0 for i in x]

def plot_spectrum(x):
    plt.plot(abs(np.fft.fftshift(np.fft.fft(x))))
    plt.show()

def fundamental_magnitude(x):
    return max(abs(np.fft.fft(x)))


t = np.linspace(0, np.pi*2, 1000)
#sinx = np.sin(t)
sinx = signal.sawtooth(t, 0.5)
#sinx = compensated(t)
#plt.plot(t, sinx)
#plt.plot(t, t)
#plt.plot(t, t/sinx*sinx)
#plt.show()

magnitudes = []
inputs = []
for magnitude in range(0, 101):
    magnitude/=100.0
    correction = magnitude/np.sin(magnitude*np.pi*0.5)
    print correction

    magnitudes.append(fundamental_magnitude(modulate(sinx, (1-magnitude*correction))))
    inputs.append(magnitude)
    
plt.plot(inputs, magnitudes)
plt.plot(inputs, 635*np.sin(0.5*np.pi*np.array(inputs)))
plt.show()
