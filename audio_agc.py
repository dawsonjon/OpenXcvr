from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from settings import Settings
from measure_magnitude import measure_magnitude
from calculate_gain import calculate_gain


def audio_agc(clk, audio, audio_stb, settings):

    #calculate magnitude and DC
    dc, magnitude = measure_magnitude(clk, audio, audio_stb, settings)

    #remove DC
    audio = audio - dc
    audio = audio.subtype.register(clk, d=audio)
    audio_stb = audio_stb.subtype.register(clk, d=audio_stb)

    #rescale the data 
    gain_m, gain_e = calculate_gain(clk, magnitude, settings)

    #squelch
    mute = magnitude < settings.squelch
    mute = mute.subtype.register(clk, d=mute)
    audio = audio.subtype.select(mute, audio, 0)
    audio = audio.subtype.register(clk, d=audio)
    audio_stb = audio_stb.subtype.register(clk, d=audio_stb)

    #scale by 2**e
    audio = audio << gain_e
    audio = audio.subtype.register(clk, d=audio)
    audio_stb = audio_stb.subtype.register(clk, d=audio_stb)

    #scale by m
    input_bits = audio.subtype.bits
    audio = audio.resize(input_bits + 
            settings.agc_lut_bits + settings.agc_lut_fraction_bits)
    audio = audio * gain_m
    audio >>= settings.agc_lut_fraction_bits
    audio = audio.resize(input_bits)
    audio = audio.subtype.register(clk, d=audio)
    audio_stb = audio_stb.subtype.register(clk, d=audio_stb)

    return audio, audio_stb

if __name__ == "__main__" and "sim" in sys.argv:

    settings = Settings()
    settings.agc_frame_size = 100
    settings.agc_frames = 4
    settings.agc_lut_bits = 7
    settings.agc_lut_fraction_bits = 8
    settings.squelch = Signed(16).input("squelch")

    clk = Clock("clk")
    data_in = Signed(16).input("data_in")
    stb_in = Boolean().input("stb_in")
    audio, audio_stb = audio_agc(clk, data_in, stb_in, settings)

    stimulus = []
    for k in range(2):
        for j in [1, 3, 6, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 32767]:
            for i in range(100):
                stimulus.append(j)
                stimulus.append(-j)
                stimulus.append(0)
        for j in reversed([1, 3, 6, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 32767]):
            for i in range(200):
                stimulus.append(j)
                stimulus.append(-j)
                stimulus.append(0)

    response = []

    #simulate
    clk.initialise()
    settings.squelch.set(100)
    stb_in.set(1)

    for data in stimulus:
        data_in.set(data)
        clk.tick()
        response.append(audio.get())

    response = np.array(response)
    plt.plot(response)
    plt.plot(stimulus)
    plt.show()
