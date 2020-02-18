from baremetal import *
from math import pi, sin, cos
import sys
from scale import scale
from settings import *



def modulator(clk, audio, audio_stb, settings):

    #generating I and Q for am and FM are fairly trivial
    audio_bits = audio.subtype.bits
    dc = (2**(audio_bits-2))-1
    am_i = (audio >> 1) + dc
    am_q = (audio >> 1) + dc
    ssb_i = audio.resize(audio_bits+1)<<1
    ssb_q = audio.subtype.constant(0)

    #FM is generated using a phase accumulator driving a look-up table
    #scale audio to give correct frequency deviation depending on mode
    audio_bits = audio.subtype.bits
    extra_bits = 8
    frequency = scale(audio, 5.0/100, extra_bits, False)
    frequency_wideband = frequency
    frequency_narrowband = (frequency>>1)
    frequency = frequency_wideband.subtype.select(settings.mode==NBFM, frequency_wideband, frequency_narrowband)
    frequency = frequency.subtype.register(clk, d=frequency, en=audio_stb)
    frequency_stb = Boolean().register(clk, d=audio_stb, init=0)

    #accumulate phase
    phase = frequency.subtype.register(clk, init=0, en=frequency_stb)
    phase.d(phase + frequency)
    phase_stb = Boolean().register(clk, d=frequency_stb, init=0)
    phase = phase[audio_bits+extra_bits-1:extra_bits]#keep MSBs

    #convert phase to i/q
    lut_depth = 2**audio.subtype.bits
    scaling_factor = (2.0**(audio.subtype.bits-1))-1
    sin_lookup_table = [sin(2.0*pi*i/lut_depth) for i in range(lut_depth)]
    sin_lookup_table = [int(round(i*scaling_factor)) for i in sin_lookup_table]
    cos_lookup_table = [cos(2.0*pi*i/lut_depth) for i in range(lut_depth)]
    cos_lookup_table = [int(round(i*scaling_factor)) for i in cos_lookup_table]
    fm_i = audio.subtype.rom(phase, *cos_lookup_table)
    fm_q = audio.subtype.rom(phase, *sin_lookup_table)
    fm_i = fm_i.subtype.register(clk, d=fm_i)
    fm_q = fm_q.subtype.register(clk, d=fm_q)
    fm_stb = Boolean().register(clk, d=frequency_stb, init=0)


    i = ssb_i.subtype.select(settings.mode, ssb_i, am_i, fm_i, fm_i)
    q = ssb_q.subtype.select(settings.mode, ssb_q, am_q, fm_q, fm_q)
    stb = Boolean().select(settings.mode, audio_stb, audio_stb, fm_stb, fm_stb)

    return i, q, stb

import numpy as np
from matplotlib import pyplot as plt

def test_modulator(stimulus, mode):

    settings = Settings()
    settings.mode = Unsigned(3).input("filter_mode")

    clk = Clock("clk")
    audio_in = Signed(8).input("i_data_in")
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
        np.sin(np.arange(10000)*2.0*pi*0.01)*
        ((2**7)-1)#scale to 16 bits
    )
    test_modulator(stimulus, AM)
    test_modulator(stimulus, FM)
    test_modulator(stimulus, NBFM)
    test_modulator(stimulus, SSB)
