from baremetal import *
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from audio_agc import audio_agc
from dc_removal import dc_removal
from filter import filter
from demodulator import demodulator
from modulator import modulator
from downconverter import downconverter
from measure_magnitude import measure_magnitude
from test_signal import test_signal
from clamp import clamp
from mic_compression import mic_compression
from decimate import decimate
from audio_filter import audio_filter
from settings import *

def af_section(clk, rx_i, rx_q, rx_stb, tx_audio, tx_audio_stb, settings, debug={}):


    # Receiver
    # ========

    #          +-------------+ +--------+ +-------------+ +-------+
    #RX I/Q----+ Fs/4        +-+ filter +-+ demodulator +-+ Audio +-- Speaker  
    #          | Downconvert | +--------+ +-------------+ | AGC   |                
    #          +-------------+                            +-------+

    # Downconvert by fs/4
    # ===================
    #
    # NCO is tuned fs/4 below wanted signal, so wanted signal appears as Fs/4
    # Fs/4 downconverter is a special case downconverter that doesn't need any 
    # multipliers.
    #                        
    #                                ____
    #                               /    \
    # ____________________________ /      \_______
    #                        
    # |----------|----------|----------|----------|
    # -fs/2    -fs/4        DC        fs/4      fs/2

    capture_i, capture_q, capture_stb = rx_i, rx_q, rx_stb
    rx_i, rx_q, rx_stb = downconverter(clk, rx_i, rx_q, rx_stb)

    # Filter
    # ======
    #
    # PCM 1802 ADC includes antialiasing/oversampling/decimation and works
    # over a wide frequency range. Using variable sample rate in the ADC,
    # combined with a couple of selectable filter kernels allows a range of
    # effective bandwidths to be realised.
    #
    # MODE      Fs kHz  Filter 
    #                   Bandwidth
    # ====      ======  ==========
    # AM        24.4      Fs/4           ~+/-3
    # NFM       39.0      Fs/4           ~+/-5
    # FM        65.2      Fs/4           ~+/-8
    # USB       24.4      Fs/8           ~+/-1.5
    # LSB       24.4      Fs/8           ~+/-1.5
    # CW        24.4      Fs/80          ~+/-0.15 (300Hz)
    # 
    # In all cases symmetrical filters are used. This means that the real and
    # imaginary parts of the filter kernel are the same, reducing filter
    # complexity. 
    #
    # For SSB signals, half of the filter bandwidth is either 
    # added or subtracted from the NCO. So for USB an audio signal at DC now
    # appears as -1.5kHz, 1.5KHz appears as DC and 3kHz appears as +1.5kHz.
    # This is corrected in the demodulator which either adds or subtracts 1.5kHz
    # to compensate. 
    #                        
    # For CW signals, the tone should appear at the centre of the filter pass
    # band, so appears as DC. Again, the frequency can be corrected in the demodulator
    # to add a side tone frequency.
    #                      ____
    #                     /    \
    # __________________ /      \__________________
    #                        
    # |----------|----------|----------|----------|
    # -fs/2    -fs/4        DC        fs/4      fs/2

    rx_i, rx_q, rx_stb = filter(clk, rx_i, rx_q, rx_stb, settings)

    # decimate
    # ========
    #
    # Now that the filter has removed at least 3/4 of the spectrum, we might as well
    # reduce the sampling rate by a factor of 4.
    #      ___________________________________
    #     /                                   \
    # ___/                                     \___
    #                        
    # |----------|----------|----------|----------|
    # -fs/2    -fs/4        DC        fs/4      fs/2

    rx_i, rx_q, rx_stb = decimate(clk, rx_i, rx_q, rx_stb, 4)

    # power measurement
    # =================
    #
    # The power measurement is used to generate the s-meter, and squelch function.
    # The power measurement is made after filter, so that close-by, but out of band signals
    # don't distort measurement.
    #
    # The measurement uses a much faster decay than the AGC, so that squelch can respond
    # rapidly.
    power = measure_magnitude(clk, rx_i, rx_stb, 0) #fast

    # demodulator
    # ===========
    #
    # AM/FM
    # --
    # 
    # The rectangular I/Q representation is converted to a phase and magnitude
    # representation using CORDIC. For AM, the magnitude is used as the audio output.
    # For FM, the phase difference (frequency) from one sample to the next is used as
    # the audio output.
    
    rx, rx_stb = demodulator(clk, rx_i, rx_q, rx_stb, settings)
    #capture_i, capture_q, capture_stb = rx, rx.subtype.constant(0), rx_stb

    # DC removal
    # ==========
    #
    # The output of the demodulator will contain a DC component, in AM mode this is because
    # the amplitude is derived from the magnitude which is never negative. In FM mode, a slight
    # miss-tuning will result in a DC offset. This is removed using a DC filter.

    rx, rx_stb = dc_removal(clk, rx, rx_stb)

    # Automatic Gain Control
    # ======================
    #
    # The amplitude of the demodulated signal will vary. In the case of AM, CW, and SSB signals
    # is is dependent on the received signal strength so will vary enormously. For FM signals 
    # there will be some variation in frequency deviation.

    rx, rx_stb, rx_USB, rx_USB_stb, overflow = audio_agc(clk, rx, rx_stb, settings.volume, settings.agc_speed)

    # output to speaker
    # =================
    #
    # Blank audio output during transmit.
    rx = rx.subtype.select(settings.rx_tx, rx, 0)
    rx_USB = rx_USB.subtype.select(settings.rx_tx, rx_USB, 0)

    # Transmitter
    # ===========

    #          +-----------+ +---------+ +-------------+ +--------+ 
    #TX Audio -+ DC        +-+ Audio   +-+ Modulator   +-+ filter +-- Audio Out
    #          | removal   | | AGC     | +-------------+ +--------+                
    #          +-----------+ +---------+


    #Microphone gain
    #===============
    #microphone gain is user programmable
    tx_bits = tx_audio.subtype.bits
    gain = Signed(5).constant(0)+settings.mic_gain
    tx_audio = tx_audio.resize(tx_bits+16) << gain
    tx_audio = tx_audio.subtype.register(clk, d=tx_audio)
    tx_audio_stb = tx_audio_stb.subtype.register(clk, d=tx_audio_stb)
    tx_audio, tx_audio_stb  = clamp(clk, tx_audio, tx_audio_stb, tx_bits)
    #tx_audio, mic_compression(clk, tx_audio, tx_audio_stb)

    #audio filter
    #============
    tx_audio, tx_audio_stb = audio_filter(clk, tx_audio, tx_audio_stb)

    #modulator
    #=========
    tx_mag, tx_phase, tx_stb = modulator(clk, tx_audio, tx_audio_stb, settings)

    #output to transmitter
    #=====================

    #Don't modulate the LO when receiving!!
    tx_mag = tx_mag.subtype.select(settings.rx_tx, tx_mag.subtype.constant(0), tx_mag)
    tx_phase = tx_phase.subtype.select(settings.rx_tx, tx_phase.subtype.constant(0), tx_phase)

    return rx, rx_stb, rx_USB, rx_USB_stb, tx_mag, tx_phase, tx_stb, power, capture_i, capture_q, capture_stb, overflow

