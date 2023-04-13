<?php
/**
 * Autor: Michal Novák
 * Login: xnovak3g
 * Datum: 13.03.2023
 */

include_once 'vars.php';

/**
 * Získání datového typu z vnitřní reprezentace
 */
function type_parser($type){
    switch($type){
        case Types::Int:
            return "int";
        case Types::Bool:
            return "bool";
        case Types::String:
            return "string";
        case Types::Nil:
            return "nil";
        case Types::Label:
            return "label";
        case Types::Type:
            return "type";
        case Types::Var:
            return "var";
    }
}

/**
 * Generace výstupního XML formátu
 */
function generate_xml($code){
    // Inicializace výstupu a formátu
    $xml = new XMLWriter(); 
    $xml->openMemory();
    $xml->setIndent(true); // povolení indentace
    $xml->setIndentString("\t"); // nastavení indentace na tabelátor
    // povinná hlavička
    $xml->startDocument('1.0', 'UTF-8');
    $xml->startElement('program');
    $xml->startAttribute('language');
    $xml->text('IPPcode23');
    
    // zpracování jednotlivých instrukcí
    for($i = 1; $i < count($code); $i++){
        $line = $code[$i];
        $xml->startElement('instruction');

        $xml->startAttribute('order');
        $xml->text($i);
        $xml->endAttribute();

        $xml->startAttribute('opcode');
        $xml->text(strtoupper($line[0]->identif));
        $xml->endAttribute();

        // operandy instrukce
        for($j = 1; $j < count($line); $j++){
            $xml->startElement('arg'.$j);

            $xml->startAttribute('type');
            $xml->text(type_parser($line[$j]->type));
            $xml->endAttribute();

            $xml->text($line[$j]->identif);
            
            $xml->endElement();
        }

        $xml->endElement();
    }
    
    // ukončení souboru
    $xml->endAttribute();
    $xml->endElement();
    $xml->endDocument();

    echo $xml->outputMemory(); // výpis XML
}

?>