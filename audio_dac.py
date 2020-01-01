from baremetal import *
import sys

def audio_dac(clk, audio, audio_stb):
    audio_bits = audio.subtype.bits
    t_data = Signed(audio_bits+1)
    sample = t_data.register(clk, d=audio, en=audio_stb, init=0)

    sigma = t_data.register(clk, init=0)
    quantized = Boolean().constant(0)+~sigma[audio_bits]

    max_val = (2**(audio_bits-1)-1)
    min_val = -(2**(audio_bits-1)-1)
    reconstructed = t_data.select(quantized, min_val, max_val)
    delta = sample - reconstructed
    sigma.d(sigma+delta)

    return quantized

import numpy as np
from matplotlib import pyplot as plt
from math import pi

def test_audio_dac(stimulus):

    clk = Clock("clk")
    audio_in = Signed(16).input("i_data_in")
    audio_stb_in = Boolean().input("stb_in")

    output = audio_dac(clk, audio_in, audio_stb_in) 

    clk.initialise()

    response = []
    for data in stimulus:
        for j in range(1000):
            audio_stb_in.set(j==999)
            audio_in.set(data)
            clk.tick()
            print output.get()
            response.append(output.get()-0.5)

    response = np.array(response)
    response -= np.mean(response)
    plt.plot(response)
    #plt.plot(20*np.log10(abs(np.fft.fftshift(np.fft.fft(response)))))
    plt.plot(stimulus)
    plt.show()


if __name__ == "__main__" and "sim" in sys.argv:

    #mode am stim am
    stimulus=(
        np.sin(np.arange(100)*2.0*pi*0.01)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
        ((2**15)-1)#scale to 16 bits
    )
    test_audio_dac(stimulus)
