<?php
/**
 * Autor: Michal Novák
 * Login: xnovak3g
 * Datum: 13.03.2023
 */

include_once 'vars.php';

function is_instruction($token){
    global $instruction_set;
    return in_array(strtoupper($token), $instruction_set);
}

function find_type($token, $instruction_expected){
    // regulární výrazy pro povolené tokeny
    $variable_pattern = "/^((LF)|(TF)|(GF))@([-]|[a-z]|[A-Z]|[_$&%*!?])([-]|[a-z]|[A-Z]|[0-9]|[_$&%*!?])*$/";
    $string_pattern = "/^string@(([^\#\\\\\001-\032])|([\\\\][0-9][0-9][0-9]))*$/";
    $int_pattern = "/^(int@[+-]?\d+)$/";
    $bool_pattern = "/^(bool@true)|(bool@false)$/";
    $nil_pattern = "/^nil@nil$/";
    $type_pattern = "/^(int)|(string)|(bool)$/";
    $label_pattern = "/^([-]|[a-z]|[A-Z]|[_$&%*!?])([-]|[a-z]|[A-Z]|[0-9]|[_$&%*!?])*$/";
    $comment_pattern = "/^#/";
    $header_pattern = "/^.IPPcode23$/";

    // zjištění jednotlivých typů
    if($instruction_expected && is_instruction($token))
        return Types::Instruction;
    if(preg_match($header_pattern, $token))
        return Types::Header;
    if(preg_match($comment_pattern, $token))
        return Types::Comment;
    if(preg_match($variable_pattern, $token))
        return Types::Var;
    if(preg_match($int_pattern, $token))
        return Types::Int;
    if(preg_match($bool_pattern, $token))
        return Types::Bool;
    if(preg_match($string_pattern, $token))
        return Types::String;
    if(preg_match($nil_pattern, $token))
        return Types::Nil;
    if(preg_match($type_pattern, $token))
        return Types::Type;
    if(preg_match($label_pattern, $token))
        return Types::Label;

    // token nebyl rozpoznán
    return Types::Error;
}

// funkce lexikální analýzy + uložení tokenů
function scanner(): array{

    $code_array = array(); // výstupní data
    // čtení souboru
    while(!feof(STDIN)){ 
        $line = fgets(STDIN); // načtení řádku

        // zpracování řádku do jednodušší podoby
        $line = str_replace("#", " #", $line); // před komentářem je vždy mezera
        $line = str_replace("# ", "#", $line);
        while(str_contains($line, "\t") || str_contains($line, "  ")){ // odebrání veškerých dvoj-mezer a tabelátorů
            $line = str_replace(array("  ", "\t"), " ", $line);
        }

        $line = trim($line); // odebrání bílých znaků ze začátku a konce řádku

        // ošetření prázdných řádků
        if(!strcmp($line, "")){ 
            continue;
        }
        
        $split_line = explode(' ', $line); // rozdělení řádku do pole
        $operation = array(); // výsledný zpracovaný řádek == instrukce + operandy

        for ($i = 0; $i < count($split_line); $i++) {
            $ret_type = find_type($split_line[$i], $i == 0); // zjištění typu
            if($ret_type == Types::Comment) // v případě komentáře se ukončí zpracování řádku
                break;
            elseif($i == 0 && $ret_type != Types::Instruction && $ret_type != Types::Header){ // lehká invaze ze syntakticé analýzy, nerozpoznaná instrukce
                if(empty($code_array)){
                    fwrite(STDERR, "ERROR:: chyba hlavicky$split_line[$i]\n");
                    exit(Header_Error);
                }
                
                fwrite(STDERR, "ERROR:: neznama instrukce $split_line[$i]\n");
                exit(UnknownCode_Error);
            }
            elseif($ret_type == Types::Error){ // chyba
                fwrite(STDERR, "ERROR:: neznamy operand $split_line[$i]\n");
                exit(LexSyn_Error);
            }
            else{ // token je operand
                $token = new Token($split_line[$i], $ret_type);
                array_push($operation, $token);
            }
        }
        if(!empty($operation)) // prázdný řádek není předán dál
            array_push($code_array, $operation); // přidání zpracovaného řádku pro další operace
    }

    return $code_array; // zpracovaná data pro syntaktickou analýzu a generator
}

?>