from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from dither import dither
from nco import nco
from prng import prng
from math import sin
from random import randint
from tx_modulator import test_modulator

def rf_section(clk, frequency, audio_i, audio_q, audio_stb, interpolation_factor, lut_bits, channels, rx_tx, enable_test_signal):

    #create nco
    dlo_i, dlo_q = nco(clk, frequency, channels)
    lo_i = [(i > int(round((2**32)*0.5))) for i in dlo_i]
    lo_q = [(i > int(round((2**32)*0.5))) for i in dlo_q]
    lo_i = [i.subtype.register(clk, d=i) for i in lo_i]
    lo_q = [i.subtype.register(clk, d=i) for i in lo_q]

    #this is where the audio gets modulated into PWM waveform
    #at the moment use a PWM modulated 1kHz sin
    _, _, rf = test_modulator(clk, 1000)

    return [rf, rf], lo_i, lo_q
