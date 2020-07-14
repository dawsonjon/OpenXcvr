def add(a, b):
    if a == "0":
        return b
    if b == "0":
        return a
    return "(%s+%s)"%(a, b)

def mul(a, b):
    if a == "0":
        return "0"
    if b == "0":
        return "0"
    if a == "1":
        return b
    if b == "1":
        return a
    if a == "-1":
        return negate(b)
    if b == "-1":
        return negate(a)
    return "(%s*%s)"%(a, b)

def negate(a):
    if a=="0":
        return "0"
    if a.startswith("-"):
        return "+" + a[1:]
    if a.startswith("+"):
        return "-" + a[1:]
    return "-(%s)"%a

def filter(data, kernel):
    new_data = []
    for i in range(len(data)):
        accumulator = "0"
        for j in range(len(kernel)):
            if i+j < len(data):
                accumulator = add(accumulator, mul(data[i+j], kernel[j]))
        new_data.append(accumulator)
    return new_data

    i, q = i.subtype.select(phase, q, i, -q, -i), q.subtype.select(phase, i, -q, -i, q)

def upconvert(i, q):
    for counter in range(len(i)):
        if counter % 4 == 0:
            new_i.append(i, range(len(i)))

        if counter % 4 == 1:
        if counter % 4 == 2:
        if counter % 4 == 3:



kernel = ["k%u"%i for i in range(7)]
data   = ["s%u"%i for i in range(20)]
print filter(data, kernel)
