from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from dither import dither
from accumulator import accumulator
from prng import prng
from math import sin
from random import randint
from audio_dac import audio_dac

def rf_section(clk, frequency, audio_i, audio_q, audio_stb, interpolation_factor, lut_bits, channels, rx_tx, enable_test_signal):
    lo = accumulator(clk, frequency, channels)
    lo = [i.subtype.register(clk, d=i, init=0) for i in lo]
    lo = [i[31:30] for i in lo]

    lo_i = [Boolean().select(i, 0, 1, 1, 0) for i in lo]
    lo_q = [Boolean().select(i, 0, 0, 1, 1) for i in lo]

    audio_i = audio_dac(clk, audio_i, audio_stb)
    audio_q = audio_dac(clk, audio_q, audio_stb)

    rf = [audio_i.subtype.select(i, audio_i, audio_q, ~audio_i, ~audio_q) for i in lo]
    rf = [i.subtype.register(clk, d=i, init=0) for i in rf]

    #blank rf output during tx
    temp = rf
    rf = [i.subtype.select(rx_tx, 0, i) for i in rf]
    test_signal = [i.subtype.select(enable_test_signal, 0, i) for i in temp]

    return rf, lo_i, lo_q, test_signal

if __name__ == "__main__":

    from math import sin, pi
    from matplotlib import pyplot as plt
    import numpy as np
    import sys

    clk = Clock("clk")
    frequency = Unsigned(32).input("frequency")
    audio_i = Signed(8).input("audio_i")
    audio_q = Signed(8).input("audio_q")
    stb = Boolean().input("audio_stb")
    rf, i, q = rf_section(clk, 
            frequency = frequency, 
            audio_i = audio_i,
            audio_q = audio_q,
            audio_stb = stb,
            interpolation_factor = 64, #from 300000000 to 9180
            lut_bits = 10,
            channels = 2
    )


    if "sim" in sys.argv:

        stim=(
            np.exp(1j*np.arange(100)*2.0*pi*0.01)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
            ((2**7)-1)#scale to 16 bits
        )

        clk.initialise()
        response = []
        frequency.set(0x40000000)
        clk.tick()
        clk.tick()
        clk.tick()
        for i in stim:
            for j in range(1500):
                audio_i.set(int(np.real(i)))
                audio_q.set(int(np.imag(i)))
                stb.set(j==1499)
                clk.tick()
                for channel in rf:
                    print channel.get()
                    if channel.get() is not None:
                        response.append(channel.get())

        response = response-np.mean(response)
        spectrum = np.abs(np.fft.fftshift(np.fft.fft(response)))
        spectrum = 20.0 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum!=0))

        plt.plot(response)
        #plt.ylim([-1, 1])
        plt.show()

        plt.plot(spectrum)
        plt.ylim([40, 100])
        plt.show()

    if "gen" in sys.argv:

        rf = [i.subtype.output("rf_%u"%idx, i) for idx, i in enumerate(rf)]

        netlist = Netlist(
            "tx",
            [clk], 
            [frequency, audio_i, audio_q],
            rf,
        )
        f = open("tx.v", "w")
        f.write(netlist.generate())
