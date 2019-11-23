from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from dither import dither
from nco import nco
from prng import prng
from math import sin
from random import randint

def mix(clk, lo, audio):
    product = lo.resize(lo.subtype.bits+audio.subtype.bits-1)*audio
    product = product[product.subtype.bits-1:product.subtype.bits-lo.subtype.bits]
    return product

def tx(clk, frequency, audio_i, audio_q, interpolation_factor, lut_bits, channels):
    lo_i, lo_q = nco(clk, frequency, lut_bits, channels)
    audio_i = interpolate(clk, audio_i, interpolation_factor, channels)
    audio_q = interpolate(clk, audio_q, interpolation_factor, channels)
    rf_i = [mix(clk, l, a) for a, l in zip(audio_i, lo_i)]
    rf_q = [mix(clk, l, a) for a, l in zip(audio_q, lo_q)]
    rf = [i+q for i, q in zip(rf_i, rf_q)]
    rf = [i.subtype.register(clk, d=i) for i in rf]
    rf = [dither(clk, i) for i in rf]
    msb = lo_i[0].subtype.bits-1
    lo_i = [i[msb] for i in lo_i]
    lo_q = [i[msb] for i in lo_q]
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
            interpolation_factor = 64,
            lut_bits = 10,
            channels = 2
    )


if "sim" in sys.argv:
    clk.initialise()
    response = []
    audio_i.set(127)
    audio_q.set(127)
    frequency.set(0x10000000)
    clk.tick()
    clk.tick()
    clk.tick()
    for it in range(20000):
        clk.tick()
        for channel in rf:
            response.append(channel.get()-0.5)

    response = response-np.mean(response)
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(response)))
    spectrum = 20.0 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum!=0))

    #plt.plot(response)
    #plt.ylim([-1, 1])
    #plt.show()

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
