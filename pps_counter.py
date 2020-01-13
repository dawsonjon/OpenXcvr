from baremetal import *
from cdc import meta_chain

def pps_counter(clk, pps):
    """Use the 1 pps output of a gps module to count clock cycles,
    the CPU can use this to calculate a correction factor for
    the frequency"""

    #detect rising edge of 1pps count
    pps_rising = meta_chain(clk, pps, "rising")

    #count clock cycles between rising edges
    count = Unsigned(31).register(clk, init=0)
    count.d(count.subtype.select(pps_rising, count+1, 0))

    #register the total
    count=count.subtype.register(clk, d=count, en=pps_rising, init=0)

    return count
