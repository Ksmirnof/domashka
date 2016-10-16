import os

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))

test_dict = {
    'Russia': ('Moscow', 143.5),
    'USA': ('Washington', 318.9),
    'China': ('Beijing', 1376.5)
}

for c in test_dict.keys():
    directory = "%s\\%s" % (SCRIPT_DIR, c)
    if not os.path.exists(directory):
        os.makedirs(directory)
        with open("%s\\info.txt" % directory, 'w') as f:
            f.write("%s, %d millions" % (test_dict[c][0], test_dict[c][1]))
