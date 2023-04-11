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
                or opcode == "EQ" or opcode == "STR2INT" or opcode == "GETCHAR" or opcode == "AND" or opcode == "OR" \
                or opcode == "NOT" or opcode == "CONCAT" or opcode == "SETCHAR" or opcode == "JUMPIFEQ" or opcode == "JUMPIFNEQ":
            return 3
        else:
            interpret.err("Neocekavana XML struktura!", 32)
            return -1

    def MOVE(self, state):
        print(state.numOfArgs)

    def DEFVAR(self, state):
        print(state.numOfArgs)
    def CALL(self, state):
        print(state.order)

    def RETURN(self, state):
        print(state.order)

    def PUSHS(self, state):
        print(state.order)

    def POPS(self, state):
        print(state.order)

    def ADD(self, state):
        print(state.order)

    def SUB(self, state):
        print(state.order)

    def MUL(self, state):
        print(state.order)

    def IDIV(self, state):
        print(state.order)

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
        print(state.order)

    def INT2CHAR(self, state):
        print(state.order)

    def READ(self, state):
        print(state.order)

    def WRITE(self, state):
        print(state.order)

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
    def __init__(self, order=1, numOfArgs=0):
        self.order = order
        self.numOfArgs = numOfArgs


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
