from baremetal import *
from audio_adc import audio_adc
from audio_dac import audio_dac

clk = Clock("clk")
adc_in = Boolean().input("adc_in")

adc_out, audio, audio_stb = audio_adc(clk, adc_in, 1500)
dac_out = audio_dac(clk, audio, audio_stb)

adc_out.subtype.output("adc_out", adc_out)
dac_out.subtype.output("dac_out", dac_out)

netlist = Netlist(
    "audio_test",
    [clk], 
    [adc_in],
    [adc_out, dac_out],
)
f = open("audio_test.v", "w")
f.write(netlist.generate())
