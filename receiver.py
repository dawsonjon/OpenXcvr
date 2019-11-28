from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from audio_agc import audio_agc
from filter import filter
from demodulator import demodulator
from settings import Settings

def receiver(clk, i, q, stb, settings):
    i, q, stb = filter(clk, i, q, stb, settings)
    audio, audio_stb = demodulator(clk, i, q, stb, settings)
    audio, audio_stb = audio_agc(clk, audio, audio_stb, settings)
    return audio, audio_stb

def test_receiver(stimulus, sideband, mode):
    settings = Settings()
    settings.filter_kernel_bits = 18
    settings.agc_frame_size = 800
    settings.agc_frames = 2
    settings.agc_lut_bits = 7
    settings.agc_lut_fraction_bits = 8
    settings.squelch = Signed(16).input("squelch")
    settings.filter_mode = Unsigned(2).input("filter_mode")
    settings.filter_sideband = Unsigned(2).input("filter_sideband")
    

    taps = 255
    clk = Clock("clk")
    i_data_in = Signed(16).input("i_data_in")
    q_data_in = Signed(16).input("q_data_in")
    stb_in = Boolean().input("stb_in")

    audio, audio_stb = receiver(clk, i_data_in, q_data_in, stb_in, settings) 

    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.show()

    #simulate
    clk.initialise()
    settings.squelch.set(0)
    settings.filter_mode.set(mode)
    settings.filter_sideband.set(sideband)

    response = []
    for data in stimulus:
        for j in range(taps+2):
            stb_in.set(j==taps+1)
            i_data_in.set(np.real(data))
            q_data_in.set(np.imag(data))
            clk.tick()
            if audio_stb.get():
                print audio.get()
                response.append(audio.get())

    response = np.array(response)
    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.plot(response)
    plt.show()
    plt.plot(20*np.log10(abs(np.fft.fftshift(np.fft.fft(response)))))
    plt.show()


if __name__ == "__main__" and "sim" in sys.argv:

    #mode am stim am
    stimulus=(
        np.exp(1j*np.arange(4000)*2.0*pi*0.0005)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
        (np.sin(np.arange(4000)*2.0*pi*0.01)*0.5+0.5)* #The signal a tone
        ((2**15)-1)#scale to 16 bits
    )
    #test_receiver(stimulus, 0, 1)#lsb AM

    #mode usb stim dsb
    stimulus=(
        np.sin(np.arange(4000)*2.0*pi*0.01)*
        ((2**15)-1)#scale to 16 bits
    )
    #test_receiver(stimulus, 1, 0)#usb SSB

    #mode fm
    audio=np.sin(np.arange(4000)*2.0*pi*0.01)
    frequency = audio * 0.05 * pi#0.1*+/-50kHZ = +/-5KHz
    phase = np.cumsum(frequency)
    stimulus = (
        np.exp(1.0j*phase)*
        ((2**15)-1)#scale to 16 bits
    )
    test_receiver(stimulus, 1, 2)#usb FM

    #mode nfm
    audio=np.sin(np.arange(4000)*2.0*pi*0.01)
    frequency = audio * 0.025 * pi#0.1*+/-50kHZ = +/-5KHz
    phase = np.cumsum(frequency)
    stimulus = (
        np.exp(1.0j*phase)*
        ((2**15)-1)#scale to 16 bits
    )
    test_receiver(stimulus, 1, 3)#usb FM
