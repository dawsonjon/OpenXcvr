import sys
from math import pi, sin

from baremetal import *
from af_section import af_section
from rf_section import rf_section
from max10adc import max_adc
from audio_dac import audio_dac
from settings import *
from pcm1802 import pcm1802
from cdc import meta_chain, slow_to_fast
from pps_counter import pps_counter

def transceiver(cpu_clk, clk, rx_i, rx_q, iq_stb, mic, mic_stb, frequency, settings):

    #uncomment this to remove trx for faster synthesis
    #zero = Boolean().constant(0)
    #rf = [zero, zero]
    #lo = [zero, zero]
    #return Unsigned(16).constant(0), Boolean().constant(0), Unsigned(16).constant(0), Boolean().constant(0), rf, lo, lo, Signed(18).constant(0), Signed(18).constant(0), Boolean().constant(0), Boolean().constant(0), Boolean().constant(0)

    (
        speaker, 
        speaker_stb, 
        audio_out,
        audio_out_stb,
        tx_i, 
        tx_q, 
        tx_stb, 
        power, 
        capture_i, 
        capture_q, 
        capture_stb,
        overflow
    ) = af_section(
        cpu_clk, 
        rx_i, 
        rx_q, 
        iq_stb, 
        mic, 
        mic_stb, 
        settings,
    )

    ###########################################################################
    ## Clock Domain Crossing from 50 to 150 MHz                                
    ###########################################################################

    frequency, _ = slow_to_fast(cpu_clk, clk, frequency)
    data_bits = tx_i.subtype.bits
    data, tx_stb = slow_to_fast(cpu_clk, clk, tx_i.cat(tx_q), tx_stb)
    tx_i, tx_q = data[2*data_bits-1:data_bits], data[data_bits-1:0]
    rx_tx = meta_chain(clk, settings.rx_tx)
    enable_test_signal = meta_chain(clk, settings.enable_test_signal)

    ###########################################################################

    rf, lo_i, lo_q = rf_section(
        clk, 
        frequency = frequency, 
        audio_i = tx_i,
        audio_q = tx_q,
        audio_stb = tx_stb,
        interpolation_factor = 3000, #from 300000000 to 9180
        lut_bits = 9,
        channels = 2, 
        rx_tx = rx_tx,
        enable_test_signal = enable_test_signal
    )

    return speaker, speaker_stb, audio_out, audio_out_stb, rf, lo_i, lo_q, capture_i, capture_q, capture_stb, power, overflow

