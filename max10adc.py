from baremetal import *
from cdc import slow_to_fast

def max_adc(clk, adc_clk, rx_tx, command_ready, response_valid, response_channel, response_data):


    #tx channel sequence 8, 8, 8, 8, 8, 8 ......
    #rx channel sequence 2, 5, 2, 5, 2, 5 ......
    idx, command_endofpacket = counter(adc_clk, 0, 1, 1, en=command_ready)
    command_startofpacket = (idx==0)
    rx_command_channel = Unsigned(5).select(idx, 2, 5)
    tx_command_channel = Unsigned(5).constant(8)
    command_channel = Unsigned(5).select(rx_tx, rx_command_channel, tx_command_channel)

    #response interface
    mic = Unsigned(12).register(adc_clk, d=response_data, en=((response_channel==8) & response_valid), init=0)
    mic_stb = Boolean().register(adc_clk, d=((response_channel==8)&response_valid), init=0)

    i = Unsigned(12).register(adc_clk, d=response_data, en=((response_channel==2) & response_valid), init=0)
    q = Unsigned(12).register(adc_clk, d=response_data, en=((response_channel==5) & response_valid), init=0)
    iq_stb = Boolean().register(adc_clk, d=((response_channel==5)&response_valid), init=0)#trigger strobe on access to last channel

    #average 10 mic samples together
    mic = Signed(mic.subtype.bits).register(adc_clk, d=mic-2048, init=0)
    mic_stb = Boolean().register(adc_clk, d=mic_stb, init=0)
    #count, last = counter(adc_clk, 0, 9, 1, en=mic_stb)
    #first = (count == 0)
    #mic_accumulator = Signed(16).register(adc_clk, init=0, en=mic_stb)
    #mic_accumulator.d(mic_accumulator.subtype.select(count==0, mic_accumulator + mic, mic))
    #mic = mic_accumulator
    #mic_stb = Boolean().register(adc_clk, d=mic_stb&last, init=0)

    #take every 5th sample i/q samples together
    i = Signed(i.subtype.bits).register(adc_clk, d=i-2048, init=0)
    q = Signed(q.subtype.bits).register(adc_clk, d=q-2048, init=0)
    iq_stb = Boolean().register(adc_clk, d=iq_stb, init=0)

    count, last = counter(adc_clk, 0, 4, 1, en=iq_stb)
    first = (count == 0)
    i_accumulator = Signed(15).register(adc_clk, init=0, en=iq_stb)
    q_accumulator = Signed(15).register(adc_clk, init=0, en=iq_stb)
    i_accumulator.d(i_accumulator.subtype.select(first, i_accumulator + i, i))
    q_accumulator.d(q_accumulator.subtype.select(first, q_accumulator + q, q))
    i = i_accumulator
    q = q_accumulator
    i.subtype.register(adc_clk, init=0, en=iq_stb&last, d=i)
    q.subtype.register(adc_clk, init=0, en=iq_stb&last, d=q)
    iq_stb = Boolean().register(adc_clk, d=iq_stb&last, init=0)

    #move to fast clock domain
    mic, mic_stb = slow_to_fast(adc_clk, clk, mic, mic_stb)
    iq_bits = i.subtype.bits
    iq, iq_stb = slow_to_fast(adc_clk, clk, i.cat(q), iq_stb)
    i, q = iq[iq_bits*2-1:iq_bits], iq[iq_bits-1:0]

    return command_channel, command_startofpacket, command_endofpacket, mic, mic_stb, i, q, iq_stb
