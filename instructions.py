import re
import sys
import traceback
from typing import Optional, List
import xml.etree.ElementTree as eet
import argparse
import interpret


class Instruction:

    def __init__(self, file):
        self.file = file
        self.name = None
        self.order = None
        self.temp_frame = None
        self.loc_frame = LocalFrame()
        self.glob_frame = GlobalFrame()
        self.stack = []
        self.labels = {}
        self.call_stack = []
        
    def get_value_type(self, arg, type):
        if type == "var":
            state = self.get_state(arg)
            if state == 1:
                if not self.glob_frame.is_defined(arg):
                    exit(54)
                return self.glob_frame.get(arg)
            if state == 2:
                if not self.loc_frame.is_defined(arg):
                    exit(54)
                return self.loc_frame.get(arg)
            if state == 3:
                if self.temp_frame == None:
                    exit(54)
                if not self.temp_frame.is_defined(arg):
                    exit(54)
                return self.temp_frame.get(arg)
        elif type == "int":
            if not re.match('^-?\d+$', arg):
                exit(32)
            return int(arg), type
        elif type == "string":
            # vymeni escape sekvence za znaky
            if arg == None:
                return "", "string"
            new = ''
            i = 0
            while i < len(arg):
                if arg[i] == '/' and i < len(arg) - 3 and arg[i+1:i+4].isdigit():
                    new += chr(int(arg[i+1:i+4]))
                    i += 4
                else:
                    new += arg[i]
                    i += 1
            return new, "string"

        elif type == "bool":
            if arg.upper() == "TRUE":
                return True, type
            else:
                return False, type
        elif type == "nil":
            return None, type
        elif type == "type":
            return arg, type
        
        
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
                or opcode == "NOT" or opcode == "CONCAT" or opcode == "STRI2INT" or opcode == "SETCHAR" or opcode == "JUMPIFEQ" or opcode == "JUMPIFNEQ":
            return 3
        else:
            interpret.err("Neocekavana XML struktura!", 32)
            return -1

    def get_state(self, arg):
        if arg.startswith("GF@"):
            return 1
        if arg.startswith("LF@"):
            return 2
        if arg.startswith("TF@"):
            return 3
        else:
            sys.exit(54)

    def get_frame(self, arg):
        if arg.startswith("GF@"):
            return self.glob_frame
        if arg.startswith("LF@"):
            return self.loc_frame
        if arg.startswith("TF@"):
            return self.temp_frame
        exit(32)
    

    def get_input(self):
        try:
            if self.file == sys.stdin:
                return input()
            else:
                string = self.file.readline()
                return string.rstrip("\n")
        except:
            return None

    def MOVE(self, state):
        if state.type1 != "var":
            sys.exit(53)
        val, type = self.get_value_type(state.arg2, state.type2)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        frame.define(state.arg1, val, type)

    def DEFVAR(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(55)
        frame.define(state.arg1, None, None)

    def CALL(self, state):
        if state.type1 != "label":
                exit(53)
        self.call_stack.append(self.order+1)
        return self.labels[state.arg1] 

    def RETURN(self, state):
        if len(self.call_stack) < 1:
            exit(56)
        return self.call_stack.pop()

    def PUSHS(self, state):
        val, type = self.get_value_type(state.arg1, state.type1)
        self.stack.append([val, type])

    def POPS(self, state):
        if len(self.stack) < 0:
            exit(56)
        if state.type2 != "var":
            exit(53)
        frame = self.get_frame(state.arg2)
        valtype = self.stack.pop()
        frame.define(valtype[0], valtype[1])

    def ADD(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)

        if type1 != "int" or type2 != "int":
            exit(53)
        
        frame.define(state.arg1, val1+val2, "int")
        

    def SUB(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)

        if type1 != "int" or type2 != "int":
            exit(53)
        
        frame.define(state.arg1, val1-val2, "int")

    def MUL(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)

        if type1 != "int" or type2 != "int":
            exit(53)
        
        frame.define(state.arg1, val1*val2, "int")

    def IDIV(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)

        if type1 != "int" or type2 != "int":
            exit(53)
        
        if(val2 == 0):
            exit(52)

        frame.define(state.arg1, val1/val2, "int")


    def LT(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != type2 or type1 == "nil" or type2 == "nil":
            exit(53)
        if val1 < val2:
            frame.define(state.arg1, True, "bool")
        else:
            frame.define(state.arg1, False, "bool")

    def GT(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != type2 or type1 == "nil" or type2 == "nil":
            exit(53)
        if val1 > val2:
            frame.define(state.arg1, True, "bool")
        else:
            frame.define(state.arg1, False, "bool")

    def EQ(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 == type2:
            if val1 == val2:
                frame.define(state.arg1, True, "bool")
            else:
                frame.define(state.arg1, False, "bool")
        else:
            frame.define(state.arg1, False, "bool")

    def AND(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != "bool" or type2 != "bool":
            exit(53)
        frame.define(state.arg1, val1 and val2, "bool")

    def OR(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != "bool" or type2 != "bool":
            exit(53)
        frame.define(state.arg1, val1 or val2, "bool")

    def NOT(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)

        if type1 != "bool" :
            exit(53)
        frame.define(state.arg1, not val1, "bool")

    def STRI2INT(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != "string" or type != "int":
            exit(53)
        if val2 > len(val1) or val2 < 0:
            exit(58)
        frame.define(state.arg1, ord(val1[val2]), "int")


    def INT2CHAR(self, state):
        print(state.order)

    def READ(self, state):
        if state.type1 != "var" or state.type2 != "type":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        string = self.get_input()
        
        if string == None:
            frame.define(state.arg1, None, "nil")
        elif state.arg2 == "string":
            frame.define(state.arg1, string, "string")
        elif state.arg2 == "int":
            if not re.match('^-?\d+$', string):
                exit(53)
            frame.define(state.arg1, int(string), "int")
        elif state.arg2 == "bool":
            if string.upper() == "TRUE":
                frame.define(state.arg1, True, "bool")
            else:
                frame.define(state.arg1, False, "bool")

    def WRITE(self, state):
        val, type = self.get_value_type(state.arg1, state.type1)
        if type == "string" or type == "int":
            print(val, end="")
        elif type == "bool":
            if val:
                print("true", end="")
            else:
                print("false", end="")
        elif type == "nil":
            print("", end="")


    def CONCAT(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)

        if type1 != "string" or type2 != "string":
            exit(53)
        
        frame.define(state.arg1, val1+val2, "string")

    def STRLEN(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        if type1 != "string":
            exit(53)
        frame.define(state.arg1, len(val1), "int")

    def GETCHAR(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != "string" or type != "int":
            exit(53)
        if val2 > len(val1) or val2 < 0:
            exit(58)
        frame.define(state.arg1, val1[val2], "int")

    def SETCHAR(self, state):
        print(state.order)

    def TYPE(self, state):
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(54)
        _, type = self.get_value_type(state.arg2, state.type2)
        frame.define(state.arg1, type, "string")


    def LABEL(self, state):
        if state.type1 != "label":
            exit(53)
        self.labels[state.arg1] = state.order

    def JUMP(self, state):
        if state.type1 != "label":
            exit(53)
        if state.arg1 not in self.labels.keys():
            exit(55)
        return self.labels[state.arg1]

    def JUMPIFEQ(self, state):
        if state.type1 != "label":
            exit(53)
        if state.arg1 not in self.labels.keys():
            exit(52)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 == type2:
            if val1 == val2:
                return self.labels[state.arg1]
        elif type1 == "nil" or type2 == "nil":
            return None
        exit(53)


    def JUMPIFNEQ(self, state):
        if state.type1 != "label":
            exit(53)
        if state.arg1 not in self.labels.keys():
            exit(52)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 == type2:
            if val1 != val2:
                return self.labels[state.arg1]
            return None
        elif type1 == "nil" or type2 == "nil":
            return self.labels[state.arg1]
        exit(53)
        

    def EXIT(self, state):
        print(state.order)

    def DPRINT(self, state):
        print(state.order)

    def BREAK(self, state):
        print(state.order)
        
    def CREATEFRAME(self, state):
        self.temp_frame = TemporalFrame()
        
    def POPFRAME(self, state):
        self.temp_frame = self.loc_frame.pop()
        
    def PUSHFRAME(self, state):
        if self.temp_frame == None:
            interpret.err("ramec neexistuje!")
            sys.exit(55)
        self.loc_frame.push(self.temp_frame.variables)
        self.temp_frame = None



class State:
    def __init__(self, order=1, numOfArgs=0, root=None, name=None, arg1=None, arg2=None, arg3=None, type1=None, type2=None, type3=None):
        self.order = order
        self.numOfArgs = numOfArgs
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

    def define(self, name, value, type):
        self.variables[name] = [value, type]

    def is_defined(self, name):
        if name not in self.variables:
            return False
        if self.variables[name][0] == None and self.variables[name][1] == None:
            return False
        return True

    def get(self, name):
        if name in self.variables:
            return self.variables[name][0], self.variables[name][1]
        else:
            exit(54)

    def __repr__(self):
        return f"GlobalFrame({self.variables})"
    
class LocalFrame:
    def __init__(self):
        self.frames = []
        
    def push(self, frame):
        newframe = {}
        for var in frame.keys():
            newframe["LF"+var[2:]] = frame[var]
        self.frames.append(newframe)
    
    def pop(self):
        newframe = {}
        if len(self.frames) > 0:
            for var in self.frames[len(self.frames) - 1].keys():
                newframe["TF"+var[2:]] = self.frames[len(self.frames) - 1][var]
            return newframe
        else:
            interpret.err("ramec neexistuje!")
            sys.exit(55)

    def define(self, name, value, type):
        if len(self.frames) > 0:
            self.frames[len(self.frames) - 1][name] = [value, type]
        else:
            interpret.err("ramec neexistuje!")
            sys.exit(55)

    def is_defined(self, name):
        if len(self.frames) <= 0:
            return False
        if name not in self.frames[len(self.frames) - 1]:
            return False
        if self.frames[len(self.frames) - 1][name][0] == None and self.frames[len(self.frames) - 1][name][1] == None:
            return False
        return True

    def get(self, name):
        if len(self.frames) > 0:
            if name in self.frames[len(self.frames) - 1]:
                return self.frames[len(self.frames) - 1][name][0], self.frames[len(self.frames) - 1][name][1]
            else:
                exit(54)
        else:
            interpret.err("ramec neexistuje!")
            sys.exit(55)

    def __repr__(self):
        return f"LocalFrame({self.variables})"
    
class TemporalFrame:
    def __init__(self):
        self.variables = {}

    def define(self, name, value, type):
        self.variables[name] = [value, type]

    def is_defined(self, name):
        if name not in self.variables:
            return False
        if self.variables[name][0] == None and self.variables[name][1] == None:
            return False
        return True

    def get(self, name):
        if name in self.variables:
            return self.variables[name][0], self.variables[name][1]
        else:
            exit(54)

    def __repr__(self):
        return f"TemporalFrame({self.variables})"


class DType:
    INT = 'int'
    BOOL = 'bool'
    NIL = 'nil'
    STR = 'string'
    FLOAT = 'float'
    UNDEFINED = ''
