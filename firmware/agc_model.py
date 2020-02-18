"""A simple script to help model the effects ofg attack and decay factors on AGC"""

from matplotlib import pyplot as plt

audio = [100 for i in range(200)] + [0 for i in range(1000000)]
max_hold = 0
time = 0

times = []
magnitudes = []

for i in audio:

    if i > max_hold:
        max_hold += (i - max_hold) * (2.0**-4.0)
        counter = 100000
    elif counter:
        counter -= 1
    else:
        max_hold -= max_hold * (2.0**-14.0)

    times.append(time)
    magnitudes.append(max_hold)

    time += 10.0e-6

plt.plot(times, magnitudes, times, audio)
plt.show()
