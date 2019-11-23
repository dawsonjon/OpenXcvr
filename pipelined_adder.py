from baremetal import *
from math import ceil

def pipelined_adder(clk, a, b, sublength):
    length = max([a.subtype.bits, b.subtype.bits])
    stages = int(ceil(float(length)/sublength))

    a = a.resize(length * stages)
    b = b.resize(length * stages)

    for stage in range(stages):
        lsb = stage * sublength
        msb = lsb + sublength - 1
        if stage == 0:
            subtotal = a[msb:lsb].resize(sublength+1)+b[msb:lsb]
            carry = subtotal[sublength]
            total = subtotal[sublength-1:0]

            a = a.subtype.register(clk, d=a)
            b = b.subtype.register(clk, d=b)
            total = total.subtype.register(clk, d=total)
            carry = carry.subtype.register(clk, d=carry)
        else:
            subtotal = a[msb:lsb].resize(sublength+1)+b[msb:lsb]+carry
            carry = subtotal[sublength]
            total = cat(subtotal[sublength-1:0], total)

            a = a.subtype.register(clk, d=a)
            b = b.subtype.register(clk, d=b)
            total = total.subtype.register(clk, d=total)
            carry = carry.subtype.register(clk, d=carry)

    return total

clk = Clock("clk")
a = Unsigned(4).input("a")
b = Unsigned(4).input("b")

total = pipelined_adder(clk, a, b, 2)
for i in range(16):
    for j in range(16):
        a.set(i)
        b.set(j)
        clk.tick()
        clk.tick()
        print total.get(), (i+j)&0xf