def test_transceiver(stimulus, mode, rx_tx):
    settings = Settings()
    settings.filter_kernel_bits = 18
    settings.agc_frame_size = 800
    settings.agc_frames = 2
    settings.agc_lut_bits = 7
    settings.agc_lut_fraction_bits = 8
    settings.squelch = Signed(16).input("squelch")
    settings.mode = Unsigned(3).input("mode")
    settings.rx_tx = Boolean().input("rx_tx")
    settings.volume = Signed(4).constant(0)
    settings.agc_speed = Signed(4).constant(0)
    

    taps = 255
    clk = Clock("clk")
    rx_i_in = Signed(18).input("i_data_in")
    rx_q_in = Signed(18).input("q_data_in")
    rx_stb_in = Boolean().input("stb_in")
    tx_audio_in = Signed(8).input("tx_audio_in")
    tx_audio_stb_in = Boolean().input("stb_in")

    rx_audio, rx_audio_stb, _, _, tx_i, tx_q, tx_stb, _, capture_i, capture_q, capture_stb, _ = af_section(clk, rx_i_in, rx_q_in, rx_stb_in, tx_audio_in, tx_audio_stb_in, settings) 

    plt.plot(np.real(stimulus))
    plt.plot(np.imag(stimulus))
    plt.show()
    plt.plot(abs(np.fft.fftshift(np.fft.fft(stimulus))))
    plt.show()

    #simulate
    clk.initialise()
    settings.squelch.set(0)
    settings.rx_tx.set(rx_tx)
    settings.mode.set(mode)

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
            if capture_stb.get() and rx_tx==0:
                print capture_i.get(), capture_q.get()
                if capture_i.get() is not None and capture_q.get() is not None:
                    response.append(capture_i.get()+1j*capture_q.get())
            if tx_stb.get() and rx_tx==1:
                print tx_i.get(), tx_q.get()
                if tx_i.get() is not None and tx_q.get() is not None:
                    response.append(tx_i.get()+1j*tx_q.get())

    response = np.array(response)
    #plt.plot(np.real(stimulus))
    #plt.plot(np.imag(stimulus))
    plt.plot(np.real(response), 'r.')
    plt.plot(np.imag(response), 'g.')
    #plt.plot(np.abs(response))
    plt.show()
    plt.plot(abs(np.fft.fftshift(np.fft.fft(response))))
    plt.show()


