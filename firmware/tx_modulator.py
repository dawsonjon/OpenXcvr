from baremetal import *
from math import sin, pi

def register(clk, *signals):
    return [i.subtype.register(clk, init=0, d=i) for i in signals]

def pwm_modulator(clk, audio, frequency_multiplier):

    counter = audio.subtype.register(clk, init=0)
    frequency_multiplier = counter.subtype.select(audio>1792, frequency_multiplier, 3)#reduce PWM period for small signals
    frequency_multiplier = counter.subtype.select(audio<-1792, frequency_multiplier, 3)#reduce PWM period for small signals
    counter.d(counter+frequency_multiplier)
    output = (counter < audio)

    return audio, counter, output

def test_modulator(clk, f):

    accumulator = Unsigned(32).register(clk, init=0)
    accumulator.d(accumulator+int((2**32)*(f/150e6)))

    lut_depth = 512
    scaling_factor = 2047
    sin_lookup_table = [sin(2.0*pi*i/lut_depth) for i in range(lut_depth)]
    sin_lookup_table = [int(round(i*scaling_factor)) for i in sin_lookup_table]

    test_signal = Signed(12).rom(accumulator[31:23], *sin_lookup_table)

    return pwm_modulator(clk, test_signal, 4)

if __name__ == "__main__":

    from matplotlib import pyplot as plt
    from itertools import cycle
    import numpy as np
    cycol = cycle('bgrcmk')

    class Monitor:
        def __init__(self, *args):
            self.points = []
            self.signals = args

        def point(self):
            print [i.get() for i in self.signals]
            self.points.append(tuple([i.get() for i in self.signals]))

        def plot(self):
            fig, ax1 = plt.subplots()
            for series in zip(*self.points):
                ax2 = ax1.twinx()
                ax2.plot(series, c=next(cycol), drawstyle='steps')
            plt.show()

        
    clk = Clock("clock")
    amplitude, accumulator, output = test_modulator(clk, 1000)

    monitor = Monitor(amplitude, output, accumulator)#, error, error_accumulator, adjusted_amplitude)
    for i in range(160000):
        clk.tick()
        monitor.point()

    monitor.plot()
