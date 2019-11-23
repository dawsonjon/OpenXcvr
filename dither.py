from prng import prng
from baremetal import *
from random import randint


def dither(clk, x, lite=False):
    bits = x.subtype.bits
    return Boolean().register(clk, d=x>prng(clk, bits, randint(0, 2**60), lite))


if __name__ == "__main__":

    from math import sin, pi
    from matplotlib import pyplot as plt
    import numpy as np

    #Make a generator to model a sin wave input
    def sin_wave():
        i=0
        while 1:
            yield sin(2.0*pi*i/10)*511
            i+= 1
    stim = iter(sin_wave())

    #Simulate
    clk = Clock("clk")
    audio = Signed(12).input("in")
    shifter = dither(clk, audio, False)

    clk.initialise()
    clk.tick()
    audio.set(next(stim))
    clk.tick()
    results = []
    for i in range(10000):
        audio.set(next(stim))
        results.append(shifter.get()-0.5)
        clk.tick()

    spectrum = np.abs(np.fft.fftshift(np.fft.fft(results)))
    spectrum = 20.0 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum!=0))

    #plot results
    plt.plot(spectrum)
    plt.show()
