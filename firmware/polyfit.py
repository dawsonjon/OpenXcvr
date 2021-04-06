import numpy as np
from matplotlib import pyplot as plt

def function_to_approximate(x):
    return 128*(np.sin((np.pi*x/256)-(0.5*np.pi))+1)

def calculate_poly(z, x):
    return np.round(z[3]+x*(z[2]+x*(z[1]+z[0]*x)))

def quantize(z, fraction_bits):
    q = 2.0**fraction_bits
    z = z * q
    z = np.round(z)
    z /= q
    return z

a = np.arange(256)

z = np.polyfit(a, function_to_approximate(a), 4)


p = np.poly1d(z)
z = quantize(z, 18)
q = np.poly1d(z)
print(z * 2**18)


plt.plot(function_to_approximate(a))
plt.plot(p(a))
plt.plot(q(a))
plt.plot(calculate_poly(z, a))
plt.show()
