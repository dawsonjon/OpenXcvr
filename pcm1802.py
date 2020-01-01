from baremetal import *


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

def pcm1802(clk, bclk, sclk, lrclk, dout)

    #create a divided down clock to drive sclk
    fs = 96000
    clk_frequency = 150000000
    clock_divide = int(ceil(clk_frequency/(512*fs)))
    counter, last = counter(clk, 0, clock_divide-1, 1)
    sclk = Boolean().register(clk, init=0i, en=last)
    sclk.d(~sclk)

    #double register clock input
    bclk = Boolean().register(clk, d=bclk, init=0)
    bclk = Boolean().register(clk, d=bclk, init=0)
    bclk_rising = bclk & ~Boolean().register(clk, d=bclk, init=0)

    #shift bits into a register msb first
    left  = Unsigned(32).register(clk, init=0, en=bclk_rising & lrclk)
    right = Unsigned(32).register(clk, init=0, en=bclk_rising & ~lrclk)
    left.d(clk, left << 1 | dout)
    right.d(clk, right << 1 | dout)

    #register left and right channel after each sample
    left  = Unsigned(32).register(clk, d=left[31:8],  en=bclk_rising & lrclk_rising)
    right = Unsigned(32).register(clk, d=right[31:8], en=bclk_rising & lrclk_rising)
    stb = Boolean.register(clk, d=bclk_rising & lrclk_rising, init=0)

    return left, right, 
