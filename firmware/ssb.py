from baremetal import *
from math import pi, sin, cos
import sys

from half_band_filter import half_band_filter
from cordic import rectangular_to_polar
from scale import scale

def upconverter(clk, i, q, stb):
    phase, _ = counter(clk, 0, 3, 1, en=stb)

    i, q = i.subtype.select(phase, i, -q, -i, q), q.subtype.select(phase, q, i, -q, -i)

    i = i.subtype.register(clk, d=i, init=0)
    q = q.subtype.register(clk, d=q, init=0)
    stb = stb.subtype.register(clk, d=stb, init=0)

    return i, q, stb

def downconverter(clk, i, q, stb):
    phase, _ = counter(clk, 0, 3, 1, en=stb)

    i, q = i.subtype.select(phase, i, q, -i, -q), q.subtype.select(phase, q, -i, -q, i)

    i = i.subtype.register(clk, d=i, init=0)
    q = q.subtype.register(clk, d=q, init=0)
    stb = stb.subtype.register(clk, d=stb, init=0)

    return i, q, stb


def ssb(clk, audio, stb, lsb):
    i = audio
    q = audio.subtype.constant(0)
    i, q, stb = upconverter(clk, i, q, stb)
    i, q, stb = half_band_filter(clk, i, q, stb)
    i, q, stb = downconverter(clk, i, q, stb)
    i, q = i.subtype.select(lsb, q, i), q.subtype.select(lsb, i, q)
    return i, q, stb


def ssb_polar(clk, audio, stb, lsb):
    i, q, stb = ssb(clk, audio, stb, lsb)
    magnitude, phase, stb, gain = rectangular_to_polar(clk, i, q, stb)
    #scale magnitude to use the available bits.
    #ideal scaling would be ~2.4
    #2.25 is close but smaller
    magnitude = (magnitude << 1) + (magnitude >> 2)
    magnitude = magnitude.subtype.register(clk, d=magnitude, init=0)
    phase = phase.subtype.register(clk, d=phase, init=0)
    stb = stb.subtype.register(clk, d=stb, init=0)
    return magnitude, phase, stb


import numpy as np
from matplotlib import pyplot as plt
from itertools import cycle

def test_modulator_1(stimulus):

    clk = Clock("clk")
    audio_in = Signed(12).input("i_data_in")
    audio_stb_in = Boolean().input("stb_in")
    lsb_in = Boolean().input("lsb_in")

    i, q, stb = ssb(clk, audio_in, audio_stb_in, lsb_in) 

    #simulate
    clk.initialise()
    lsb_in.set(0)

    response = []
    for data in stimulus:
        for j in range(400):
            audio_stb_in.set(j==199)
            audio_in.set(data)
            clk.tick()
            if stb.get():
                print i.get(), q.get()
                if i.get() is None:
                    continue
                if q.get() is None:
                    continue
                response.append(i.get()+1j*q.get())

    response = np.array(response)
    plt.title("SSB Modulator Time Domain")
    plt.xlabel("Time (samples)")
    plt.ylabel("Value")

    cycol = cycle('bgrcmk')
    a, = plt.plot(np.real(response), c=next(cycol), label="I")
    c, = plt.plot(stimulus, c=next(cycol), label="Audio Input")
    b, = plt.plot(np.imag(response), c=next(cycol), label="Q")
    plt.legend(handles=[a, b, c])
    plt.show()

    plt.title("SSB Frequency Response")
    plt.xlabel("Time (samples)")
    plt.ylabel("Value")

    stimulus = stimulus[:len(response)]

    a, = plt.plot(
            np.linspace(-6, 6, len(response)), 
            20*np.log10(abs(np.fft.fftshift(np.fft.fft(stimulus)))), label = "Input")
    b, = plt.plot(
            np.linspace(-6, 6, len(response)), 
            20*np.log10(abs(np.fft.fftshift(np.fft.fft(response)))), label = "Output")
    plt.legend(handles=[a, b])
    plt.show()

def test_modulator_2(stimulus):

    clk = Clock("clk")
    audio_in = Signed(12).input("i_data_in")
    audio_stb_in = Boolean().input("stb_in")
    lsb_in = Boolean().input("lsb_in")

    i, q, stb = ssb_polar(clk, audio_in, audio_stb_in, lsb_in) 

    #simulate
    clk.initialise()
    lsb_in.set(0)

    response = []
    for data in stimulus:
        for j in range(400):
            audio_stb_in.set(j==199)
            audio_in.set(data)
            clk.tick()
            if stb.get():
                print i.get(), q.get()
                if i.get() is None:
                    continue
                if q.get() is None:
                    continue
                response.append(i.get()+1j*q.get())

    response = np.array(response)
    plt.title("SSB Modulator Time Domain")
    plt.xlabel("Time (samples)")
    plt.ylabel("Value")

    cycol = cycle('bgrcmk')
    a, = plt.plot(np.real(response), c=next(cycol), label="I")
    c, = plt.plot(stimulus, c=next(cycol), label="Audio Input")
    b, = plt.plot(np.imag(response), c=next(cycol), label="Q")
    plt.legend(handles=[a, b, c])
    plt.show()

    plt.title("SSB Frequency Response")
    plt.xlabel("Time (samples)")
    plt.ylabel("Value")

    stimulus = stimulus[:len(response)]

    a, = plt.plot(
            np.linspace(-6, 6, len(response)), 
            20*np.log10(abs(np.fft.fftshift(np.fft.fft(stimulus)))), label = "Input")
    b, = plt.plot(
            np.linspace(-6, 6, len(response)), 
            20*np.log10(abs(np.fft.fftshift(np.fft.fft(response)))), label = "Output")
    plt.legend(handles=[a, b])
    plt.show()

if __name__ == "__main__" and "sim" in sys.argv:

    #mode am stim am
    stimulus=(
        (
            np.sin(np.arange(1000)*2.0*pi*0.03)+
            np.sin(np.arange(1000)*2.0*pi*0.02)
        )*
        ((2**10)-1)#scale to 8 bits
    )
    plt.plot(stimulus)
    plt.show()
    test_modulator_2(stimulus)
