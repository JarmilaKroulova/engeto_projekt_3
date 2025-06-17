> Tento návod je psán pro úplného začátečníka – všechny kroky jsou podrobně vysvětleny. 

# Scraping volebních výsledků z volby.cz
Tento skript slouží ke scrapování výsledků voleb do Poslanecké sněmovny z webu [volby.cz](https://www.volby.cz).


## Přílohy:
    - requierements.txt - textový soubor se seznamem potřebných knihoven
    - README.md - tento soubor s popisem projektu, návodem na instalaci a ukázkou spuštění
    - vysledky_usti.csv - ukázkový výstupní csv soubor

## Požadavky pro spuštění
    - Python 3.10+
    - Knihovny jsou vypsány v přiloženém souboru requierements.txt -> je potřeba instalovat, což doporučuji udělat ve virtuálním prostředí:
        - `requests`
        - `beautifulsoup4`

## Doporučený postup: Virtuální prostředí (ve VS Code)
    - otevři soubor main.py
    - v terminálu zadej příkaz, kde venv je jakýkoliv název tvého virtuálního prostředí:     python -m venv venv  
    - dále zadej příkaz, kterým své virtuální prostředí aktivuješ:        source venv/bin/activate    # nebo ve Windows: venv\Scripts\activate     
    - na začátku každého řádku nyní vidíš název svého virtuálního prostředí v kulatých závorkách:       (venv) C:\Users\.....
    - nyní můžeš instalovat knihovny příkazem:      pip install<název knihovny>

Samotný script pak spouštíš v terminálu pomocí <názvu souboru> <"URL požadovaného územního celku"> <jména výstupního csv souboru>
    - např.: python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky_benesov.csv

Výstupem je CSV soubor s volebními výsledky jednotlivých obcí v daném okrese/kraji.
    - např.:
    Kód obce,Název obce,Voliči v seznamu,Vydané obálky,Platné hlasy,Občanská demokratická strana,...
    529303,Benešov,13104,8485,8437,1052,...
    532568,Bernartice,191,148,148,4,...
    ...
