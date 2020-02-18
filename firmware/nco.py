from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from accumulator import accumulator
from dither import dither
from math import sin, cos, pi

def nco(clk, frequency, lut_bits, channels):
    bits = frequency.subtype.bits
    lut_depth = 2**lut_bits
    scaling_factor = (lut_depth * 0.5-1) * 0.7
    sin_lookup_table = [sin(2.0*pi*i/lut_depth) for i in range(lut_depth)]
    sin_lookup_table = [int(round(i*scaling_factor)) for i in sin_lookup_table]
    cos_lookup_table = [cos(2.0*pi*i/lut_depth) for i in range(lut_depth)]
    cos_lookup_table = [int(round(i*scaling_factor)) for i in cos_lookup_table]

    lo = accumulator(clk, frequency, channels)
    lo = [i[bits-1:bits-lut_bits] for i in lo]
    lo = [i.subtype.register(clk, d=i) for i in lo]
    lo = [i.subtype.register(clk, d=i) for i in lo]
    lo_i = [Signed(lut_bits).rom(i, *cos_lookup_table) for i in lo]
    lo_q = [Signed(lut_bits).rom(i, *sin_lookup_table) for i in lo]
    lo_i = [i.subtype.register(clk, d=i) for i in lo_i]
    lo_q = [i.subtype.register(clk, d=i) for i in lo_q]
    lo_i = [i.subtype.register(clk, d=i) for i in lo_i]
    lo_q = [i.subtype.register(clk, d=i) for i in lo_q]

    return lo_i, lo_q

if __name__ == "__main__":

    from math import sin, pi
    from matplotlib import pyplot as plt
    import numpy as np

    clk = Clock("clk")
    lo_i, lo_q = nco(clk, 
            frequency = Unsigned(32).constant(0x00300000), 
            lut_bits = 12,
            channels = 2
    )

    clk.initialise()
    i = []
    q = []
    clk.tick()
    clk.tick()
    clk.tick()
    clk.tick()
    clk.tick()
    clk.tick()
    for it in range(1000):
        for j in range(4):
            clk.tick()
            for channel in lo_i:
                i.append(channel.get()),
            for channel in lo_q:
                q.append(channel.get()),

    i = np.array(i)
    q = np.array(q)

    spectrum = np.abs(np.fft.fftshift(np.fft.fft(i + 1.0j*q)))
    spectrum = 20.0 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum!=0))

    plt.plot(i)
    plt.plot(q)
    plt.show()

    outputs = [Unsigned(10).output("lo_i_%u"%i, x) for i, x in enumerate(lo_i)]
    outputs += [Unsigned(10).output("lo_q_%u"%i, x) for i, x in enumerate(lo_q)]

    #netlist = Netlist("nco",[clk], [], outputs)
    #print netlist.generate()
