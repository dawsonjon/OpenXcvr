from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from dither import dither
from nco import nco
from prng import prng
from math import sin
from random import randint

def rf_section(clk, frequency, audio_i, audio_q, audio_stb, interpolation_factor, lut_bits, channels):
    dlo_i, dlo_q = nco(clk, frequency, lut_bits, channels)
    dlo_i = [i.label("nco_i_%s"%idx) for idx, i in enumerate(dlo_i)]
    dlo_q = [i.label("nco_q_%s"%idx) for idx, i in enumerate(dlo_q)]
    lo_i = [i[i.subtype.bits-1] for i in dlo_i]
    lo_q = [i[i.subtype.bits-1] for i in dlo_q]

    audio_bits = audio_i.subtype.bits
    audio_i = interpolate(clk, audio_i, audio_stb, interpolation_factor, channels)
    audio_q = interpolate(clk, audio_q, audio_stb, interpolation_factor, channels)
    audio_i = [i.label("audio_i_%s"%idx) for idx, i in enumerate(audio_i)]
    audio_q = [i.label("audio_q_%s"%idx) for idx, i in enumerate(audio_q)]

    product_bits = audio_bits + lut_bits - 1
    rf_i = [((a.resize(product_bits)*l)>>lut_bits-1).resize(audio_bits) for a, l in zip(audio_i, dlo_i)]
    rf_q = [((a.resize(product_bits)*l)>>lut_bits-1).resize(audio_bits) for a, l in zip(audio_q, dlo_q)]
    rf_i = [i.subtype.register(clk, d=i) for i in rf_i]
    rf_q = [i.subtype.register(clk, d=i) for i in rf_q]
    rf_i = [i.label("rf_i_%s"%idx) for idx, i in enumerate(rf_i)]
    rf_q = [i.label("rf_q_%s"%idx) for idx, i in enumerate(rf_q)]
    
    rf = [i.subtype.register(clk, d=i+q) for i, q in zip(rf_i, rf_q)]
    rf = [i.label("rf_full_%s"%idx) for idx, i in enumerate(rf)]
    rf = [dither(clk, i, True) for i in rf]

    return rf, lo_i, lo_q

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
