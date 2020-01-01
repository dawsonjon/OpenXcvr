from baremetal import *

def max_adc(clk, adc_clk, command_ready, response_valid, response_channel, response_data):

    #
    #channel, command_end_of_packet = counter(clk, 0, 3, 1, en=command_ready)
    #command_start_of_packet = (channel == 3)
    command_channel = Unsigned(5).constant(8)
    command_startofpacket = Boolean().constant(1)
    command_endofpacket = Boolean().constant(1)

    #response interface
    mic = Unsigned(12).register(adc_clk, d=response_data, en=((response_channel==8) & response_valid), init=0)
    stb = Boolean().register(adc_clk, d=((response_channel==8)&response_valid), init=1)#trigger strobe on access to last channel
    response_ready = Boolean().constant(1)

    #move to fast clock domain
    stb = Boolean().register(clk, d=stb, init=0)
    stb = Boolean().register(clk, d=stb, init=0)
    stb = stb & ~Boolean().register(clk, d=stb, init=0)
    mic = Signed(12).register(clk, d=mic-2048, en=stb)
    stb = Boolean().register(clk, d=stb, init=0)

    return command_channel, command_startofpacket, command_endofpacket, mic, stb
