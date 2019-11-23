from baremetal import *
from math import ceil

def pipelined_counter(clk, delta, stage_bits):
    bits = delta.subtype.bits
    stages = int(ceil(float(bits)/stage_bits))
    delta = delta.resize(stages*stage_bits)

    for stage in range(stages):
        lsb = stage * stage_bits
        msb = lsb + stage_bits - 1

        if stage == 0:
            subcounter = Unsigned(stage_bits).register(clk, init=0)
            sum = subcounter.resize(stage_bits+1) + delta[msb:lsb]
            carry, sum = sum[stage_bits], sum[stage_bits-1:0]
            subcounter.d(sum)

            counter = subcounter
            counter = counter.subtype.register(clk, d=subcounter)
            carry = carry.subtype.register(clk, init=0, d=carry)
            delta = delta.subtype.register(clk, init=0, d=delta)
        else:
            subcounter = Unsigned(stage_bits).register(clk, init=0)
            sum = subcounter.resize(stage_bits+1) + delta[msb:lsb] + carry
            carry, sum = sum[stage_bits], sum[stage_bits-1:0]
            subcounter.d(sum)

            counter = cat(subcounter, counter)
            counter = counter.subtype.register(clk, d=counter)
            carry = carry.subtype.register(clk, init=0, d=carry)
            delta = delta.subtype.register(clk, init=0, d=delta)

    return counter

    
if __name__ == "__main__":
    clk = Clock("clk")
    delta = Unsigned(32).input("delta")

    counter = pipelined_counter(clk, delta, 8)
    clk.initialise()
    delta.set(300)
    print counter.get()
    for i in range(100):
        clk.tick()
        print counter.get()
