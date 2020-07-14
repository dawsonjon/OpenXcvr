from baremetal import *
from math import atan, pi, sqrt
import sys

#1.0 = +180
#-1.0 = -180
def calculate_gain(iterations):
    gain = 1.0
    for idx in range(iterations):
        d = 2.0**idx
        magnitude = sqrt(1+(1.0/d)*(1.0/d))
        gain *= magnitude
    return gain

def rectangular_to_polar(clk, i, q, stb):
    extra_bits = 1
    iterations = i.subtype.bits -1 + extra_bits
    #magnitude can be up to 1.414*i/q and cordic gain of ~1.6 can give a growth of ~2.4
    t_data = Signed(i.subtype.bits+2)
    #allow some extra fraction bits
    fraction_bits = iterations
    scale_factor = 2**fraction_bits
    t_phase = Signed(fraction_bits+1)

    
    ltz = q < q.subtype.constant(0)
    phase = t_phase.select(ltz, t_phase.constant(+0.5 * scale_factor), t_data.constant(-0.5 * scale_factor))
    first_i = t_data.register(clk, d=t_data.select(ltz,  q, -q), en=stb)
    first_q = t_data.register(clk, d=t_data.select(ltz, -i,  i), en=stb)
    first_phase = t_phase.register(clk, d=phase, en=stb)
    stb = stb.subtype.register(clk, d=stb, init=0)

    #############################################

    en=Boolean().wire()
    iteration, _ = counter(clk, 0, iterations, 1, en=en)
    first_iteration = (iteration == 0)
    last_iteration = (iteration == iterations-1)
    waiting = (iteration == iterations)
    en.drive(~waiting|stb)

    angles = [round(scale_factor * atan(2.0**-idx)/pi) for idx in range(iterations)]
    angle = t_phase.rom(iteration, *angles)

    i = t_data.register(clk, d=i, en=~waiting)
    q = t_data.register(clk, d=q, en=~waiting)
    phase = t_phase.register(clk, d=phase, en=~waiting)

    next_i = t_data.select(first_iteration, i, first_i)
    next_q = t_data.select(first_iteration, q, first_q)
    next_phase = t_phase.select(first_iteration, phase, first_phase)
    q_shifted = next_q >> iteration
    i_shifted = next_i >> iteration

    ltz = next_q < next_q.subtype.constant(0)

    i.d(t_data.select(ltz, next_i+q_shifted, next_i-q_shifted))
    q.d(t_data.select(ltz, next_q-i_shifted, next_q+i_shifted))
    phase.d(t_phase.select(ltz, next_phase+angle, next_phase-angle))
    phase >>= extra_bits
    stb = stb.subtype.register(clk, d=last_iteration)

    return (i>>2).resize(t_data.bits-2), phase.resize(t_data.bits-2), stb, calculate_gain(iterations)


def polar_to_rectangular(clk, magnitude, phase, stb):
    t_data = magnitude.subtype
    t_phase = phase.subtype
    iterations = t_phase.bits+1
    fraction_bits = t_phase.bits-1
    scale_factor = 2**fraction_bits

    #gain = calculate_gain(iterations)
    i = magnitude #* Signed(iterations+2).constant(1.0/gain)
    q = t_data.constant(0)

    gtz = phase > 0
    temp_i = t_data.select(gtz,  q, -q)
    temp_q = t_data.select(gtz, -i,  i)
    i, q = temp_i, temp_q
    phase = t_phase.select(gtz, phase+(0.5*scale_factor), phase-(0.5*scale_factor))

    first_i = i.subtype.register(clk, d=i, en=stb)
    first_q = q.subtype.register(clk, d=q, en=stb)
    first_phase = t_phase.register(clk, d=phase, en=stb)
    stb = stb.subtype.register(clk, d=stb, init=0)
    #############################################

    en=Boolean().wire()
    iteration, _ = counter(clk, 0, iterations, 1, en=en)
    first_iteration = (iteration == 0)
    last_iteration = (iteration == iterations-1)
    waiting = (iteration == iterations)
    en.drive(~waiting|stb)

    angles = [round(scale_factor * atan(2.0**-idx)/pi) for idx in range(iterations)]
    angle = t_phase.rom(iteration, *angles)

    i = t_data.register(clk, d=i, en=~waiting)
    q = t_data.register(clk, d=q, en=~waiting)
    phase = t_phase.register(clk, d=phase, en=~waiting)

    next_i = t_data.select(first_iteration, i, first_i)
    next_q = t_data.select(first_iteration, q, first_q)
    next_phase = t_phase.select(first_iteration, phase, first_phase)
    q_shifted = next_q >> iteration
    i_shifted = next_i >> iteration

    gtz = next_phase > 0

    i.d(t_data.select(gtz, next_i+q_shifted, next_i-q_shifted))
    q.d(t_data.select(gtz, next_q-i_shifted, next_q+i_shifted))
    phase.d(t_phase.select(gtz, next_phase+angle, next_phase-angle))
    stb = stb.subtype.register(clk, d=last_iteration, init=0)

    return i, q, phase

if __name__ == "__main__":


    if "sim_1" in sys.argv:
        gain = calculate_gain(17)

        i_in = Signed(8).input("in")
        q_in = Signed(8).input("in")
        stb_in = Boolean().input("stb")
        clk = Clock("clk")
        magnitude, phase, stb, _ = rectangular_to_polar(clk, i_in, q_in, stb_in)

        stimulus = [
        [127, 0], 
        [127, -127], 
        [0, -127], 
        [-127, -127], 
        [-127, 0], 
        [-127, 127], 
        [0, 127], 
        [127, 127], 
        ]
        response = []
        clk.initialise()
        for i, q in stimulus:
            for j in range(20):
                stb_in.set(j==19)
                i_in.set(i)
                q_in.set(q)
                clk.tick()

                if stb.get():
                    mag = magnitude.get()
                    mag_corrected = None
                    if mag is not None:
                        mag_corrected = mag/gain
                    ph = phase.get()
                    if ph is not None:
                        ph /= (2.0**7)
                    print(mag, mag_corrected, ph, stb.get())
                    response.append((mag_corrected, ph))

    if "sim_2" in sys.argv:

        mag_in = Signed(8).input("in")
        phase_in = Signed(8).input("in")
        stb_in = Boolean().input("stb")
        clk = Clock("clk")
        i, q, stb = polar_to_rectangular(clk, mag_in, phase_in, stb_in)

        stimulus = [
        [127, 0], 
        [127, 32], 
        [127, 64], 
        [127, 96], 
        [127, -128], 
        [127, -96], 
        [127, -64], 
        [127, -32], 
        ]
        response = []
        clk.initialise()
        for mag, phase in stimulus:
            for j in range(20):
                stb_in.set(j==19)
                mag_in.set(mag)
                phase_in.set(phase)
                clk.tick()

                #if stb.get():
                print(i.get(), q.get(), stb.get())