if __name__ == "__main__" and "sim" in sys.argv:

    #TX
    ##############################################

    #mode am stim tx
    #stimulus=(
    #    np.sin(np.arange(1000)*2.0*pi*0.01)*
    #    ((2**7)-1)#scale to 16 bits
    #)
    #stimulus=(
        #((np.sin(np.arange(1000)*2.0*pi*0.01)>0)-0.5)*127*2
    #)
    #test_transceiver(stimulus, USB, AM, 1)#lsb AM

    #mode SSB stim tx
    #stimulus=(
    #   ((np.sin(np.arange(1000)*2.0*pi*0.01)>0)-0.5)*127*2
    #)
    #stimulus=(
        #np.sin(np.arange(1000)*2.0*pi*0.01)*
        #((2**7)-1)#scale to 16 bits
    #)
    #test_transceiver(stimulus, USB, SSB, 1)#lsb AM

    #mode nfm
    #stimulus=(
        #np.sin(np.arange(1000)*2.0*pi*0.01)*
        #((2**7)-1)#scale to 16 bits
    #)
    #test_transceiver(stimulus, USB, NBFM, 1)#usb NBFM

    #RX
    ###############################################

    #mode am stim am
    #stimulus=(
        #np.exp(1j*np.arange(400)*2.0*pi*+0.25)* #lo tuned to -Fs/4
        ##np.exp(1j*np.arange(400)*2.0*pi*0.005)* #represents the effect of a slight mis-tuning so that the power circulates between +ve and -ve in i and q channels
        #(np.sin(np.arange(400)*2.0*pi*0.05)*0.5+0.5)* #The signal a tone + DC
        #((2**15)-1)#scale to 16 bits
    #)
    #test_transceiver(stimulus, AM, 0)#lsb AM

    #mode usb stim usb
    stimulus=(
        np.exp(1j*np.arange(2000)*2.0*pi*0.1875)* #lo tuned to -Fs/4 + 0.5*ssb bandwidth
        (
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.01)+ #The signal a tone ~1kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.03)+ #The signal a tone ~1kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.05)+ #The signal a tone ~2kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.07)+ #The signal a tone ~2kHz should come out slightly above DC
            0.3*np.exp(-1j*np.arange(2000)*2.0*pi*0.09)+ #The signal a tone ~2kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.11)+ #The signal a tone ~3kHz should come out slightly above DC
            0.1*np.exp(1j*np.arange(2000)*2.0*pi*0.02)+ #The signal a tone ~1kHz should come out slightly above DC
            0.2*np.exp(1j*np.arange(2000)*2.0*pi*0.04)+ #The signal a tone ~2kHz should come out slightly above DC
            0.3*np.exp(1j*np.arange(2000)*2.0*pi*0.06)+ #The signal a tone ~2kHz should come out slightly above DC
            0.4*np.exp(1j*np.arange(2000)*2.0*pi*0.08)+ #The signal a tone ~2kHz should come out slightly above DC
            0.5*np.exp(1j*np.arange(2000)*2.0*pi*0.10)
        )* ((2**15)-1)#scale to 16 bits
    )

    #test_transceiver(stimulus, USB, 0)

    stimulus=(
        np.exp(1j*np.arange(2000)*2.0*pi*0.3125)* #lo tuned to -Fs/4 + 0.5*ssb bandwidth
        (
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.01)+ #The signal a tone ~1kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.03)+ #The signal a tone ~1kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.05)+ #The signal a tone ~2kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.07)+ #The signal a tone ~2kHz should come out slightly above DC
            0.3*np.exp(-1j*np.arange(2000)*2.0*pi*0.09)+ #The signal a tone ~2kHz should come out slightly above DC
            0.2*np.exp(-1j*np.arange(2000)*2.0*pi*0.11)+ #The signal a tone ~3kHz should come out slightly above DC
            0.1*np.exp(1j*np.arange(2000)*2.0*pi*0.02)+ #The signal a tone ~1kHz should come out slightly above DC
            0.2*np.exp(1j*np.arange(2000)*2.0*pi*0.04)+ #The signal a tone ~2kHz should come out slightly above DC
            0.3*np.exp(1j*np.arange(2000)*2.0*pi*0.06)+ #The signal a tone ~2kHz should come out slightly above DC
            0.4*np.exp(1j*np.arange(2000)*2.0*pi*0.08)+ #The signal a tone ~2kHz should come out slightly above DC
            0.5*np.exp(1j*np.arange(2000)*2.0*pi*0.10)
        )* ((2**15)-1)#scale to 16 bits
    )
    #test_transceiver(stimulus, LSB, 0)

    stimulus=(
        np.exp(1j*np.arange(2000)*2.0*pi*0.25)* #lo tuned to -Fs/4 + 0.5*ssb bandwidth
        ((2**15)-1)#scale to 16 bits
    )
    test_transceiver(stimulus, CW, 0)

    #mode usb stim dsb
    #stimulus=(
        #np.sin(np.arange(4000)*2.0*pi*0.01)*
        #((2**15)-1)#scale to 16 bits
    #)
    #test_transceiver(stimulus, 1, 0)#usb SSB

    #mode fm
    #audio=np.sin(np.arange(4000)*2.0*pi*0.01)
    #frequency = audio * 0.05 * pi#0.1*+/-50kHZ = +/-5KHz
    #phase = np.cumsum(frequency)
    #stimulus = (
        #np.exp(1.0j*phase)*
        #((2**15)-1)#scale to 16 bits
    #)
    #test_transceiver(stimulus, 1, 2)#usb FM
