a = 1024

for i in range(1000):
    a -= a/1024.0
    print a
