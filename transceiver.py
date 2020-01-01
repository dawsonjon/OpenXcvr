from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from audio_agc import audio_agc
from filter import filter
from demodulator import demodulator
from modulator import modulator
from settings import *

def transceiver(clk, rx_i, rx_q, rx_stb, tx_audio, tx_audio_stb, settings, debug={}):


    tx_bits = tx_audio.subtype.bits
    t_rx = rx_i.subtype

    #declare signals
    modulator_out_i = Signed(tx_bits+1).wire()
    modulator_out_q = Signed(tx_bits+1).wire()
    modulator_out_stb = Boolean().wire()

    #filter
    filter_in_i = t_rx.select(settings.rx_tx, rx_i, modulator_out_i)
    filter_in_q = t_rx.select(settings.rx_tx, rx_q, modulator_out_q)
    filter_in_stb = Boolean().select(settings.rx_tx, rx_stb, modulator_out_stb)
    filter_out_i, filter_out_q, filter_out_stb = filter(clk, filter_in_i, filter_in_q, filter_in_stb, settings)

    filter_out_i = filter_out_i.label("filter_out_i")
    filter_out_q = filter_out_q.label("filter_out_q")
    filter_out_stb = filter_out_stb.label("filter_out_stb")

    #demodulator
    demodulator_out, demodulator_out_stb = demodulator(clk, filter_out_i, filter_out_q, filter_out_stb, settings)

    #agc
    agc_in = t_rx.select(settings.rx_tx, demodulator_out, tx_audio)
    agc_in_stb = t_rx.select(settings.rx_tx, demodulator_out_stb, tx_audio_stb)
    agc_out, agc_out_stb = audio_agc(clk, agc_in, agc_in_stb, settings)

    #modulator
    #i, q, stb = modulator(clk, agc_out.resize(tx_bits), agc_out_stb, settings)
    i, q, stb = modulator(clk, tx_audio, tx_audio_stb, settings)
    modulator_out_i.drive(i)
    modulator_out_q.drive(q)
    modulator_out_stb.drive(stb)


    #rx audio
    rx_audio = agc_out
    rx_audio_stb = agc_out_stb

    #resize tx

    tx_i = filter_out_i.resize(tx_bits)
    tx_q = filter_out_q.resize(tx_bits)
    tx_stb = filter_out_stb

    debug["audio"] = tx_audio
    debug["audio_stb"] = tx_audio_stb
    debug["modulator_out_i"] = modulator_out_i
    debug["modulator_out_q"] = modulator_out_q
    debug["modulator_out_stb"] = modulator_out_stb
    debug["filter_out_i"] = filter_out_i
    debug["filter_out_q"] = filter_out_q
    debug["filter_out_stb"] = filter_out_stb

    return rx_audio, rx_audio_stb, tx_i, tx_q, tx_stb

def test_transceiver(stimulus, sideband, mode, rx_tx):
    settings = Settings()
    settings.filter_kernel_bits = 18
    settings.agc_frame_size = 800
    settings.agc_frames = 2
    settings.agc_lut_bits = 7
    settings.agc_lut_fraction_bits = 8
    settings.squelch = Signed(16).input("squelch")
    settings.mode = Unsigned(2).input("filter_mode")
    settings.sideband = Unsigned(2).input("filter_sideband")
    settings.rx_tx = Boolean().input("rx_tx")
    

    taps = 255
    clk = Clock("clk")
    rx_i_in = Signed(16).input("i_data_in")
    rx_q_in = Signed(16).input("q_data_in")
    rx_stb_in = Boolean().input("stb_in")
    tx_audio_in = Signed(8).input("tx_audio_in")
    tx_audio_stb_in = Boolean().input("stb_in")

    rx_audio, rx_audio_stb, tx_i, tx_q, tx_stb = transceiver(clk, rx_i_in, rx_q_in, rx_stb_in, tx_audio_in, tx_audio_stb_in, settings) 

    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.show()

    #simulate
    clk.initialise()
    settings.squelch.set(0)
    settings.rx_tx.set(rx_tx)
    settings.mode.set(mode)
    settings.sideband.set(sideband)

    tx_audio_in.set(0)
    tx_audio_stb_in.set(0)

    response = []
    for data in stimulus:
        for j in range(taps+2):
            rx_stb_in.set(j==taps+1)
            rx_i_in.set(np.real(data))
            rx_q_in.set(np.imag(data))
            tx_audio_in.set(np.real(data))
            tx_audio_stb_in.set(j==taps+1)
            clk.tick()
            if rx_audio_stb.get() and rx_tx==0:
                print rx_audio.get()
                response.append(rx_audio.get())
            if tx_stb.get() and rx_tx==1:
                print tx_i.get(), tx_q.get()
                if tx_i.get() is not None and tx_q.get() is not None:
                    response.append(tx_i.get()+1j*tx_q.get())

    response = np.array(response)
    #plt.plot(np.real(stimulus))
    #plt.plot(np.imag(stimulus))
    plt.plot(np.real(response))
    plt.plot(np.imag(response))
    plt.show()
    plt.plot(20*np.log10(abs(np.fft.fftshift(np.fft.fft(response)))))
    plt.show()


if __name__ == "__main__" and "sim" in sys.argv:

    #TX
    ##############################################

    #mode am stim tx
    stimulus=(
        np.sin(np.arange(1000)*2.0*pi*0.01)*
        ((2**7)-1)#scale to 16 bits
    )
    #test_transceiver(stimulus, USB, AM, 1)#lsb AM

    #mode SSB stim tx
    stimulus=(
        np.sin(np.arange(1000)*2.0*pi*0.01)*
        ((2**7)-1)#scale to 16 bits
    )
    test_transceiver(stimulus, USB, SSB, 1)#lsb AM

    #mode nfm
    stimulus=(
        np.sin(np.arange(1000)*2.0*pi*0.01)*
        ((2**7)-1)#scale to 16 bits
    )
    test_transceiver(stimulus, USB, NBFM, 1)#usb NBFM

    #RX
    ###############################################

    #mode am stim am
    stimulus=(
        np.exp(1j*np.arange(4000)*2.0*pi*0.0005)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
        (np.sin(np.arange(4000)*2.0*pi*0.01)*0.5+0.5)* #The signal a tone
        ((2**15)-1)#scale to 16 bits
    )
    test_transceiver(stimulus, 0, 1)#lsb AM

    #mode usb stim dsb
    stimulus=(
        np.sin(np.arange(4000)*2.0*pi*0.01)*
        ((2**15)-1)#scale to 16 bits
    )
    test_transceiver(stimulus, 1, 0)#usb SSB

    #mode fm
    audio=np.sin(np.arange(4000)*2.0*pi*0.01)
    frequency = audio * 0.05 * pi#0.1*+/-50kHZ = +/-5KHz
    phase = np.cumsum(frequency)
    stimulus = (
        np.exp(1.0j*phase)*
        ((2**15)-1)#scale to 16 bits
    )
    test_transceiver(stimulus, 1, 2)#usb FM
