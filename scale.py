from baremetal import *

def scale(x, fraction, extra_bits, trim_extra_bits = True):
    denominator = 2**extra_bits
    numerator = int(round(fraction*denominator))
    x_bits = x.subtype.bits
    x = x.resize(x_bits+extra_bits)
    result = x.subtype.constant(0)
    for shift_amount, bit in enumerate(bin(numerator)[2:]):
        if bit == "1":
            result = result + (x << shift_amount)

    if trim_extra_bits:
        return result[x_bits+extra_bits-1:extra_bits]
    else:
        return result
