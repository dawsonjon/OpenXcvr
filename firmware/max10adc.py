from baremetal import *
from cdc import slow_to_fast, slow_to_fast2

def max_adc(clk, adc_clk, command_ready, response_valid, response_channel, response_data):


    #reading 10 channels at 500KHz means that each channel gets sampled at 50KHz
    #channel sequence 8, 2, 5, 1, 3
    #8 = mic
    #2 = battery voltage
    #5 = fwd power
    #1 = rev power
    #3 = ptt
    #7 = dit
    #4 = dah
    idx, command_endofpacket = counter(adc_clk, 0, 9, 1, en=command_ready)
    command_startofpacket = (idx==0)
    command_channel = Unsigned(5).select(idx, 8, 2, 5, 1, 3, 7, 4, 2, 2, 2)

    #response interface
    mic = Unsigned(12).register(adc_clk, d=response_data, en=((response_channel==8) & response_valid), init=0)
    mic_stb = Boolean().register(adc_clk, d=((response_channel==8)&response_valid), init=0)

    #convert mic to signed
    mic = Signed(mic.subtype.bits).register(adc_clk, d=mic-2048, init=0, en=mic_stb)
    mic_stb = Boolean().register(adc_clk, d=mic_stb, init=0)

    adc_value   = response_data.subtype.register(adc_clk, d=response_data, en=response_valid, init=0)
    adc_channel = response_channel.subtype.register(adc_clk, d=response_channel, en=response_valid, init=0)

    #move to fast clock domain
    mic, mic_stb = slow_to_fast(adc_clk, clk, mic, mic_stb)
    adc, adc_stb = slow_to_fast(adc_clk, clk, adc_value.resize(32) | adc_channel.resize(32)<<16, response_valid)

    return command_channel, command_startofpacket, command_endofpacket, mic, mic_stb, adc, adc_stb
