from baremetal import *


def lfsr63(clk, bits, seed):
    assert bits < 61
    shifter = Unsigned(63).register(clk, init=seed)
    shifter.d(cat(shifter[62-bits:0], shifter[62:62-bits+1]^shifter[61:61-bits+1]))
    return shifter[bits-1:0]

def lfsr65(clk, bits, seed):
    assert bits < 46
    shifter = Unsigned(65).register(clk, init=seed)
    shifter.d(cat(shifter[63-bits:0], shifter[64:64-bits+1]^shifter[46:46-bits+1]))
    return shifter[bits-1:0]

def lfsr31(clk, bits, seed):
    assert bits < 27
    shifter = Unsigned(31).register(clk, init=seed)
    shifter.d(cat(shifter[30-bits:0], shifter[30:30-bits+1]^shifter[27:27-bits+1]))
    return shifter[bits-1:0]

def lfsr33(clk, bits, seed):
    assert bits < 19
    shifter = Unsigned(33).register(clk, init=seed)
    shifter.d(cat(shifter[32-bits:0], shifter[32:32-bits+1]^shifter[19:19-bits+1]))
    return shifter[bits-1:0]

def prng(clk, bits, seed, lite=False):
    if lite:
        return Unsigned(bits).register(clk, d=lfsr33(clk, bits, seed) ^ lfsr31(clk, bits, seed))
    else:
        return Unsigned(bits).register(clk,  d=lfsr63(clk, bits, seed) ^ lfsr65(clk, bits, seed))

if __name__ == "__main__":
    clk = Clock("clk")
    shifter = prng(clk, 10, 123)

    clk.initialise()
    clk.tick()
    for i in range(1000):
        print shifter.get()
        clk.tick()

    shifter = Unsigned(10).output("shifter", shifter)

    netlist = Netlist("accum",[clk], [], [shifter])
    print netlist.generate()
