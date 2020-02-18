from prng import prng
from baremetal import *
from random import randint


def dither(clk, x, lite=False):
    bits = x.subtype.bits
    signed_prng = Signed(bits).constant(0)+prng(clk, bits, randint(0, 2**60), lite)
    return Boolean().register(clk, d=x>signed_prng)


if __name__ == "__main__":

    from math import sin, pi
    from matplotlib import pyplot as plt
    import numpy as np

    #Make a generator to model a sin wave input
    def sin_wave():
        i=0
        while 1:
            yield sin(2.0*pi*i/500)*511
            i+= 1
    stim = iter(sin_wave())

    #Simulate
    clk = Clock("clk")
    audio = Signed(10).input("in")
    shifter = dither(clk, audio, False)

    clk.initialise()
    clk.tick()
    audio.set(next(stim))
    clk.tick()
    stimulus = []
    results = []
    for i in range(1000):
        x = next(stim)
        audio.set(x)
        stimulus.append(x)
        results.append(shifter.get()-0.5)
        clk.tick()

    spectrum = np.abs(np.fft.fftshift(np.fft.fft(results)))
    spectrum = 20.0 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum!=0))

    #plot results
    plt.plot(spectrum)
    plt.show()

    plt.title("Dithering")
    a, = plt.plot(stimulus, label="Input to Dither")
    b, = plt.plot(np.array(results)*1023, label="Output from Dither")
    plt.legend(handles=[a, b])
    plt.show()
