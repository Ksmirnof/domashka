
test_dict = {
    'Russia': ('Moscow', 143.5),
    'USA': ('Washington', 318.9),
    'China': ('Beijing', 1376.5)
}

for c in test_dict.keys():
    print("%s\n\t%s\n\t%d millions" % (c, test_dict[c][0], test_dict[c][1]))
