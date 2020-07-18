from baremetal import *
from baremetal.signed import number_of_bits_needed
from interpolate import interpolate
from dither import dither
from nco import nco
from prng import prng
from math import sin
from random import randint
from tx_modulator import pwm_modulator

def rf_section(clk, frequency, audio_mag, audio_phase, audio_stb, interpolation_factor, lut_bits, channels, rx_tx, enable_test_signal):

    #modulate the phase in TX, but not in RX
    phase = audio_phase#audio_phase.subtype.select(rx_tx, 0, audio_phase)

    #create nco
    dlo_i, dlo_q = nco(clk, frequency, phase, channels)
    lo_i = [(i > int(round((2**32)*0.5))) for i in dlo_i]
    lo_q = [(i > int(round((2**32)*0.5))) for i in dlo_q]
    lo_i = [i.subtype.register(clk, d=i) for i in lo_i]
    lo_q = [i.subtype.register(clk, d=i) for i in lo_q]

    #generate pwm output to control amplifier envelope
    _, _, rf = pwm_modulator(clk, audio_mag, 4)

    return [rf, rf], lo_i, lo_q
