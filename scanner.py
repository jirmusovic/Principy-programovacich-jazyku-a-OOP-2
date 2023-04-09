import re
import sys
import traceback
from typing import Optional, List
import xml.etree.ElementTree as eet
import argparse
import configparser
from html.parser import HTMLParser


def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description='Loads an XML representation of an IPPcode21 program and interprets it.',
        epilog='At least one of --source and --input arguments must be used. If one of them is missing, '
               'the corresponding input will be read from stdin.')
    parser.add_argument('-s', '--source', nargs=1, help='path to the input program file', action='append')
    parser.add_argument('-i', '--input', nargs=1, help='path to a file with input for the interpreted program', action='append')

    args = None
    try:
        args = parser.parse_args()

    except SystemExit:
        if '--help' in sys.argv:
            err("Vstupni parametry: \
               --source=file vstupní soubor s XML reprezentací zdrojového kódu \
               --input=file soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu \
               Alespon jeden z techto paramteru musi byt zadan!")
            exit(0)
        else:
            exit(10)

    if args is None or (args.source is None and args.input is None):
        err('Vstupni soubor nebo soubor se vstupy musi byt zadan', 10)
        exit(10)

    if (args.input is not None and len(args.input) > 1) or (args.source is not None and len(args.source) > 1):
        err('Vstupni parametry lze zadat pouze jednou', 10)
        exit(10)

    src = args.source
    print(src)
    inp = args.input

    class Instructions:
        def __innit__(self, opcode, order, arg1, arg2, arg3, data1, data2, data3):
            self.op = opcode
            self.order = order
            self.a1 = arg1
            self.a2 = arg2
            self.a3 = arg3
            self.d1 = data1
            self.d2 = data2
            self.d3 = data3

    class DType:
        INT = 'int'
        BOOL = 'bool'
        NIL = 'nil'
        STR = 'string'
        FLOAT = 'float'
        UNDEFINED = ''

    tree = eet.parse(src)
    root = tree.getroot()
    
    for instruction in root:
        print(instruction.attrib['order'], instruction.attrib['opcode'])
        for sub in instruction:
            print(sub.tag, sub.text)
            
if __name__ == '__main__':
    main()
