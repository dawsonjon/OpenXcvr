from baremetal import *
from baremetal.unsigned import number_of_bits_needed
from accumulator import accumulator
from math import log

def interpolate(clk, sample, interpolation_factor, channels):
    t=sample.subtype

    #difference
    count, en = counter(clk, 0, interpolation_factor//channels-1, 1)
    registered_sample = t.register(clk, en=en, d=sample, init=0)
    last_sample = t.register(clk, en=en, d=registered_sample, init=0)
    delta = registered_sample - last_sample
    output_bits = t.bits + log(interpolation_factor, 2)
    delta = delta.resize(output_bits)

    #integrator
    return accumulator(clk, delta, channels)



if __name__ == "__main__":

    from math import sin, pi
    from matplotlib import pyplot as plt
    import numpy as np

    def sin_wave():
        i=0
        while 1:
            yield sin(2.0*pi*i/100)*255
            i+= 1
    stim = iter(sin_wave())


    clk = Clock("clk")
    audio = Signed(8).input("in")
    counters = interpolate(clk, audio, 16, 8)

    clk.initialise()
    result = []
    for i in range(1000):
        audio.set(next(stim))
        for j in range(8):
            clk.tick()
            for channel in counters:
                result.append(channel.get())

    plt.plot(result)
    plt.show()

