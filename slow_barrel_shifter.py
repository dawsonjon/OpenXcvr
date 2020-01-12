from baremetal import *
from math import ceil, log

def slow_barrel_shifter(clk, x, shift_amount, stb, left_right):

    bits = x.subtype.bits 
    shift_bits = int(ceil(log(bits, 2)))+1

    x_shifted = x.subtype.register(clk, init=0)
    shift_amount_reg = (shift_bits).register(clk, init=0)

    done = (shift_amount_reg==0)
    if left_right == "left":
        next_x_shifted    = x.subtype.select(done, x_shifted<<1,   x_shifted)
        next_shift_amount = x.subtype.select(done, shift_amount_reg-1, shift_amount_reg)
    else:
        next_x_shifted    = x.subtype.select(done, x_shifted>>1,   x_shifted)
        next_shift_amount = x.subtype.select(done, shift_amount_reg-1, shift_amount_reg)

    next_x_shifted    = x.subtype.select(stb, next_x_shifted, x)
    next_shift_amount = x.subtype.select(stb, next_shift_amount, shift_amount)

    x_shifted.d(next_x_shifted)
    shift_amount_reg.d(next_shift_amount)
    stb  = stb.subtype.register(clk, d=stb, init=0)
    done = done & (~done.subtype.register(clk, d=done, init=0) | stb)

    return x_shifted, done

def test(clk, a, b):
    din.set(a)
    shmtin.set(b)
    stb_in.set(1)
    clk.tick()
    stb_in.set(0)

    for i in range(10):
        if stb_out.get():
            assert dout.get() == a>>b
        clk.tick()

if __name__ == "__main__":

    clk = Clock("clk")
    din = Unsigned(8).input("din")
    shmtin = Unsigned(8).input("shmtin")
    stb_in = Unsigned(1).input("stb_in")

    dout, stb_out = slow_barrel_shifter(clk, din, shmtin, stb_in, "right")

    clk.initialise()
    test(clk, 100, 4)
    test(clk, 255, 0)
    test(clk, 255, 1)
    test(clk, 255, 7)
    test(clk, 255, 8)
    test(clk, 1, 0)
    test(clk, 1, 1)
    test(clk, 1, 7)
    test(clk, 1, 8)
    test(clk, 0, 0)
    test(clk, 0, 1)
    test(clk, 0, 7)
    test(clk, 0, 8)
    print "pass"

