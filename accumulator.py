from baremetal import *

def accumulator(clk, delta, channels):
    t = delta.subtype
    def tree(delta, x, n):
        x, xn=t.register(clk, d=x), t.register(clk, d=x+delta*n)
        delta=t.register(clk, d=delta)
        if n == 1:
            return [x, xn]
        else:
            return tree(delta, x, n//2) + tree(delta, xn, n//2)
    counter = t.register(clk, init=0)
    counter.d(counter+(delta*int(channels)))
    counters = tree(delta, counter, channels//2)
    return counters


if __name__ == "__main__":
    clk = Clock("clk")
    counters = accumulator(clk, Unsigned(10).constant(1), 8)

    results = []
    clk.initialise()
    clk.tick()
    clk.tick()
    for i in range(16):
        for j in range(8):
            clk.tick()
            for channel in counters:
                sample = channel.get()
                print sample
                results.append(sample),

    if results == range(1024):
        print "pass"
    else:
        print "fail"

    counters = [Unsigned(16).output("i_%u"%i, x) for i, x in enumerate(counters)]

    netlist = Netlist("accum",[clk], [], counters)
    #print netlist.generate()
