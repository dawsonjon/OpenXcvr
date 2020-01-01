import sys
from math import pi, sin

from baremetal import *
from transceiver import transceiver
from tx import tx
from settings import *

settings = Settings()
settings.filter_kernel_bits = 18
settings.agc_frame_size = 800
settings.agc_frames = 2
settings.agc_lut_bits = 7
settings.agc_lut_fraction_bits = 8

#settings.squelch = Signed(16).input("squelch")
settings.mode = Unsigned(2).input("filter_mode_in")
settings.sideband = Unsigned(2).input("filter_sideband_in")
#settings.rx_tx = Boolean().input("rx_tx")
settings.squelch = Signed(16).constant(0)
#settings.mode = Unsigned(2).constant(AM)
#settings.sideband = Boolean().constant(USB)
settings.rx_tx = Boolean().constant(1)
    

clk = Clock("clk")
#rx_i_in = Signed(16).input("i_data_in")
#rx_q_in = Signed(16).input("q_data_in")
#rx_stb_in = Boolean().input("stb_in")
rx_i_in = Signed(16).constant(0)
rx_q_in = Signed(16).constant(0)
rx_stb_in = Boolean().constant(0)

tx_audio_in = Signed(8).input("tx_audio_in")
tx_audio_stb_in = Boolean().input("tx_audio_stb_in")

#generate audio sample rate
#100e3/150e6
#_, tx_audio_stb = counter(clk, 0, 1499, 1)

#test signal generator
#test_frequency = 1.0e3 #1kHz
#audio_sample_rate = 100.0e3 #1KHz
#test_frequency = (2**8)*(test_frequency/audio_sample_rate)
#phase = Unsigned(8).register(clk, init=0, en=tx_audio_stb)
#phase.d(phase + test_frequency)
#tx_audio_stb = Boolean().register(clk, d=tx_audio_stb, init=0)
#lut_depth = 256
#scaling_factor = 127
#sin_lookup_table = [sin(2.0*pi*i/lut_depth) for i in range(lut_depth)]
#sin_lookup_table = [int(round(i*scaling_factor)) for i in sin_lookup_table]
#tx_audio = Signed(8).rom(phase, *sin_lookup_table)
#tx_audio = tx_audio.subtype.register(clk, d=tx_audio)
#tx_audio_stb = Boolean().register(clk, d=tx_audio_stb, init=0)
#tx_audio = tx_audio.subtype.register(clk, d=tx_audio)
#tx_audio_stb = Boolean().register(clk, d=tx_audio_stb, init=0)
#tx_audio = tx_audio.label("tx_audio")
#tx_audio_stb = tx_audio_stb.label("tx_audio_stb")

frequency = Unsigned(32).input("frequency")
debug = {}
rx_audio, rx_audio_stb, tx_i, tx_q, tx_stb = transceiver(
    clk, 
    rx_i_in, 
    rx_q_in, 
    rx_stb_in, 
    tx_audio_in, 
    tx_audio_stb_in, 
    settings,
    debug
)

tx_i = tx_i.label("tx_i")
tx_q = tx_q.label("tx_q")
tx_stb = tx_stb.label("tx_stb")

rf, lo_i, lo_q = tx(
    clk, 
    frequency = frequency, 
    audio_i = tx_i,
    audio_q = tx_q,
    audio_stb = tx_stb,
    interpolation_factor = 3000, #from 300000000 to 9180
    lut_bits = 10,
    channels = 2
)

class Monitor:
    def __init__(self, probe_points):
        self.probe_points = probe_points
        self.capture = {}

    def monitor(self):
        for name, probe in self.probe_points.iteritems():
            if name in self.capture:
                self.capture[name].append(probe.get())
            else:
                self.capture[name] = [probe.get()]

    def plot(self):
        for name, data in self.capture:
            plt.plot(data)
        plt.show()


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
        rf = [i.subtype.output("rf_%u"%idx, i) for idx, i in enumerate(rf)]
        lo_i = [i.subtype.output("lo_i_%u"%idx, i) for idx, i in enumerate(lo_i)]
        lo_q = [i.subtype.output("lo_q_%u"%idx, i) for idx, i in enumerate(lo_q)]
        netlist = Netlist(
            "transceiver",
            [clk], 
            [frequency, tx_audio_in, tx_audio_stb_in, settings.mode, settings.sideband],
            rf + lo_i + lo_q,
        )
        f = open("transceiver.v", "w")
        f.write(netlist.generate())
