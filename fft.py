from baremetal import *
from sfixed import SFixed
from complex import Complex
from cmath import exp, pi

def delay(clk, x, n, init=None):
    for i in range(n):
        if init is not None:
            x = x.subtype.register(clk, d=x, init=init)
        else:
            x = x.subtype.register(clk, d=x)
    return x

def bit_reverse(x):
    bits = x.subtype.bits
    return cat(*[x[i] for i in range(bits)])

def bit_reverse_order(clk, s0, s1, valid, n):
    s0_ram = s0.subtype.ram(2*n, clk, False) 
    s1_ram = s1.subtype.ram(2*n, clk, False) 
    write_address, ovr = counter(clk, 0, n-1, 1, valid)
    write_ping_pong, _ = counter(clk, 0, 1, 1, ovr)
    write_address = cat(write_ping_pong, write_address)
    s0_ram.write(write_address, s0, valid)
    s1_ram.write(write_address, s1, valid)

    valid = delay(clk, valid, n, 0)
    read_address, ovr = counter(clk, 0, n-1, 1, valid)
    read_ping_pong, _ = counter(clk, 0, 1, 1, ovr)
    read_address = cat(read_ping_pong, bit_reverse(read_address))
    valid = delay(clk, valid, 1, 0)
    s0 = s0_ram.read(read_address)
    s1 = s1_ram.read(read_address)
    return s0, s1, valid

def reorder(clk, s0, s1, valid, n):
    m=2**(n-1)
    count, _ = counter(clk, 0, (2**n)-1, 1, valid)
    switch = count[n-1]
    s1 = delay(clk, s1, m)
    s0, s1 = s0.subtype.select(switch, s0, s1), s1.subtype.select(switch, s1, s0)
    s0 = delay(clk, s0, m)
    valid = delay(clk, valid, m, 0)
    return s0, s1, valid

def fft(clk, s0, s1, valid, num_stages):
    for stage in reversed(range(num_stages)):
        m = 2**stage

        #generate constants
        twiddles = [i/(2*m) for i in range(m)]
        twiddles = [exp(-2.0j*pi*i) for i in twiddles]
        twiddle_type = Complex(SFixed(s0.i.subtype.bits+2, s0.i.subtype.bits))

        #butterfly
        s0, s1 = s0+s1, s0-s1
        s0 = delay(clk, s0, 1)
        s1 = delay(clk, s1, 1)
        valid = delay(clk, valid, 1)

        #rotate
        if stage:
            count, _ = counter(clk, 0, m//2-1, 1, valid)
            s1 = s1 * twiddle_type.rom(count, *twiddles)
            s0 = delay(clk, s0, 1)
            s1 = delay(clk, s1, 1)
            valid = delay(clk, valid, 1)

            #reorder
            s0, s1, valid = reorder(clk, s0, s1, valid, stage)

    return bit_reverse_order(clk, s0, s1, valid, 2**(num_stages-1))


clk = Clock("clk")
base_type = SFixed(16, 8)
subtype = Complex(base_type)


a = subtype.input("in")
b = subtype.input("in")
valid = Boolean().input("valid")
s0, s1, valid_out = fft(clk, a, b, valid, 3)

test = [1, 0, 1, 0, 1, 0, 1, 0]

clk.initialise()
for i in range(10):
    for i in range(4):
        a.set(test[i]), b.set(test[i+4]), valid.set(1)
        print("%10s %10s %10s"%(s0.get(), s1.get(), valid_out.get()))
        clk.tick()
    valid.set(0)
    print("%10s %10s %10s"%(s0.get(), s1.get(), valid_out.get()))
    clk.tick()

