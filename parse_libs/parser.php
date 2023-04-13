<?php
/**
 * Autor: Michal Novák
 * Login: xnovak3g
 * Datum: 13.03.2023
 */

include_once "vars.php";

// zjednodušená pravidla neuvažující ani základní kontrolu sémantiky operandu
// způsob uspořádání dat: seznam instrukcí, seznam možných argumentů
$RULE_SET = array(
    array( 
        "_MOVE__NOT__INT2CHAR__STRLEN__TYPE_", // instrukce
        array(Types::Var), // arg1
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil) ), //arg2 
    array( "_CREATEFRAME__PUSHFRAME__POPFRAME__RETURN__BREAK_" ),
    array( "_DEFVAR__POPS_", 
        array(Types::Var) ),
    array( "_CALL__LABEL__JUMP_", 
        array(Types::Label) ),
    array( "_PUSHS__WRITE__DPRINT_", 
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil) ),
    array( "_ADD__SUB__MUL__IDIV__LT__GT__EQ__AND_OR__STRI2INT__GETCHAR__CONCAT__SETCHAR_", 
        array(Types::Var), 
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil), 
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil) ),
    array( "_READ_",  
        array(Types::Var), 
        array(Types::Type)),
    array("_JUMPIFEQ__JUMPIFNEQ_", 
        array(Types::Label), 
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil), 
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil) ),
    array( "_EXIT_", 
        array(Types::Var, Types::String, Types::Bool, Types::Int, Types::Nil) )
);

function check_line($line){
    global $RULE_SET;

    $instruction = $line[0]->identif;

    if($line[0]->type == Types::Header){
        fwrite(STDERR, "ERROR:: Prebyvajici hlavicka!\n");
            exit(UnknownCode_Error);
    }

    $found = false;
    foreach($RULE_SET as $rule){
        if(str_contains($rule[0], strtoupper("_".$instruction."_")) && (count($rule) == count($line))){
            if(count($rule) == 1)
                $found = true;
            for($i = 1; $i < count($rule); $i++){
                if(!in_array($line[$i]->type, $rule[$i], true)){
                    $found = false;
                    break;
                }
                else
                    $found = true;
            }
        }
    }
    if(!$found){
        fwrite(STDERR, "ERROR:: rule for <$instruction> with operands:");
        for($i = 1; $i < count($line); $i++){
            $output=$line[$i]->identif;
            fwrite(STDERR, " <$output>");
        }
        fwrite(STDERR, " not found!\n");
        exit(LexSyn_Error);
    }
}

function syntax_check($code_lines){

    if(empty($code_lines)) // soubor neobsahoval kod
        return;

    if($code_lines[0][0]->type != Types::Header){ // soubor bez hlavičky
        fwrite(STDERR, "ERROR:: Chybejici nebo chybna hlavicka souboru!\n");
            exit(Header_Error);
    }
    for($i = 1; $i < count($code_lines); $i++){ // zpracování jednotlivých instrukcí
        check_line($code_lines[$i]);
    }
}

?>