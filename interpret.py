"""
@author Veronika Jirmusova xjirmu00
@file interpret.py
@brief Primary file that checks arguments and then runs the whole program.
@since 11.04.2023
"""

import sys
import xml.etree.ElementTree as eet
import argparse
import instructions


def err(*args, **kwargs):
    """
    Error output.

    Function prints wanted message into stderr.
    """
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    
    # Create an ArgumentParser object with a description of the program
    parser = argparse.ArgumentParser(
        description='Nacte XML reprezentaci IPPCode2023 a interpretuje ji.',
        epilog='Alespon jeden z argumentu --source and --input musi byt zadan. Pokud jeden z nich chybi, '
                'prislusny vstupni soubor bude nacten z stdin.')
    # Add command-line arguments for the source file and input file
    parser.add_argument('-s', '--source', nargs=1, help='cesta vstupniho souboru', action='append')
    parser.add_argument('-i', '--input', nargs=1, help='cesta souboru se vstupem', action='append')

    # Parse the command-line arguments
    args = None
    try:
        args = parser.parse_args()

    # Check arguments and parse them correctly
    except SystemExit:
        # Check if '--help' argument was passed
        if '--help' in sys.argv:
            # Print usage information and exit
            err("Vstupni parametry: \
                --source=file vstupní soubor s XML reprezentací zdrojového kódu \
                --input=file soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu \
                Alespon jeden z techto paramteru musi byt zadan!")
            exit(0)
        else:
            err("Chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů", 10)
            exit(10)

    # Check if a file is given
    if args is None or (args.source is None and args.input is None):
        err('Vstupni soubor nebo soubor se vstupy musi byt zadan.', 10)
        exit(10)

    # Check if a file is used max once
    if (args.input is not None and len(args.input) > 1) or (args.source is not None and len(args.source) > 1):
        err('Vstupni parametry lze zadat pouze jednou.', 10)
        exit(10)

    # Open given file
    src = args.source[0][0] if args.source != None else sys.stdin
    if src != sys.stdin:
        src = open(src, "r")

    # Parse input file into a tree
    try:
        tree = eet.parse(src)
    except:
        err("Neocekavana struktura XML", 31)
        sys.exit(31)
    root = tree.getroot()

    # Read a file from stdin if not provided
    if args.input == None:
        input_file = sys.stdin
    else:
        input_file = args.input[0][0]
    # And open it
    if input_file != sys.stdin:
        try:
            input_file = open(input_file, "r")
        except:
            err("Interni chyba", 99)
            exit(99)

    # Check how many instructions need to be checked
    todo = len(root)
    cnt = 0
    # Instruction and state init
    instr = instructions.Instruction(input_file)

    if input_file != sys.stdin:
        input_file.close()


    state = instructions.State()

    max_order = 1
    # Instruction dicdionary
    instruction_set = {}
    # Order: [instr, instr.name, instruction.State]

    # For each instruction in the XML tree, check if it has an 'order' attribute and if it's a valid integer
    # If not, exit the program with error code 32.
    for tmp in root:
        if 'order' not in tmp.attrib.keys():
            err("Neocekavana struktura XML", 32)
            sys.exit(32)
        if not tmp.attrib['order'].isdigit():
            err("Neocekavana struktura XML", 32)
            sys.exit(32)
        # If the 'order' attribute is equal to 'cnt', create an instruction object and add it to the 'instruction_set'
        if 'opcode' not in tmp.attrib.keys():
            err("Neocekavana struktura XML", 32)
            sys.exit(32)
        instr.name = tmp.attrib['opcode']
        instr.order = int(tmp.attrib['order'])
        if instr.order > max_order:
            max_order = instr.order
        num = instr.how_many_args(tmp.attrib['opcode'].upper())
        # If the instruction order is already in 'instruction_set' or less than or equal to 0, exit with error code 32
        if instr.order in instruction_set or instr.order <= 0:
            err("Neocekavana struktura XML", 32)
            exit(32)
        # Create an instruction object with correct number of arguments and add it to 'instruction_set'
        # 0 arguments
        if num == 0:
            instruction_set[instr.order] = [instr, instr.name.upper(), instructions.State(instr.order, num, root, 0)]
            
        # 1 argument
        elif num == 1:
            var = tmp.find('arg1')
            if var == None:
                err("Neocekavana struktura XML", 32)
                sys.exit(32)
            var = var.text
            var = None if None else var.strip()
            type1 = tmp.find('arg1').get('type')
            instruction_set[instr.order] = [instr, instr.name.upper(), instructions.State(instr.order, num, root, 0, arg1=var, type1=type1)]
            
        # 2 arguments
        elif num == 2:
            var1 = tmp.find('arg1')
            if var1 == None:
                err("Neocekavana struktura XML", 32)
                sys.exit(32)
            var1 = var1.text
            var1 = None if None else var1.strip()
            var2 = tmp.find('arg2')
            if var2 == None:
                err("Neocekavana struktura XML", 32)
                sys.exit(32)
            var2 = var2.text
            var2 = None if None else var2.strip()
            type1 = tmp.find('arg1').get('type')
            type2 = tmp.find('arg2').get('type')
            instruction_set[instr.order] = [instr, instr.name.upper(), instructions.State(instr.order, num, root, 0, arg1=var1, arg2=var2, type1=type1, type2=type2)]
            
        # 3 arguments
        elif num == 3:
            var1 = tmp.find('arg1')
            if var1 == None:
                err("Neocekavana struktura XML", 32)
                sys.exit(32)
            var1 = var1.text
            var1 = None if None else var1.strip()
            var2 = tmp.find('arg2')
            if var2 == None:
                err("Neocekavana struktura XML", 32)
                sys.exit(32)
            var2 = var2.text
            var2 = None if None else var2.strip()
            var3 = tmp.find('arg3')
            if var3 == None:
                err("Neocekavana struktura XML", 32)
                sys.exit(32)
            var3 = var3.text
            var3 = None if None else var3.strip()
            type1 = tmp.find('arg1').get('type')
            type2 = tmp.find('arg2').get('type')
            type3 = tmp.find('arg3').get('type')
            instruction_set[instr.order] = [instr, instr.name.upper(), instructions.State(instr.order, num, root, 0, arg1=var1, arg2=var2, arg3=var3, type1=type1, type2=type2, type3=type3)]
            
        # Check if the number of arguments matches the expected number of arguments for the instruction
        for sub in tmp:
            if len(tmp) != num:
                #print(num, len(tmp), instr.order)
                err("Neocekavana struktura XML!", 32)
                sys.exit(32)

    # No instructions in XML file
    if len(instruction_set) == 0:
        exit(0)

    # Loop through instructions in the order they were defined
    instr_count = 1
    while instr_count <= max_order:
        # If instruction doesn't exist at this order, move on to next one
        if instr_count not in instruction_set.keys():
            instr_count += 1
        # Otherwise, get the current instruction and its arguments
        else:
            act_instr = instruction_set[instr_count]
            # If the instruction is a label, just call the method and move on to next instruction
            if act_instr[1] == "LABEL":
                getattr(act_instr[0], act_instr[1])(act_instr[2])
            instr_count += 1
            
    # Loop through instructions again, but this time execute all instructions except for labels
    instr_count = 1
    while instr_count <= max_order:
        # If instruction doesn't exist at this order, move on to next one
        if instr_count not in instruction_set.keys():
            instr_count += 1
        # Otherwise, get the current instruction and its arguments
        else:
            act_instr = instruction_set[instr_count]
            # If the instruction is a label, skip it and move on to next instruction
            if act_instr[1] == "LABEL":
                instr_count += 1
                continue
            ret = getattr(act_instr[0], act_instr[1])(act_instr[2])
            if ret == None:
                instr_count += 1
            else:
                instr_count = ret
            
    """
    End of file interpret.py
    """