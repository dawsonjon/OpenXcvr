from baremetal import *

def test_signal(clk, stb):
    """Generate an fs/4 tone at the receiver sample rate"""

    phase, _ = counter(clk, 0, 3, 1, en=stb)
    i, q = Signed(8).select(phase, 127, 0, -127, 0), Signed(8).select(phase, 0, -127, 0, 127)

    i = i.subtype.register(clk, d=i, init=0)
    q = q.subtype.register(clk, d=q, init=0)
    stb = stb.subtype.register(clk, d=stb, init=0)

    return i, q, stb
