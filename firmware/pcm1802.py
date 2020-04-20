from baremetal import *
from math import ceil
from cdc import meta_chain


#PCM1802 DAC configuration
#=========================
#
# The DAC is configured as follows:
#
# Configure in master mode with system clock 256xfs
#
# MODE_0 : HIGH
# MODE_1 : HIGH
#
# Configure in format 0, 24 bit left aligned data
#
# FMT_0 : LOW
# FMT_0 : LOW

def pcm1802(clk, bclk, lrclk, dout, clock_divide):

    #create a divided down clock to drive sclk

    count = clock_divide.subtype.register(clk, init=0)
    count.d(count.subtype.select(count==0, count-1, clock_divide-1))
    last = (count==0)
    sclk = Boolean().register(clk, init=0, en=last)
    sclk.d(~sclk)

    #double register clock input
    bclk_rising = meta_chain(clk, bclk, "rising")
    lrclk_rising = lrclk & ~Boolean().register(clk, init=0, d=lrclk, en=bclk_rising)

    #shift bits into a register msb first
    left  = Unsigned(32).register(clk, init=0, en=bclk_rising & lrclk)
    right = Unsigned(32).register(clk, init=0, en=bclk_rising & ~lrclk)
    left.d(left << 1 | dout)
    right.d(right << 1 | dout)

    #register left and right channel after each sample
    left  = Signed(18).register(clk, d=left[31:14],  en=bclk_rising & lrclk_rising)
    right = Signed(18).register(clk, d=right[31:14], en=bclk_rising & lrclk_rising)
    stb = Boolean().register(clk, d=bclk_rising & lrclk_rising, init=0)

    return left, right, stb, sclk
