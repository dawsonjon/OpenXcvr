from matplotlib import pyplot as plt

z0=-9   
z1=3454  
z2=-34855   
z3=296111

def mul(x, y):
    k = 1<<16
    return ((x*y)+k)>>18

points = []
for i in range(256):
    x = i << 18
    value = z3+mul(x,z2+mul(x,z1+mul(z0,x)))
    points.append(value>>18)
for i in range(512):
    points.append(255)
for i in reversed(range(256)):
    x = i << 18
    value = z3+mul(x,z2+mul(x,z1+mul(z0,x)))
    points.append(value>>18)

plt.plot(points)
plt.show()
