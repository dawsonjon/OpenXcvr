from baremetal import *
from math import sin, pi

clk = Clock("clk")

pulse_width = Unsigned(32).constant(0)
amplitude = Unsigned(32).constant(1)
error = Signed(32).constant(0)+(pulse_width-amplitude)

print error.get()
error_accumulator = Signed(32).register(clk, init=0)
error_accumulator.d(error_accumulator+error)

print (error_accumulator+error).get()
#amplitude_error.drive(error_accumulator)

