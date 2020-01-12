import sys
from math import pi, sin

from baremetal import *
from af_section import af_section
from rf_section import rf_section
from max10adc import max_adc
from audio_dac import audio_dac
from settings import *
from pcm1802 import pcm1802

def transceiver(clk, rx_i, rx_q, iq_stb, mic, mic_stb, frequency, settings):

    (
        speaker, 
        speaker_stb, 
        tx_i, 
        tx_q, 
        tx_stb, 
        power, 
        capture_i, 
        capture_q, 
        capture_stb,
        overflow
    ) = af_section(
        clk, 
        rx_i, 
        rx_q, 
        iq_stb, 
        mic, 
        mic_stb, 
        settings,
    )
    rf, lo_i, lo_q = rf_section(
        clk, 
        frequency = frequency, 
        audio_i = tx_i,
        audio_q = tx_q,
        audio_stb = tx_stb,
        interpolation_factor = 3000, #from 300000000 to 9180
        lut_bits = 10,
        channels = 2
    )

    return speaker, speaker_stb, rf, lo_i, lo_q, capture_i, capture_q, capture_stb, power, overflow

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
    settings.mode     = Unsigned(2).input("filter_mode_in")
    settings.sideband = Unsigned(2).input("filter_sideband_in")
    settings.rx_tx    = Boolean().input("rx_tx_in")
    settings.gain     = Signed(4).input("gain_in")
    settings.volume   = Signed(6).input("volume_in")
    frequency         = Unsigned(32).input("frequency_in")

    #adc interface inputs
    response_channel  = Unsigned(5).input("response_channel_in")
    response_data     = Unsigned(12).input("response_data_in")
    response_valid    = Unsigned(1).input("response_valid_in")
    command_ready     = Unsigned(1).input("command_ready_in")
    bclk              = Unsigned(1).input("bclk_in")
    lrclk             = Unsigned(1).input("lrclk_in")
    dout              = Unsigned(1).input("dout_in")
    ext_adc           = Unsigned(1).input("ext_adc_in")

    # MAX10 built in ADC
    ####################
    (
        command_channel, 
        command_startofpacket, 
        command_endofpacket, 
        mic, 
        mic_stb, 
        rx_i, 
        rx_q, 
        iq_stb
    ) = max_adc(
        clk, 
        adc_clk, 
        settings.rx_tx,
        command_ready, 
        response_valid, 
        response_channel, 
        response_data
    )


    #external PCM1802 ADC
    #####################
    rx_i, rx_q, iq_stb, sclk, leds = pcm1802(clk, bclk, lrclk, dout)

    # Implement transceiver
    ########################
    speaker, speaker_stb, rf, lo_i, lo_q, capture_i, capture_q, capture_stb, power, overflow = transceiver(
            clk, rx_i, rx_q, iq_stb, mic[11:4], mic_stb, frequency, settings)

    leds = overflow

    # Create Audio DAC
    ##################

    clk = Clock("clk")
    speaker = audio_dac(clk, speaker, speaker_stb) 
    
    #audio capture
    ##############

    #extend stb
    capture_stb = capture_stb | capture_stb.subtype.register(clk, d=capture_stb, init=0)
    capture_stb = speaker_stb | speaker_stb.subtype.register(clk, d=capture_stb, init=0)
    capture_stb = speaker_stb | speaker_stb.subtype.register(clk, d=capture_stb, init=0)
    capture_stb = speaker_stb | speaker_stb.subtype.register(clk, d=capture_stb, init=0)
    capture_i     = capture_i.subtype.register(clk, d=capture_i, en=capture_stb)
    capture_q     = capture_q.subtype.register(clk, d=capture_q, en=capture_stb)
    capture_stb = capture_stb.subtype.register(clk, d=capture_stb, init = 0)

    #edge detect strobe in target clock domain
    capture_stb = Boolean().register(cpu_clk, d=capture_stb, init=0)
    capture_stb = Boolean().register(cpu_clk, d=capture_stb, init=0)
    capture_stb = capture_stb & ~Boolean().register(cpu_clk, d=capture_stb, init=0)
    capture_i = capture_i.subtype.register(cpu_clk, d=capture_i, en=capture_stb)
    capture_q = capture_q.subtype.register(cpu_clk, d=capture_q, en=capture_stb)
    capture_stb = Boolean().register(cpu_clk, d=capture_stb, init=0)
    capture = capture_i[17:2].cat(capture_q[17:2])

    # Create Device Outputs
    #######################

    #ADC interface outputs
    command_channel = command_channel.subtype.output("command_channel_out", command_channel)
    command_startofpacket = command_startofpacket.subtype.output("command_startofpacket_out", command_startofpacket)
    command_endofpacket = command_endofpacket.subtype.output("command_endofpacket_out", command_endofpacket)
    capture = capture.subtype.output("capture_out", capture)
    capture_stb = capture.subtype.output("capture_stb_out", capture_stb)
    power = power.subtype.output("power_out", power)
    sclk = sclk.subtype.output("sclk_out", sclk)
    leds = leds.subtype.output("leds", leds)

    #RF outputs
    rf = [i.subtype.output("rf_%u_out"%idx, i) for idx, i in enumerate(rf)]
    lo_i = [i.subtype.output("lo_i_%u_out"%idx, i) for idx, i in enumerate(lo_i)]
    lo_q = [i.subtype.output("lo_q_%u_out"%idx, i) for idx, i in enumerate(lo_q)]

    #speaker output
    speaker = speaker.subtype.output("speaker_out", speaker)

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
            settings.mode,
            settings.sideband,
            settings.rx_tx,
            settings.gain,
            settings.volume,
            frequency,
            response_channel,
            response_data,
            response_valid,
            command_ready,
            bclk,
            lrclk, 
            dout,
            ext_adc
        ],

        #outputs
        rf + lo_i + lo_q + [
            command_channel,
            command_startofpacket,
            command_endofpacket,
            speaker,
            capture,
            capture_stb,
            sclk,
            leds,
            power,
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



