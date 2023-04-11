import re
import sys
import traceback
from typing import Optional, List
import xml.etree.ElementTree as eet
import argparse
import interpret


class Instruction:
    name = None
    order = None

    def how_many_args(self, opcode):
        if opcode == "CREATEFRAME" or opcode == "PUSHFRAME" or opcode == "POPFRAME" or opcode == "RETURN" or opcode == "BREAK":
            return 0
        if opcode == "DEFVAR" or opcode == "POPS" or opcode == "CALL" or opcode == "LABEL" or opcode == "JUMP" \
                or opcode == "WRITE" or opcode == "EXIT" or opcode == "PUSHS" or opcode == "DPRINT":
            return 1
        if opcode == "MOVE" or opcode == "INT2CHAR" or opcode == "STRLEN" or opcode == "TYPE" or opcode == "READ":
            return 2
        if opcode == "ADD" or opcode == "SUB" or opcode == "MUL" or opcode == "IDIV" or opcode == "LT" or opcode == "GT" \
                or opcode == "EQ" or opcode == "GETCHAR" or opcode == "AND" or opcode == "OR" \
                or opcode == "NOT" or opcode == "CONCAT" or opcode == "STR2INT" or opcode == "SETCHAR" or opcode == "JUMPIFEQ" or opcode == "JUMPIFNEQ":
            return 3
        else:
            interpret.err("Neocekavana XML struktura!", 32)
            return -1

    def MOVE(self, state):
        print(state.numOfArgs)

    def DEFVAR(self, state):
        state.name = state.arg1[3:]
        if state.GFrame.get(state.name) is None:
            state.GFrame.define(state.name, 0)
        else:
            interpret.err("chyba při sémantických kontrolách vstupního kódu", 52)
            exit(52)

    def CALL(self, state):
        print(state.order)

    def RETURN(self, state):
        print(state.order)

    def PUSHS(self, state):
        print(state.order)

    def POPS(self, state):
        print(state.order)

    def ADD(self, state):
        if state.type2 == 'int' and state.type3 == 'int':
            state.name = state.arg1[3:]
            if state.GFrame.get(state.name) is None:
                interpret.err("běhová chyba interpretace", 54)
                exit(54)
            var1 = int(state.arg2)
            var2 = int(state.arg3)
            result = var1 + var2
            state.GFrame.define(state.name, result)
        else:
            interpret.err(" běhová chyba interpretace", 53)
            exit(53)

    def SUB(self, state):
        if state.type2 == 'int' and state.type3 == 'int':
            state.name = state.arg1[3:]
            if state.GFrame.get(state.name) is None:
                interpret.err("běhová chyba interpretace", 54)
                exit(54)
            var1 = int(state.arg2)
            var2 = int(state.arg3)
            result = var1 - var2
            state.GFrame.define(state.name, result)
        else:
            interpret.err(" běhová chyba interpretace", 53)
            exit(53)

    def MUL(self, state):
        if state.type2 == 'int' and state.type3 == 'int':
            state.name = state.arg1[3:]
            if state.GFrame.get(state.name) is None:
                interpret.err("běhová chyba interpretace", 54)
                exit(54)
            var1 = int(state.arg2)
            var2 = int(state.arg3)
            result = var1 * var2
            state.GFrame.define(state.name, result)
        else:
            interpret.err(" běhová chyba interpretace", 53)
            exit(53)

    def IDIV(self, state):
        if state.type2 == 'int' and state.type3 == 'int':
            state.name = state.arg1[3:]
            if state.GFrame.get(state.name) is None:
                interpret.err("běhová chyba interpretace", 54)
                exit(54)
            if int(state.arg3) == 0:
                interpret.err("nelze delit nulou!", 57)
                exit(57)
            var1 = int(state.arg2)
            var2 = int(state.arg3)
            result = var1 // var2
            state.GFrame.define(state.name, result)
        else:
            interpret.err(" běhová chyba interpretace", 53)
            exit(53)


    def LT(self, state):
        print(state.order)

    def GT(self, state):
        print(state.order)

    def EQ(self, state):
        print(state.order)

    def AND(self, state):
        print(state.order)

    def OR(self, state):
        print(state.order)

    def NOT(self, state):
        print(state.order)

    def STR2INT(self, state):
        state.name = state.arg1[3:]
        if state.GFrame.get(state.name) is None or int(state.arg3) < 0 or int(state.arg3) > len(state.arg2):
            interpret.err("běhová chyba interpretace", 54)
            exit(54)
        result = state.arg2[int(state.arg3)]
        result = ord(result)
        print(state.arg2, result)
        state.GFrame.define(state.name, result)


    def INT2CHAR(self, state):
        state.name = state.arg1[3:]
        if state.GFrame.get(state.name) is None:
            interpret.err("běhová chyba interpretace", 54)
            exit(54)
        var1 = int(state.arg2)
        result = chr(var1)
        if var1 < 0 or var1 > 1114111:
            interpret.err("běhová chyba interpretace!", 58)
            exit(58)
        state.GFrame.define(state.name, result)

    def READ(self, state):
        print(state.order)

    def WRITE(self, state):
        if state.arg1 == 'nil@nil':
            print("")
        print(state.arg1, " ")

    def CONCAT(self, state):
        print(state.order)

    def STRLEN(self, state):
        print(state.order)

    def GETCHAR(self, state):
        print(state.order)

    def SETCHAR(self, state):
        print(state.order)

    def TYPE(self, state):
        print(state.order)

    def LABEL(self, state):
        print(state.order)

    def JUMP(self, state):
        print(state.order)

    def JUMPIFEQ(self, state):
        print(state.order)

    def JUMPIFNEQ(self, state):
        print(state.order)

    def EXIT(self, state):
        print(state.order)

    def DPRINT(self, state):
        print(state.order)

    def BREAK(self, state):
        print(state.order)


class State:
    def __init__(self, order=1, numOfArgs=0, GFrame=None, root=None, name=None, arg1=None, arg2=None, arg3=None, type1=None, type2=None, type3=None):
        self.order = order
        self.numOfArgs = numOfArgs
        self.GFrame = GFrame
        self.root = root
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.type1 = type1
        self.type2 = type2
        self.type3 = type3


class GlobalFrame:
    def __init__(self):
        self.variables = {}

    def define(self, name, value):
        self.variables[name] = value

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        else:
            return None

    def __repr__(self):
        return f"GlobalFrame({self.variables})"


class DType:
    INT = 'int'
    BOOL = 'bool'
    NIL = 'nil'
    STR = 'string'
    FLOAT = 'float'
    UNDEFINED = ''
