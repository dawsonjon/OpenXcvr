from baremetal import *
from cordic import rectangular_to_polar
import numpy as np

def demodulator(clk, i, q, stb, settings):
    stb = Boolean().register(clk, d=stb, init=0)
    i = i.subtype.register(clk, d=i, init=0)
    q = q.subtype.register(clk, d=q, init=0)

    #AM/FM demodulator
    magnitude, phase, magnitude_phase_stb = rectangular_to_polar(clk, i, q, stb)
    am  = magnitude.subtype.register(clk, d=magnitude, en=magnitude_phase_stb)
    last_phase=phase.subtype.register(clk, d=phase, en=magnitude_phase_stb)
    fm  = phase.subtype.register(clk, d=phase-last_phase, en=magnitude_phase_stb)
    am_fm_stb = Boolean().register(clk, d=magnitude_phase_stb, init=0)

    #Add/Subtract Fs/4 ~1.5kHz
    quadrant, last = counter(clk, 0, 3, 1, en=stb)
    usb     = i.subtype.select(quadrant, q, i, -q, -i)
    usb     = i.subtype.register(clk, d=usb, en=stb)
    lsb     = i.subtype.select(quadrant, q, -i, -q, i)
    lsb     = i.subtype.register(clk, d=lsb, en=stb)
    ssb_stb = Boolean().register(clk, d=stb, init=0)

    #CW demodulator (side tone)
    #Add Fs/8 ~ 750Hz to the frequency
    #We discard the imaginary part so we can use i*sin(theta) + q*cos(theta)
    i_stb = stb
    q_stb = Boolean().register(clk, d=i_stb, init=0)
    theta, _ = counter(clk, 0, 7, 1, en=q_stb)
    scaling_factor = (2**(i.subtype.bits - 1))-1
    cos_lookup_table = np.round(scaling_factor*np.cos(2*np.pi*np.arange(8)/8.0))

    #use one multiplier and one ROM to calculate i*sin(theta) and q*cos(theta) in alternate cycles
    theta = theta.subtype.select(i_stb, theta, theta-2) #toggle between sin and cosine
    k   = i.subtype.rom(theta, *cos_lookup_table)
    i_q = i.subtype.select(i_stb, q, i).resize(i.subtype.bits*2-1) * k >> i.subtype.bits - 1
    cw = i.subtype.register(clk, init=0)
    cw.d(i.subtype.select(i_stb, cw+i_q, i_q))
    cw_stb = stb.subtype.register(clk, d=q_stb, init=0)

    audio     = i.subtype.select(settings.mode, am,        fm,        fm,        lsb,     usb,     cw)
    audio_stb = Boolean().select(settings.mode, am_fm_stb, am_fm_stb, am_fm_stb, ssb_stb, ssb_stb, cw_stb)

    return audio, audio_stb

import sys
import numpy as np
from math import pi
from matplotlib import pyplot as plt
from settings import CW
if __name__ == "__main__" and "sim" in sys.argv:
    class Settings:
        pass
    settings = Settings()
    settings.mode = Unsigned(3).input("mode")
    rx_i_in = Signed(16).input("i_data_in")
    rx_q_in = Signed(16).input("q_data_in")
    rx_stb_in = Boolean().input("stb_in")
    clk = Clock("clk")

    rx_out, rx_stb = demodulator(clk, rx_i_in, rx_q_in, rx_stb_in, settings) 

    #mode am stim tx
    stimulus=(
        np.exp(1.0j*np.arange(1000)*2.0*pi*0.03)*
        ((2**15)-1)#scale to 16 bits
    )

    #simulate
    clk.initialise()
    settings.mode.set(CW)

    response  = []
    for data in stimulus:
        for j in range(10):
            rx_stb_in.set(j==9)
            rx_i_in.set(np.real(data))
            rx_q_in.set(np.imag(data))
            clk.tick()
            if rx_stb.get():
                print rx_out.get()/(2.0**15)
                response.append(rx_out.get()/(2.0**15))

    response = np.array(response)

    #response = np.array(response)
    #plt.plot(np.real(stimulus))
    #plt.plot(np.imag(stimulus))
    plt.plot(response)
    plt.show()
    plt.plot(abs(np.fft.fftshift(np.fft.fft(response))))
    plt.show()
