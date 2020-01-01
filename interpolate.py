from baremetal import *
from baremetal.unsigned import number_of_bits_needed
from accumulator import accumulator
from math import log, ceil

def interpolate(clk, sample, stb, interpolation_factor, channels):
    t=sample.subtype

    #difference
    registered_sample = t.register(clk, en=stb, d=sample, init=0)
    last_sample = t.register(clk, en=stb, d=registered_sample, init=0)
    delta = registered_sample - last_sample
    output_bits = t.bits + ceil(log(interpolation_factor, 2))+1
    delta = delta.resize(output_bits)
    interpolated = registered_sample

    #integrator
    return [interpolated, interpolated]#accumulator(clk, delta, channels)



if __name__ == "__main__":

    from math import sin, pi
    from matplotlib import pyplot as plt
    import numpy as np

    stim=(
        np.exp(1j*np.arange(100)*2.0*pi*0.01)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
        ((2**7)-1)#scale to 16 bits
    )


    clk = Clock("clk")
    audio = Signed(8).input("in")
    stb = Boolean().input("stb")
    counters = interpolate(clk, audio, stb, 3000, 2)


    clk.initialise()
    result = []
    for i in stim:
        for j in range(3000):
            stb.set(j==2999)
            audio.set(i)
            clk.tick()
            for counter in counters:
                print counter.get()
                result.append(counter.get())

    plt.plot(result)
    plt.show()

