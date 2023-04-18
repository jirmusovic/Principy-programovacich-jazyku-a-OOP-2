## Implementační dokumentace k 2. úloze do IPP 2022/2023
### Jméno a příjmení: Veronika JIrmusová<br>Login: xjirmu00
<br>

### Architektura

Architektonický návrh je popsán následujícím diagramem tříd, ve kterém je znázorněna komunikace mezi vytvořenými třídami.<br>
![diagram tříd](/graph.png "diagram tříd")<br>

### Implementace:
Program funguje na principu objektové orientace a sestává ze dvou vzájemně komunikujících modulů: instructions.py a interpret.py.<br>
Soubor instructions.py obsahuje definice všech tříd a jejich metod. Nejobsáhlejší je třída Instruction, se kterou lze pomocí jiné třídy State komunikovat. Stará se jak o zpracování všech instrukcí, tak o zjišťování informací. Dále také vrací do souboru interpret.py informaci o správném počtu argumentů, který je porovnává se zadanými hodnotami. Další třídy se starají o vytváření potřebných framů.<br>
Interpret.py zpracovává argumenty a poté rozkládá pomocí knihovny *xml.etree.ElementTree* přijatý XML soubor na strom, ze kterého pak vytěžuje potřebná data. Předává souboru instrictions.py informace o instrukci a jejích atributech pomocí třídy Sate.

### Testování:
Testování bylo prováděno na dvou zařízeních, Windows 11 a Windows 10. Na druhém zařízení byl program spuštěn a otestován i na vurtuálním stroji Ubuntu 20.4.
Program byl důkladně testován vkládáním XML zpráv do testovacího souboru xml.xml, přičemž se porovnávaly výstupy s očekávanými výstupy. Vstupní hodnoty byly čerpány z poskytnutých testů v informačním systému a také od kolegů, kteří své testovací sady sdíleli jako volné dílo, mohli jsme je tedy využít. Testovacích souborů je však obrovské množství, nebudu je tedy odevzdávat společně s projektem, ale na vyžádání je mohu poskytnout k nahlédnutí.<br>
Časté chyby při testování byly převážně chyby takové, že např. v souboru XML byla použita proměnná, která nebyla předem deklarována, tedy ani rámec nebyl inicializován. Program ukončil běh s chybovou hodnotou neexistujícího rámce, v testech se však očekávalo ukončení z důvodu nedeklarované proměnné. Tato skutečnost v kódu změněna nebyla, protože mi zde příjdou obě varianty správně.

### Limitace:
Instrukce *BREAK* nebyla z důvodu špatného plánování implementována.

### Licence:
Softwarové produkty v tomto projektu jsou dostupné pod licencí MIT, viz níže.


Copyright (c) 2023 Veronika Jirmusová

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    - The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    - The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.

    - The authors or copyright holders shall not be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

### Zdroje:
Generace grafu: https://pylint.readthedocs.io/en/latest/pyreverse.html
Python3: https://diveintopython3.net/
Syntax: https://peps.python.org/pep-0008/#designing-for-inheritance
Práce se stromem při členění XML souboru: https://docs.python.org/release/3.10.6/library/xml.etree.elementtree.html
