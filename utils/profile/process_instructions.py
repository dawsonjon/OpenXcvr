counts = {}

with open("instructions") as f:
    for line in f:
        _, source = line.split("///")
        source = source.split(":")[0]
        source = source.split("/")[-1]

        if source not in counts:
            counts[source]=1
        else:
            counts[source]+=1

print counts
