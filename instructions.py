"""
@author Veronika Jirmusova xjirmu00
@file instructions.py
@brief File with all the classes that are used to work with given instructions.
@since 12.04.2023
"""
import re
import sys
from typing import Optional, List
import xml.etree.ElementTree as eet
import interpret

# Main class with all the known instructions 
class Instruction:

    # Constructor method
    def __init__(self, file):
        self.file = file
        if file != sys.stdin:
            self.input_lines = file.readlines()
            self.input_lines.reverse()
        self.name = None
        self.order = None
        self.temp_frame = None
        self.loc_frame = LocalFrame()       # Initialization of a Local frame
        self.glob_frame = GlobalFrame()     # Initialization of a Global frame frame
        self.stack = []                 
        self.labels = {}
        self.call_stack = []
        
    # Metod to get the type of the variable
    def get_value_type(self, arg, type):
        if type == "var":
            # Check which frame the variable is defined in and return its value
            state = self.get_state(arg)
            # Global frame
            if state == 1:
                if not self.glob_frame.is_defined(arg):
                    interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
                    exit(54)                                # Variable is not defined in global frame
                if not self.glob_frame.has_value(arg):
                    interpret.err("Běhová chyba interpretace – chybějící hodnota", 56)
                    exit(56)                                # Variable in global frame has no value
                return self.glob_frame.get(arg)
            # Local frame
            if state == 2:
                if not self.loc_frame.is_defined(arg):
                    interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
                    exit(54)
                if not self.loc_frame.has_value(arg):
                    interpret.err("Běhová chyba interpretace – chybějící hodnota", 56)
                    exit(56)
                return self.loc_frame.get(arg)
            # Temporary frame
            if state == 3:
                if self.temp_frame == None:
                    interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
                    exit(55)                                # Temporary frame does not exist     
                if not self.temp_frame.is_defined(arg):
                    interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
                    exit(54)
                if not self.temp_frame.has_value(arg):
                    interpret.err("Běhová chyba interpretace – chybějící hodnota", 56)
                    exit(56)
                return self.temp_frame.get(arg)
        
        elif type == "int":
            # Check if argument is a valid integer and return it with the type
            if not re.match('^-?\d+$', arg):
                exit(32)
            return int(arg), type
        
        elif type == "string":
            # Replace escape sequences with characters in the string argument
            if arg == None:
                return "", "string"

            str = ""
            i = 0
            while i < len(arg):
                if arg[i] == '\\' and i < len(arg) - 3 and arg[i+1:i+4].isdigit():
                    str += chr(int(arg[i+1:i+4]))
                    i += 4
                else:
                    str += arg[i]
                    i += 1
            
            return str, "string"

        elif type == "bool":
            # Check if argument is a boolean and return it with the type
            if arg.upper() == "TRUE":
                return True, type
            else:
                return False, type
        elif type == "nil":
            # Check if argument is nil and then return None
            return None, type
        elif type == "type":
            # Return argument with the type
            return arg, type
        
    # Check how many arguments is each instruction supposed to have
    def how_many_args(self, opcode):
        if opcode == "CREATEFRAME" or opcode == "PUSHFRAME" or opcode == "POPFRAME" or opcode == "RETURN" or opcode == "BREAK":
            return 0
        if opcode == "DEFVAR" or opcode == "POPS" or opcode == "CALL" or opcode == "LABEL" or opcode == "JUMP" \
                or opcode == "WRITE" or opcode == "EXIT" or opcode == "PUSHS" or opcode == "DPRINT":
            return 1
        if opcode == "MOVE" or opcode == "INT2CHAR" or opcode == "STRLEN" or opcode == "TYPE" or opcode == "READ" or opcode == "NOT":
            return 2
        if opcode == "ADD" or opcode == "SUB" or opcode == "MUL" or opcode == "IDIV" or opcode == "LT" or opcode == "GT" \
                or opcode == "EQ" or opcode == "GETCHAR" or opcode == "AND" or opcode == "OR" \
                or opcode == "CONCAT" or opcode == "STRI2INT" or opcode == "SETCHAR" or opcode == "JUMPIFEQ" or opcode == "JUMPIFNEQ":
            return 3
        else:
            interpret.err("Neocekavana XML struktura!", 32)
            return -1

    # Get state of each variable and decide in what frame was it put
    def get_state(self, arg):
        if arg.startswith("GF@"):
            return 1
        if arg.startswith("LF@"):
            return 2
        if arg.startswith("TF@"):
            return 3
        else:
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            sys.exit(54)

    # # Get state of each variable and decide in what frame was it put and return given frame
    def get_frame(self, arg):
        if arg.startswith("GF@"):
            return self.glob_frame
        if arg.startswith("LF@"):
            return self.loc_frame
        if arg.startswith("TF@"):
            return self.temp_frame
        exit(32)
    
    # Get input
    def get_input(self):
        try:
            if self.file == sys.stdin:
                # Read input from standard input if the input file is the same as the system standard input
                return input()
            else:
                # Read input from the input file and remove the newline character at the end
                string = self.input_lines.pop()
                string = string.rstrip()
                return string
        except:
            # Return None if an error occurs while reading input
            return None

    """
    Instruction methods
    """
    
    # Takes value from the second param and moves it into the first one
    def MOVE(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            sys.exit(53)
            # Get value, frame and type o the second argument
        val, type = self.get_value_type(state.arg2, state.type2)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        frame.define(state.arg1, val, type)

    # Defines variable (if not alredy defined) in wanted frame
    def DEFVAR(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Get frame of the variable
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if frame.is_defined(state.arg1):
            interpret.err("Chyba při sémantických kontrolách vstupního kódu v IPPcode23", 52)
            exit(52)
        frame.define(state.arg1, "empty", "empty")

    # Saves incremented order into stack
    def CALL(self, state):
        # Check if given arguments are correct types
        if state.type1 != "label":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if state.arg1 not in self.labels.keys():
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        # Append object to the end of a list
        self.call_stack.append(state.order + 1)
        return self.labels[state.arg1] 

    # Move to the position saved by 'CALL'
    def RETURN(self, state):
        if len(self.call_stack) < 1:
            interpret.err("Běhová chyba interpretace – chybějící hodnota", 56)
            exit(56)
        return self.call_stack.pop()

    # Put a value of wanted variable on the top of a stack
    def PUSHS(self, state):
        val, type = self.get_value_type(state.arg1, state.type1)
        self.stack.append([val, type])

    # Pop a value from the top of a stack
    def POPS(self, state):
        if len(self.stack) < 0:
            interpret.err("Běhová chyba interpretace – chybějící hodnota", 56)
            exit(56)
        # Check if given arguments are correct types
        if state.type2 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg2)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        valtype = self.stack.pop()
        frame.define(valtype[0], valtype[1])

    # Add the values of the second and third given attributes and put the result into the first variable
    def ADD(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "int" or type2 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        
        frame.define(state.arg1, val1+val2, "int")
        

    # Subtract the values of the second and third given attributes and put the result into the first variable
    def SUB(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "int" or type2 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        
        frame.define(state.arg1, val1-val2, "int")

    # Multiply the values of the second and third given attributes and put the result into the first variable
    def MUL(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "int" or type2 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        
        frame.define(state.arg1, val1*val2, "int")

    # Divide the values of the second and third given attributes and put the result into the first variable
    def IDIV(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "int" or type2 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        
        if(val2 == 0):
            interpret.err("Běhová chyba interpretace – špatná hodnota operandu", 57)
            exit(57)

        frame.define(state.arg1, val1//val2, "int")

    # Less than
    def LT(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Get frame or variable
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != type2 or type1 == "nil" or type2 == "nil":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if val1 < val2:
            frame.define(state.arg1, True, "bool")
        else:
            frame.define(state.arg1, False, "bool")

    # Greater than
    def GT(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Get frame os variable
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 != type2 or type1 == "nil" or type2 == "nil":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if val1 > val2:
            frame.define(state.arg1, True, "bool")
        else:
            frame.define(state.arg1, False, "bool")

    # Equals
    def EQ(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Get frame of variable
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 == type2:
            if val1 == val2:
                frame.define(state.arg1, True, "bool")
            else:
                frame.define(state.arg1, False, "bool")
        else:
            if type1 == "nil" or type2 == "nil":
                if val1 == val2:
                    frame.define(state.arg1, True, "bool")
                else:
                    frame.define(state.arg1, False, "bool")
            else:
                interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
                exit(53)

    # Logical and
    def AND(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Get frame of variable
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "bool" or type2 != "bool":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame.define(state.arg1, val1 and val2, "bool")

    # Logical or
    def OR(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Get frame of variable
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "bool" or type2 != "bool":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame.define(state.arg1, val1 or val2, "bool")

    # Logical not
    def NOT(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get value and its type
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        # Check if given arguments are correct types
        if type1 != "bool" :
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame.define(state.arg1, not val1, "bool")

    # Converts a string type value to int type value
    def STRI2INT(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get values and their types
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "string" or type2 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if val2 >= len(val1) or val2 < 0:
            interpret.err("Běhová chyba interpretace – chybná práce s řetězcem", 58)
            exit(58)
        frame.define(state.arg1, ord(val1[val2]), "int")

    # Converts a int type value to char type value
    def INT2CHAR(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        # Get value and its type
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        # Check if given arguments are correct types
        if type1 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        # Check if value is in ASCII range
        if val1 < 0 or val1 > 0x10ffff:
            interpret.err("Běhová chyba interpretace – chybná práce s řetězcem", 58)
            exit(58)
        frame.define(state.arg1, chr(val1), "string")

    # 
    def READ(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var" or state.type2 != "type":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        string = self.get_input()
        # Check type
        if string == None:
            frame.define(state.arg1, None, "nil")
            return None
        if state.arg2 == "string":
            frame.define(state.arg1, string, "string")
        if state.arg2 == "int":
            if not re.match('^-?\d+$', string):
                frame.define(state.arg1, "", "nil")
            else:
                frame.define(state.arg1, int(string), "int")
        if state.arg2 == "bool":
            if string.upper() == "TRUE":
                frame.define(state.arg1, True, "bool")
            else:
                frame.define(state.arg1, False, "bool")

    def WRITE(self, state):
        # Get and then check value and type
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
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "string" or type2 != "string":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        
        frame.define(state.arg1, val1+val2, "string")

    def STRLEN(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        # Check if given arguments are correct types
        if type1 != "string":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame.define(state.arg1, len(val1), "int")

    def GETCHAR(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type1 != "string" or type2 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if val2 >= len(val1) or val2 < 0:
            interpret.err("Běhová chyba interpretace – chybná práce s řetězcem", 58)
            exit(58)
        frame.define(state.arg1, val1[val2], "string")

    def SETCHAR(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
        val0, type0 = self.get_value_type(state.arg1, state.type1)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        # Check if given arguments are correct types
        if type0 != "string" or type1 != "int" or type2 != "string":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if val1 >= len(val0) or val1 < 0 or len(val2) < 1:
            interpret.err("Běhová chyba interpretace – chybná práce s řetězcem", 58)
            exit(58)
        string = ""
        for i in range(0, len(val0)):
            if i == val1:
                string += val2[0]
            else:
                string += val0[i]

        frame.define(state.arg1, string, "string")

    def TYPE(self, state):
        # Check if given arguments are correct types
        if state.type1 != "var":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        frame = self.get_frame(state.arg1)
        if frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        if not frame.is_defined(state.arg1):
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)
            
        _, type1 = self.get_value_type(state.arg2, state.type2)
        frame.define(state.arg1, type1, "string")


    def LABEL(self, state):
        # Check if given arguments are correct types
        if state.type1 != "label":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        self.labels[state.arg1] = state.order

    def JUMP(self, state):
        # Check if given arguments are correct types
        if state.type1 != "label":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if state.arg1 not in self.labels.keys():
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            exit(55)
        return self.labels[state.arg1]

    def JUMPIFEQ(self, state):
        # Check if given arguments are correct types
        if state.type1 != "label":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if state.arg1 not in self.labels.keys():
            interpret.err("Chyba při sémantických kontrolách vstupního kódu v IPPcode23", 52)
            exit(52)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 == type2:
            if val1 == val2:
                return self.labels[state.arg1]
        elif type1 == "nil" or type2 == "nil":
            return None
        else:
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)


    def JUMPIFNEQ(self, state):
        # Check if given arguments are correct types
        if state.type1 != "label":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if state.arg1 not in self.labels.keys():
            interpret.err("Chyba při sémantických kontrolách vstupního kódu v IPPcode23", 52)
            exit(52)
        val1, type1 = self.get_value_type(state.arg2, state.type2)
        val2, type2 = self.get_value_type(state.arg3, state.type3)
        if type1 == type2:
            if val1 != val2:
                return self.labels[state.arg1]
            return None
        elif type1 == "nil" or type2 == "nil":
            return self.labels[state.arg1]
        interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
        exit(53)
        

    def EXIT(self, state):
        val1, type1 = self.get_value_type(state.arg1, state.type1)
        # Check if given arguments are correct types
        if type1 != "string" and type1 != "int":
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if type1 == "string" and not type1.isdigit():
            interpret.err("Běhová chyba interpretace – špatné typy operandů", 53)
            exit(53)
        if int(val1) < 0 or int(val1) > 49:
            interpret.err("Běhová chyba interpretace – špatná hodnota operandu", 57)
            exit(57)
        exit(int(val1))

    def DPRINT(self, state):
        print(state.order)

    def BREAK(self, state):
        print(state.order)
        
    def CREATEFRAME(self, state):
        self.temp_frame = TemporalFrame()
        
    def POPFRAME(self, state):
        self.temp_frame = TemporalFrame()
        self.temp_frame.variables = self.loc_frame.pop()
        
    def PUSHFRAME(self, state):
        if self.temp_frame == None:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            sys.exit(55)
        self.loc_frame.push(self.temp_frame.variables)
        self.temp_frame = None


# Class for transfering information about instruction
class State:
    def __init__(self, order=1, numOfArgs=0, root=None, name=None, arg1=None, arg2=None, arg3=None, type1=None, type2=None, type3=None):
        self.order = order          # Order of instruction
        self.numOfArgs = numOfArgs  # Number of arguments
        self.root = root            # Root
        self.name = name            # Name of instruction
        self.arg1 = arg1            # First argument (if present)
        self.arg2 = arg2            # Second argument (if present)
        self.arg3 = arg3            # Third argument (if present)
        self.type1 = type1          # Type of the first argument (if present)
        self.type2 = type2          # Type of the second argument (if present)
        self.type3 = type3          # Type of the third argument (if present)

# Class for a Global Frame
class GlobalFrame:
    # Initialization of an empty frame
    def __init__(self):
        self.variables = {}

    # Defining variable in Global Frame with its type
    def define(self, name, value, type):
        self.variables[name] = [value, type]

    # Check if given variable is already defined
    def is_defined(self, name):
        if name not in self.variables:
            return False
        return True
        
    # Check whether given variable has a value or not
    def has_value(self, name):
        if self.variables[name][0] == "empty" and self.variables[name][1] == "empty":
            return False
        return True

    # Get the value of given variable
    def get(self, name):
        if name in self.variables:
            return self.variables[name][0], self.variables[name][1]
        else:
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)

    # Return a string representation of the object that can be used to recreate the object or display useful information about it
    def __repr__(self):
        return f"GlobalFrame({self.variables})"
    
# Class for a Local Frame
class LocalFrame:
    # Initialization of an empty frame
    def __init__(self):
        self.frames = []
        
    # Add a new frame to the list
    def push(self, frame):
        # Create a new dictionary
        newframe = {}
        # Add each variable to it
        for var in frame.keys():
            # Variable then starts with 'LF'
            newframe["LF"+var[2:]] = frame[var]
        self.frames.append(newframe)
    
    # Remove the most recent frame from the list and terurn its variable
    def pop(self):
        newframe = {}
        # Add each variable in the removed frame to a new dictionary
        if len(self.frames) > 0:
            for var in self.frames[len(self.frames) - 1].keys():
                # Variable then starts with TF
                newframe["TF"+var[2:]] = self.frames[len(self.frames) - 1][var]
            self.frames.pop()
            return newframe
        else:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            sys.exit(55)

    # Add a new variable and its type to the current frame
    def define(self, name, value, type):
        if len(self.frames) > 0:
            self.frames[len(self.frames) - 1][name] = [value, type]
        else:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            sys.exit(55)

    # Check whether a variable with the given name has been defined in the current frame
    def is_defined(self, name):
        if len(self.frames) <= 0:
            return False
        if name not in self.frames[len(self.frames) - 1]:
            return False
        return True
        
    # Check whether a variable with the given name has a non-empty value in the current frame
    def has_value(self, name):
        if len(self.frames) <= 0:
            return False
        if self.frames[len(self.frames) - 1][name][0] == "empty" and self.frames[len(self.frames) - 1][name][1] == "empty":
            return False
        return True
        
    # Retrieve the value and type of the variable with the given name from the current frame
    def get(self, name):
        if len(self.frames) > 0:
            if name in self.frames[len(self.frames) - 1]:
                return self.frames[len(self.frames) - 1][name][0], self.frames[len(self.frames) - 1][name][1]
            else:
                interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
                exit(54)
        else:
            interpret.err("Běhová chyba interpretace – rámec neexistuje", 55)
            sys.exit(55)

    # Return a string representation of the object that can be used to recreate the object or display useful information about it
    def __repr__(self):
        return f"LocalFrame({self.variables})"
    
class TemporalFrame:
    # Initialization of an empty frame
    def __init__(self):
        self.variables = {}

    # Add a new variable and its type to the current frame
    def define(self, name, value, type):
        self.variables[name] = [value, type]

    # Check whether a variable with the given name has been defined in the current frame
    def is_defined(self, name):
        if name not in self.variables:
            return False
        return True
        
    # Check whether a variable with the given name has a non-empty value in the current frame
    def has_value(self, name):
        if self.variables[name][0] == "empty" and self.variables[name][1] == "empty":
            return False
        return True

    # Get the value of given variable
    def get(self, name):
        if name in self.variables:
            return self.variables[name][0], self.variables[name][1]
        else:
            interpret.err("Běhová chyba interpretace – přístup k neexistující proměnné", 54)
            exit(54)

    # Return a string representation of the object that can be used to recreate the object or display useful information about it
    def __repr__(self):
        return f"TemporalFrame({self.variables})"


