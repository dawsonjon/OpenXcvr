from baremetal import *
from cordic import rectangular_to_polar

def demodulator(clk, i, q, stb, settings):
    magnitude, phase, magnitude_phase_stb = rectangular_to_polar(clk, i, q, stb)

    am  = magnitude.subtype.register(clk, d=magnitude, en=magnitude_phase_stb)
    last_phase=phase.subtype.register(clk, d=phase, en=magnitude_phase_stb)
    fm  = phase.subtype.register(clk, d=phase-last_phase, en=magnitude_phase_stb)
    am_fm_stb = Boolean().register(clk, d=magnitude_phase_stb, init=0)
    ssb  = i.subtype.register(clk, d=i, en=stb)
    ssb_stb = Boolean().register(clk, d=stb, init=0)

    audio     = i.subtype.select(settings.mode, ssb, am, fm, fm)
    audio_stb = Boolean().select(settings.mode, ssb_stb, am_fm_stb, am_fm_stb, am_fm_stb)

    return audio, audio_stb
