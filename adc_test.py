from baremetal import *
from audio_dac import audio_dac
from max10adc import max_adc

clk = Clock("clk")
adc_clk = Clock("adc_clk")

response_channel = Unsigned(5).input("response_channel")
response_data = Unsigned(12).input("response_data")
response_valid = Unsigned(1).input("response_valid")
command_ready = Unsigned(1).input("command_ready")

#instance controller for max10ADC
(
    command_channel, 
    command_startofpacket, 
    command_endofpacket, 
    mic, 
    stb
) = max_adc(
    clk, 
    adc_clk, 
    command_ready, 
    response_valid, 
    response_channel, 
    response_data
)

command_channel = command_channel.subtype.output("command_channel", command_channel)
command_startofpacket = command_startofpacket.subtype.output("command_startofpacket", command_startofpacket)
command_endofpacket = command_endofpacket.subtype.output("command_endofpacket", command_endofpacket)
command_endofpacket = command_endofpacket.subtype.output("command_endofpacket", command_endofpacket)
tx_audio = mic.subtype.output("tx_audio", mic)
tx_audio_stb = Boolean().output("tx_audio_stb", stb)


netlist = Netlist(
    "adc_test",
    [adc_clk, clk], 
    [response_channel, response_data, response_valid, command_ready],
    [command_channel, command_startofpacket, command_endofpacket, tx_audio, tx_audio_stb],
)
f = open("adc_test.v", "w")
f.write(netlist.generate())
