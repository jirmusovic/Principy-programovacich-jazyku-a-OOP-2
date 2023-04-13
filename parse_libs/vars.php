<?php
/**
 * Autor: Michal Novák
 * Login: xnovak3g
 * Datum: 13.03.2023
 */


$instruction_set = array( "MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK");

enum Types{
    case Instruction;
    case Int;
    case Bool;
    case String;
    case Nil;
    case Label;
    case Type;
    case Var;
    case Comment;
    case Error;
    case Header;
}

const Param_Error = 10; //chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů
const Open_Error = 11; //chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění)
const WriteOpen_Error = 12; //chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba)
const Header_Error = 21; //chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode23
const UnknownCode_Error = 22; //neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode23
const LexSyn_Error = 23; //jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode23
const Internal_Error = 99; //interní chyba (neovlivněná vstupními soubory či parametry příkazové řádky; např. chyba alokace paměti)


class Token{
    public $identif;
    public $type;

    public function __construct($identif, $type){
        $to_replace = array("bool@", "nil@", "int@", "string@");
        $identif = str_replace($to_replace, "", $identif);
        $this->identif = $identif;
        $this->type = $type;
    }
} 

?>