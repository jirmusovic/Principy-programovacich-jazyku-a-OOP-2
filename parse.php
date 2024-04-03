<?php


ini_set('display_errors', 'stderr');

include 'parse_libs/scanner.php';
include 'parse_libs/parser.php';
include 'parse_libs/generator.php';

// zpracování argumentů programu
$short_options = "h";
$long_options = array("help");
$options = getopt($short_options, $long_options);

if(array_key_exists("h", $options) || array_key_exists("help", $options)){
    if($argc > 2){
        fwrite(STDERR, "Muze byt pouzit pouze prepinac '--help'\n");
        exit(Param_Error);
    }
    echo "Skript typu filtr (parse.phpv jazycePHP 8.1) nacte ze standardniho\nvstupu zdrojovy kod v IPP-code23, zkontroluje lexikalni a syntaktickou\nspravnost kodu a vypise na standardni vystup XML reprezentaci programu.\n";
    echo "\nMozne prepinace:\n\t--help, -h\tvypise na standardni vystup napovedu skriptu\n\n";
    
    return;
}

// lexikální analýza a uložení tokenů
$code_lines = scanner();

// syntaktická a základní sémantická analýza
syntax_check($code_lines);

// generace výstupního XML formátu
generate_xml($code_lines);

exit(0);

?>
