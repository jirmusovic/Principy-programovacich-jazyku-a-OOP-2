import sys
import xml.etree.ElementTree as eet
import enum as en


def err(*args, **kwargs):
    """Wrapper for print() that outputs to stderr."""
    print(*args, file=sys.stderr, **kwargs)
    
    
class instructions:    
    def __innit__ (self, opcode, order, arg1, arg2, arg3, data1, data2, data3):
        self.op = opcode
        self.order = order
        self.a1 = arg1
        self.a2 = arg2
        self.a3 = arg3
        self.d1 = data1
        self.d2 = data2
        self.d3 = data3
    
class d_type:
    INT = 'int'
    BOOL = 'bool'
    NIL = 'nil'
    STR = 'string'
    FLOAT = 'float'
    UNDEFINED = ''
    
    
tree = eet.parse('xml.xml')
root = tree.getroot();


for instruction in root:
    print(instruction.attrib['order'], instruction.attrib['opcode'])
    for sub in instruction:
        print(sub.tag, sub.text)