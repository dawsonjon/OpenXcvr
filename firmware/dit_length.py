def dit_length_seconds(wpm):
    #wps = wpm/60.0
    #dits_per_second = wps*50.0
    #return 1000/dits_per_second
    return 1200/wpm

print dit_length_seconds(5)
print dit_length_seconds(10)
print dit_length_seconds(20)
print dit_length_seconds(60)