def generate():
    settings = Settings()
    settings.filter_kernel_bits = 18
    settings.agc_frame_size = 65536
    settings.agc_frames = 10
    settings.agc_lut_bits = 7
    settings.agc_lut_fraction_bits = 8

    # Create IP inputs
    ##################

    clk = Clock("clk")
    adc_clk = Clock("adc_clk")
    cpu_clk = Clock("cpu_clk")

    #control settings
    control                     = Unsigned(32).input("control_in")
    settings.mode               = control[2:0]
    settings.rx_tx              = control[3]
    settings.agc_speed          = control[5:4]
    settings.enable_test_signal = control[6]
    settings.volume             = control[13:8]
    usb_audio                   = control[20]
    settings.band               = control[23:21]
    frequency                   = Unsigned(32).input("frequency_in")
    audio_in                    = Signed(8).input("audio_in_in")
    audio_in_stb                = Boolean().input("audio_in_stb_in")

    #adc interface inputs
    response_channel  = Unsigned(5).input("response_channel_in")
    response_data     = Unsigned(12).input("response_data_in")
    response_valid    = Unsigned(1).input("response_valid_in")
    command_ready     = Unsigned(1).input("command_ready_in")
    bclk              = Unsigned(1).input("bclk_in")
    lrclk             = Unsigned(1).input("lrclk_in")
    dout              = Unsigned(1).input("dout_in")

    #GPS interface inputs
    pps              = Unsigned(1).input("pps_in")
    

    # MAX10 built in ADC
    ####################
    (
        command_channel, 
        command_startofpacket, 
        command_endofpacket, 
        mic, 
        mic_stb, 
        adc, 
        adc_stb
    ) = max_adc(
        cpu_clk, 
        adc_clk, 
        command_ready, 
        response_valid, 
        response_channel, 
        response_data
    )


    #external PCM1802 ADC
    #####################

    # Mode Divider  Fs 
    # ==== =====   ====
    #  AM    2     48828
    #  NFM   1     97656
    #  FM    1     97656
    #  LSB   4     24414
    #  USB   4     24414
    #  CW    3     32552

    clock_divide = Unsigned(3).select(settings.mode, 2, 1, 1, 4, 4, 3)
    rx_i, rx_q, iq_stb, sclk = pcm1802(cpu_clk, bclk, lrclk, dout, clock_divide)

    # Implement transceiver
    ########################

    #select usb audio input
    mic = Signed(8).select(usb_audio, mic[11:4], audio_in)
    mic_stb = Signed(8).select(usb_audio, mic_stb, audio_in_stb)
    speaker, speaker_stb, audio_out, audio_out_stb, rf, lo_i, lo_q, capture_i, capture_q, capture_stb, power, overflow = transceiver(
            cpu_clk, clk, rx_i, rx_q, iq_stb, mic, mic_stb, frequency, settings)
    capture = capture_i[17:2].cat(capture_q[17:2])#capture data for debug via CPU

    leds =settings.enable_test_signal.cat(adc_stb.cat(mic_stb))

    # Create Audio DAC
    ##################

    clk = Clock("clk")
    speaker = audio_dac(cpu_clk, speaker, speaker_stb) 
    #speaker = audio_dac(cpu_clk, mic.resize(18)<<6, mic_stb) 
    
    # 1pps counter
    ##############
    pps_count = pps_counter(clk, pps)

    # Create Device Outputs
    #######################

    #ADC interface outputs
    command_channel = command_channel.subtype.output("command_channel_out", command_channel)
    command_startofpacket = command_startofpacket.subtype.output("command_startofpacket_out", command_startofpacket)
    command_endofpacket = command_endofpacket.subtype.output("command_endofpacket_out", command_endofpacket)
    capture = capture.subtype.output("capture_out", capture)
    capture_stb = capture_stb.subtype.output("capture_stb_out", capture_stb)
    power = power.subtype.output("power_out", power)
    sclk = sclk.subtype.output("sclk_out", sclk)
    leds = leds.subtype.output("leds", leds)

    #audio output to CPU
    audio_out = audio_out.subtype.output("audio_out_out", audio_out.resize(32))
    audio_out_stb = audio_out_stb.subtype.output("audio_out_stb_out", audio_out_stb)

    #RF outputs
    rf = [i.subtype.output("rf_%u_out"%idx, i) for idx, i in enumerate(rf)]
    lo_i = [i.subtype.output("lo_i_%u_out"%idx, i) for idx, i in enumerate(lo_i)]
    lo_q = [i.subtype.output("lo_q_%u_out"%idx, i) for idx, i in enumerate(lo_q)]

    #speaker output
    speaker = speaker.subtype.output("speaker_out", speaker)

    #pps counter output
    pps_count = pps_count.subtype.output("pps_count_out", pps_count)

    #adc output
    adc = adc.subtype.output("adc_out", adc)
    adc_stb = adc_stb.subtype.output("adc_stb_out", adc_stb)

    #filter control
    band = settings.band.subtype.output("band", settings.band)
    tx_enable = Boolean().output("tx_enable", settings.rx_tx)

    #generate netlist and output
    netlist = Netlist(
        "transceiver",
        #clocks
        [
            clk, 
            adc_clk,
            cpu_clk
        ], 

        #inputs
        [
            audio_in,
            audio_in_stb,
            control,
            frequency,
            response_channel,
            response_data,
            response_valid,
            command_ready,
            bclk,
            lrclk, 
            dout,
            pps,
        ],

        #outputs
        rf + lo_i + lo_q + [
            command_channel,
            command_startofpacket,
            command_endofpacket,
            speaker,
            audio_out,
            audio_out_stb,
            capture,
            capture_stb,
            sclk,
            leds,
            power,
            pps_count,
            adc,
            adc_stb,
            band,
            tx_enable
        ]
    )
    f = open("transceiver.v", "w")
    f.write(netlist.generate())

if __name__ == "__main__":

    if "sim" in sys.argv:
        import numpy as np
        from matplotlib import pyplot as plt
        monitor = Monitor(debug)
        clk.initialise()
        response = []
        frequency.set(0x00000000)
        for i in range(256*1500*2):
            clk.tick()
            monitor.monitor()
            for channel in rf:
                print(tx_audio.get(), tx_i.get(), tx_q.get(), channel.get())
                if channel.get():
                    response.append(channel.get()-0.5)

        #response = response-np.mean(response)
        spectrum = np.abs(np.fft.fftshift(np.fft.fft(response)))
        #spectrum = 20.0 * np.log10(spectrum, out=np.zeros_like(spectrum), where=(spectrum!=0))
        plt.plot(spectrum)
        plt.show()

    if "gen" in sys.argv:
        generate()



