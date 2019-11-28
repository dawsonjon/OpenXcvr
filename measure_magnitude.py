from baremetal import *
from baremetal.signed import number_of_bits_needed
from settings import Settings
from math import log, pi
from matplotlib import pyplot as plt
import numpy as np
import sys
from math import log, ceil
from numpy import log10


def measure_magnitude(clk, data_in, stb, settings):
    frame_size = settings.agc_frame_size
    frames = settings.agc_frames
    frame_count, eop = counter(clk, 0, frame_size-1, 1)
    sop = frame_count == 0

    #find the largest value in a frame
    t_data = data_in.subtype     
    maxval = t_data.register(clk, init=0, en=stb)
    minval = t_data.register(clk, init=0, en=stb)
    maxval.d(t_data.select(sop, t_data.select(data_in > maxval, maxval, data_in), data_in))
    minval.d(t_data.select(sop, t_data.select(data_in < minval, minval, data_in), data_in))
    stb = Boolean().register(clk, d=stb&eop, init=0)

    #store frames in a circular buffer
    en = Boolean().wire()
    count, _ = counter(clk, 0, frames, 1, en)
    address, _ = counter(clk, 0, frames-1, 1, en)
    write = (count == frames)
    en.drive(~write|stb)#wait for a strobe
    sop = count == 0
    eop = count == frames-1

    #create RAM
    bufmax = t_data.ram(clk=clk, depth=frames)
    bufmin = t_data.ram(clk=clk, depth=frames)

    #write data into RAM
    bufmax.write(address, maxval, write & stb) 
    bufmin.write(address, minval, write & stb) 

    #read_data_from_RAM
    maxval = bufmax.read(address)
    minval = bufmin.read(address)

    ###################################################
    minval = minval.subtype.register(clk, d=minval)
    maxval = maxval.subtype.register(clk, d=maxval)
    write = write.subtype.register(clk, d=write, init=0)
    sop = sop.subtype.register(clk, d=sop, init=0)
    eop = eop.subtype.register(clk, d=eop, init=0)
    ###################################################

    #apply weighting to profile
    weighted_maxval = maxval
    weighted_minval = minval

    #find the largest value in the stored frames
    maxval = t_data.register(clk, init=0, en=~write)
    minval = t_data.register(clk, init=0, en=~write)
    maxval.d(t_data.select(sop, t_data.select(weighted_maxval > maxval, maxval, weighted_maxval), weighted_maxval))
    minval.d(t_data.select(sop, t_data.select(weighted_minval < minval, minval, weighted_minval), weighted_minval))
    stb = Boolean().register(clk, d=eop, init=0)
    maxval = t_data.register(clk, d=maxval, en=stb)
    minval = t_data.register(clk, d=minval, en=stb)

    #calculate magnitude
    maxval = maxval.resize(t_data.bits+1)
    magnitude = (maxval - minval) >> 1
    dc = (maxval + minval) >> 1
    magnitude = magnitude.resize(t_data.bits)
    dc = dc.resize(t_data.bits)


    return dc, magnitude

if __name__ == "__main__" and "sim" in sys.argv:

    settings = Settings()
    settings.agc_frame_size = 100
    settings.agc_frames = 4
    clk = Clock("clk")
    data_in = Signed(9).input("data_in")
    stb_in = Boolean().input("stb_in")
    dc, magnitude = measure_magnitude(clk, data_in, stb_in, settings)

    stimulus = []
    for i in range(1000):
        stimulus.append(0)
    for i in range(100):
        stimulus.append(0)
        stimulus.append(22)
        stimulus.append(-18)
    for i in range(300):
        stimulus.append(0)
    for i in range(100):
        stimulus.append(0)
        stimulus.append(22)
        stimulus.append(-18)
    for i in range(1000):
        stimulus.append(0)
    for i in range(100):
        stimulus.append(0)
        stimulus.append(200)
        stimulus.append(-200)
    for i in range(1000):
        stimulus.append(0)

    response = []

    #simulate
    clk.initialise()

    stb_in.set(1)
    i = 0
    for data in stimulus:
        data_in.set(data)
        clk.tick()
        response.append(magnitude.get())
        i+=1

    response = np.array(response)

    plt.plot(response)
    plt.plot(stimulus)
    plt.show()
