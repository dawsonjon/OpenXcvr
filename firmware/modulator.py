from baremetal import *
from math import pi, sin, cos
import sys
from scale import scale
from settings import *



def modulator(clk, audio, audio_stb, settings):
    audio_bits = audio.subtype.bits

    #AM modulation
    am_mag   = Unsigned(12).constant(0) + audio + 2048
    am_phase = Signed(32).constant(0)
    am_stb   = audio_stb

    #FM modulation
    fm_mag = Unsigned(12).constant(4095)
    frequency = Signed(32).constant(0) + audio

    nfm_scaled_frequency = frequency * (2**(32-audio_bits) * 5 / 50)
    nfm_phase = nfm_scaled_frequency.subtype.register(clk, en=audio_stb, init=0)
    nfm_phase.d(nfm_phase + nfm_scaled_frequency)

    scaled_frequency = frequency * (2**(32-audio_bits) * 8 / 50)
    fm_phase = scaled_frequency.subtype.register(clk, en=audio_stb, init=0)
    fm_phase.d(fm_phase + scaled_frequency)

    fm_stb = Boolean().register(clk, d=audio_stb, init=0)

    #lsb modulation
    lsb_mag   = Unsigned(12).constant(0)
    lsb_phase = Signed(32).constant(0)
    lsb_stb   = audio_stb

    #usb modulation
    usb_mag   = Unsigned(12).constant(0)
    usb_phase = Signed(32).constant(0)
    usb_stb   = audio_stb

    #cw modulation
    cw_mag   = Unsigned(12).constant(0)
    cw_phase = Signed(32).constant(0)
    cw_stb   = audio_stb

    #mode switching
    magnitude     = Unsigned(12).select(settings.mode, am_mag,   fm_mag,    fm_mag,    lsb_mag,     usb_mag,     cw_mag)
    phase         = Signed(32).select(settings.mode,   am_phase, nfm_phase, fm_phase,  lsb_phase,   usb_phase,   cw_phase)
    stb           = Boolean().select(settings.mode,    am_stb,   fm_stb,    fm_stb,    lsb_stb,     usb_stb,     cw_stb)


    return magnitude, phase, audio_stb

import numpy as np
from matplotlib import pyplot as plt

def test_modulator(stimulus, mode):

    settings = Settings()
    settings.mode = Unsigned(3).input("filter_mode")

    clk = Clock("clk")
    audio_in = Signed(12).input("i_data_in")
    audio_stb_in = Boolean().input("stb_in")

    i, q, stb = modulator(clk, audio_in, audio_stb_in, settings) 

    #simulate
    clk.initialise()
    settings.mode.set(mode)

    response = []
    for data in stimulus:
        for j in range(5):
            audio_stb_in.set(j==4)
            audio_in.set(data)
            clk.tick()
            if stb.get():
                print i.get(), q.get()
                response.append(i.get()+1j*q.get())

    response = np.array(response)
    plt.title("Modulator")
    plt.xlabel("Time (samples)")
    plt.ylabel("Value")
    a, = plt.plot(np.real(response), label="I")
    b, = plt.plot(np.imag(response), label="Q")
    c, = plt.plot(stimulus, label="Audio Input")
    plt.legend(handles=[a, b, c])
    plt.show()




if __name__ == "__main__" and "sim" in sys.argv:

    #mode am stim am
    stimulus=(
        np.sin(np.arange(10000)*2.0*pi*0.01)*2047
    )
    test_modulator(stimulus, FM)
    #test_modulator(stimulus, FM)
    #test_modulator(stimulus, NBFM)
    #test_modulator(stimulus, SSB)
