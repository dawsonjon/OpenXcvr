from baremetal import *


def meta_chain(clk, data, edge_detect=None):
    """double register with optional edge detect"""

    data = data.subtype.register(clk, d=data, init=0)
    data = data.subtype.register(clk, d=data, init=0)
    
    if edge_detect == "rising":
        data = data & ~data.subtype.register(clk, d=data, init=0)

    elif edge_detect == "falling":
        data = ~data & data.subtype.register(clk, d=data, init=0)

    elif edge_detect == "both":
        data = ~data & data.subtype.register(clk, d=data, init=0)

    return data


def slow_to_fast(slow_clk, fast_clk, data, stb=None):
    """Transfer a vector from a slow to a fast clock domain strobe is optional"""

    if stb is None:
        stb, _ = counter(slow_clk, 0, 1, 1)

    data = data.subtype.register(slow_clk, d=data, init=0, en=stb)
    stb = stb.subtype.register(slow_clk, d=stb, init=0)

    #######################################################################
    # Clock Domain Crossing
    #######################################################################

    stb = meta_chain(fast_clk, stb, "rising")
    data = data.subtype.register(fast_clk, d=data, init=0, en=stb)
    stb = stb.subtype.register(fast_clk, d=stb, init=0)

    return data, stb


