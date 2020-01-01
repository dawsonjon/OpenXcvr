from baremetal import *
import sys
from math import ceil, log

def audio_adc(clk, adc_in, oversample=3000):

    adc_out = Boolean().register(clk, d=adc_in)
    
    bits = ceil(log(oversample, 2))+1
    t_data = Signed(bits)
    accumulator = t_data.register(clk, init=0)
    accumulator.d(t_data.select(adc_out, accumulator-1, accumulator+1))

    count, last = counter(clk, 0, oversample-1, 1)
    audio = t_data.register(clk, init=0, en=last)
    audio.d(accumulator - audio)
    audio_stb = Boolean().register(clk, d=last, init=0)

    return adc_out, audio, audio_stb
