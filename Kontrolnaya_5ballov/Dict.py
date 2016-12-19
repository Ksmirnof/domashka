import os
import xml.etree.ElementTree as etree

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))

DICT = "%s\\data\\dict.xdxf" % SCRIPT_DIR

out_dict = {}

tree = etree.parse(DICT)
root = tree.getroot()
ars = root.findall('ar')
for ar in ars:
    out_dict.update({ar[0].text: ar[0].tail.strip('\n')})

print(out_dict)
