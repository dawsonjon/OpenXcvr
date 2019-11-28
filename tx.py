from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from dither import dither
from nco import nco
from prng import prng
from math import sin
from random import randint

def sum_1_bit(clk, a,  b):
    return Boolean().register(clk, d=Boolean().select(a.cat(b), 0, 0, 1, 1))

def tx(clk, frequency, audio_i, audio_q, interpolation_factor, lut_bits, channels):
    lo_i, lo_q = nco(clk, frequency, lut_bits, channels)
    dlo_i = [dither(clk, i, True) for i in lo_i]
    dlo_q = [dither(clk, i, True) for i in lo_q]

    audio_bits = audio_i[0].subtype.bits
    audio_i = interpolate(clk, audio_i, interpolation_factor, channels)
    audio_q = interpolate(clk, audio_q, interpolation_factor, channels)
    msb = audio_i[0].subtype.bits - 1
    lsb = msb - audio_bits + 1
    audio_i = [dither(clk, i, True) for i in audio_i]
    audio_q = [dither(clk, i, True) for i in audio_q]

    rf_i = [a^l for a, l in zip(audio_i, dlo_i)]
    rf_q = [a^l for a, l in zip(audio_q, dlo_q)]
    rf = [sum_1_bit(clk, i, q) for i, q in zip(rf_i, rf_q)]

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
    rf, i, q = tx(clk, 
            frequency = frequency, 
            audio_i = audio_i,
            audio_q = audio_q,
            interpolation_factor = 64, #from 300000000 to 9180
            lut_bits = 10,
            channels = 2
    )


if "sim" in sys.argv:
    clk.initialise()
    response = []
    audio_i.set(127)
    audio_q.set(127)
    frequency.set(0x40020000)
    clk.tick()
    clk.tick()
    clk.tick()
    for it in range(20000):
        clk.tick()
        for channel in rf:
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
