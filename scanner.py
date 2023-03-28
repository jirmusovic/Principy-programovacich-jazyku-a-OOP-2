import sys
import xml.etree.ElementTree as eet
import enum as en


tree = eet.parse('xml.xml')
root = tree.getroot();



for instruction in root:
    print(instruction.attrib['order'], instruction.attrib['opcode'])
    for sub in instruction:
        print(sub.tag, sub.text)