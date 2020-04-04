from baremetal import *
from math import ceil
from cdc import meta_chain


def rotary_encoder(clk, quad_a, quad_b, debounce_time_s = 0.004, frequency_Hz = 50000000):

    debounce_clocks = debounce_time_s * frequency_Hz

    #double register quadrature inputs
    quad_a = meta_chain(clk, quad_a)
    quad_b = meta_chain(clk, quad_b)

    _, sample = counter(clk, 0, debounce_clocks-1, 1)
    quad_a = quad_a.subtype.register(clk, init=3, d=quad_a, en=sample)
    quad_b = quad_b.subtype.register(clk, init=3, d=quad_b, en=sample)
    old_a = quad_a.subtype.register(clk, init=3, d=quad_a)
    old_b = quad_b.subtype.register(clk, init=3, d=quad_b)

    position = Signed(32).register(clk, init=0, en=(quad_b ^ old_b) & ~quad_a & ~old_a) #any change in b when a is low
    position.d(position.subtype.select(quad_b, position+1, position-1))

    return position

clk = Clock("clk")
quad_a = Boolean().input("quad_a")
quad_b = Boolean().input("quad_b")
count = rotary_encoder(clk, quad_a, quad_b)
count = count.subtype.output("position", count)
netlist = Netlist(
    "rotary_encoder",
    [clk], 
    [quad_a, quad_b],
    [count],
)
f = open("rotary_encoder.v", "w")
f.write(netlist.generate())
