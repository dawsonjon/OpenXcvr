from baremetal import *
from math import sin, pi
from matplotlib import pyplot as plt

def test_tone(clk):
    count, stb = counter(clk, 0, 1499, 1)
    phase, _ = counter(clk, 0, 65535, 655, en=stb)
    phase = phase[15:8]

    lut_depth = 256
    scaling_factor = 127
    sin_lookup_table = [sin(2.0*pi*i/lut_depth) for i in range(lut_depth)]
    sin_lookup_table = [int(round(i*scaling_factor)) for i in sin_lookup_table]
    test_signal = Signed(8).rom(phase, *sin_lookup_table)
    #test_signal = test_signal.subtype.register(clk, d=test_signal, en=stb)
    #stb = stb.subtype.register(clk, d=stb)

    return test_signal, stb

if __name__ == "__main__":

    clk = Clock("clk")

    test_signal, stb = test_tone(clk)
    clk.initialise
    response = []
    for i in range(500000):
        if stb.get():
            response.append(test_signal.get())
        clk.tick()

    plt.plot(response)
    plt.show()

