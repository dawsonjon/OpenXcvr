from baremetal import *

def tx_uart(clk, rx, baud_rate, clock_frequency):

    Boolean().wire(half_tick)
    Boolean().wire(tick)
    Boolean().wire(bit_tick)
    Boolean().wire(stop_tick)

    state, next_state = fsm(clk, 
    {
        "idle" : ((rx, "wait"), "idle"),
        "wait" : ((half_tick,  "rx"), "wait"),
        "rx"   : ((bit_tick),  "stop")
        "stop" : ((stop_tick), "idle")
    }, default:"idle")

    baud_max = int(round(baud_rate/clock_frequency)) - 1
    half_baud_max = int(round(baud_rate/(2.0*clock_frequency))) - 1

    _, ovr = counter(clk, 0, half_baud_max, 1, en=state["wait"])
    half_tick.drive(ovr)
    _, ovr = counter(clk, 0, baud_max, 1, en=state["rx"])
    tick.drive(ovr)
    _, ovr = counter(clk, 0, baud_max, 1, en=state["stop"])
    stop_tick.drive(ovr)
    _, ovr = counter(clk, 0, 7, 1, en=tick)
    bit_tick.drive(ovr)

    data = Unsigned(8).register(clk, init=0, en=tick)
    data.d(cat(data[6:0], rx))

    return data, bit_tick

