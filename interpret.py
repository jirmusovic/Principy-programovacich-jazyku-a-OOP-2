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

# def get_state()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Loads an XML representation of an IPPcode23 program and interprets it.',
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
        err('Vstupni soubor nebo soubor se vstupy musi byt zadan.', 10)
        exit(10)

    if (args.input is not None and len(args.input) > 1) or (args.source is not None and len(args.source) > 1):
        err('Vstupni parametry lze zadat pouze jednou.', 10)
        exit(10)

    src = args.source[0][0] if args.source != None else sys.stdin
    if src != sys.stdin:
        src = open(src, "r")

    try:
        tree = eet.parse(src)
    except:
        sys.exit(32)
    root = tree.getroot()

    input_file = args.input[0][0] if not None else sys.stdin
    if input_file != sys.stdin:
        try:
            input_file = open(input_file, "r")
        except:
            exit(99)

    todo = len(root)
    cnt = 0
    instr = instructions.Instruction(None)
    state = instructions.State()

    max_order = 1
    instruction_set = {}
    # order: [instr, instr.name, instruction.State]

    while cnt != todo:
        cnt += 1
        for tmp in root:
            if 'order' not in tmp.attrib.keys():
                sys.exit(32)
            if not tmp.attrib['order'].isdigit():
                sys.exit(32)
            if cnt == int(tmp.attrib['order']):
                """print(tmp.attrib['order'], tmp.attrib['opcode'])"""
                if 'opcode' not in tmp.attrib.keys():
                    sys.exit(32)
                instr.name = tmp.attrib['opcode']
                instr.order = int(tmp.attrib['order'])
                if instr.order > max_order:
                    max_order = instr.order
                num = instr.how_many_args(tmp.attrib['opcode'])
                if instr.order in instruction_set or instr.order <= 0:
                    exit(32)
                if num == 0:
                    instruction_set[instr.order] = [instr, instr.name, instructions.State(instr.order, num, root, 0)]
                    
                elif num == 1:
                    var = tmp.find('arg1')
                    if var == None:
                        sys.exit(32)
                    var = var.text
                    type1 = tmp.find('arg1').get('type')
                    instruction_set[instr.order] = [instr, instr.name, instructions.State(instr.order, num, root, 0, arg1=var, type1=type1)]
                    
                elif num == 2:
                    var1 = tmp.find('arg1')
                    if var1 == None:
                        sys.exit(32)
                    var1 = var1.text
                    var2 = tmp.find('arg2')
                    if var2 == None:
                        sys.exit(32)
                    var2 = var2.text
                    type1 = tmp.find('arg1').get('type')
                    type2 = tmp.find('arg2').get('type')
                    instruction_set[instr.order] = [instr, instr.name, instructions.State(instr.order, num, root, 0, arg1=var1, arg2=var2, type1=type1, type2=type2)]
                    
                elif num == 3:
                    var1 = tmp.find('arg1')
                    if var1 == None:
                        sys.exit(32)
                    var1 = var1.text
                    var2 = tmp.find('arg2')
                    if var2 == None:
                        sys.exit(32)
                    var2 = var2.text
                    var3 = tmp.find('arg3')
                    if var3 == None:
                        sys.exit(32)
                    var3 = var3.text
                    type1 = tmp.find('arg1').get('type')
                    type2 = tmp.find('arg2').get('type')
                    type3 = tmp.find('arg3').get('type')
                    instruction_set[instr.order] = [instr, instr.name, instructions.State(instr.order, num, root, 0, arg1=var1, arg2=var2, arg3=var3, type1=type1, type2=type2, type3=type3)]
                    

                """print(tmp[0].text)"""
                for sub in tmp:
                    if len(tmp) != num:
                        err("Neocekavana struktura XML!, 32")
                        sys.exit(32)
    
    if len(instruction_set) == 0:
        exit(0)

    instr_count = 1
    while instr_count <= max_order:
        if instr_count not in instruction_set.keys():
            instr_count += 1
        else:
            act_instr = instruction_set[instr_count]
            if act_instr[1] == "LABEL":
                getattr(act_instr[0], act_instr[1])(act_instr[2])
            instr_count += 1
            
    
    instr_count = 1
    while instr_count <= max_order:
        if instr_count not in instruction_set.keys():
            instr_count += 1
        else:
            act_instr = instruction_set[instr_count]
            if act_instr[1] == "LABEL":
                instr_count += 1
                continue
            ret = getattr(act_instr[0], act_instr[1])(act_instr[2])
            if ret == None:
                instr_count += 1
            else:
                instr_count = ret
            
