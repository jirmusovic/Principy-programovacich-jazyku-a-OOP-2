import re
import sys
import traceback
from typing import Optional, List
import xml.etree.ElementTree as eet
import argparse
import configparser
from html.parser import HTMLParser

import instructions


def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description='Loads an XML representation of an IPPcode23 program and interprets it.',
        epilog='At least one of --source and --input arguments must be used. If one of them is missing, '
               'the corresponding input will be read from stdin.')
    parser.add_argument('-s', '--source', nargs=1, help='path to the input program file', action='append')
    parser.add_argument('-i', '--input', nargs=1, help='path to a file with input for the interpreted program',
                        action='append')

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
        err('Vstupni soubor nebo soubor se vstupy musi byt zadan.', 10)
        exit(10)

    if (args.input is not None and len(args.input) > 1) or (args.source is not None and len(args.source) > 1):
        err('Vstupni parametry lze zadat pouze jednou.', 10)
        exit(10)

    src = args.source
    src = src[0][0]
    inp = args.input

    tree = eet.parse(src)
    root = tree.getroot()

    todo = len(root)
    cnt = 0
    instr = instructions.Instruction()
    state = instructions.State()
    print(root[1][0].text)
    while cnt != todo:
        cnt += 1
        for tmp in root:
            if cnt == int(tmp.attrib['order']):
                """print(tmp.attrib['order'], tmp.attrib['opcode'])"""
                instr.name = tmp.attrib['opcode']
                instr.order = tmp.attrib['order']
                num = instr.how_many_args(tmp.attrib['opcode'])
                getattr(instructions.Instruction, instr.name)(instructions.Instruction, instructions.State(tmp.attrib['order'], num))
                """print(tmp[0].text)"""
                for sub in tmp:
                    if len(tmp) != num:
                        err("Neocekavana struktura XML!, 32")
                        break


if __name__ == '__main__':
    main()
