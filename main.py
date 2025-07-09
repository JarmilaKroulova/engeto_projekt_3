"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Jarmila Kroulová
email: jarmilxxx@seznam.cz
"""


import sys
import csv
import time
import re


import requests
from bs4 import BeautifulSoup


def zkontrolovani_vstupu():
    """
    Zkontroluje, zda byly zadány správné argumenty (URL a název CSV souboru) 
    a zda má URL požadovaný tvar.

    Vrací:
    tuple[str, str]: URL a název výstupního souboru.
    
    """
    if len(sys.argv) != 3:
        print("Chyba: Zadej 2 argumenty – URL a název výstupního CSV souboru.")
        print("Použití: python main.py <URL> <vystup.csv>")
        sys.exit(1)

    url = sys.argv[1]
    vystupni_soubor = sys.argv[2]

    if not url.startswith("https://www.volby.cz/pls/ps2017nss/ps32"):
        print("Chybný odkaz. Zadej URL na konkrétní územní celek (začíná na 'ps32').")
        sys.exit(1)

    return url, vystupni_soubor


def zpracovani_uzemniho_celku(url):
    """
    Načte HTML obsah stránky ze zadané URL a vrátí ho jako objekt typu BeautifulSoup.

    Parametry:
    url (str): Adresa webové stránky.

    Vrací:
    BeautifulSoup: Zpracovaný HTML obsah stránky.
    """
    hlavicka = {"User-Agent": "Mozilla/5.0"}
    odpoved = requests.get(url, headers=hlavicka)
    if not odpoved.ok:
        print(f"Nepodařilo se stáhnout stránku, zkontroluj URL. Chyba {odpoved.status_code}")
        sys.exit(1)
    return BeautifulSoup(odpoved.text, "html.parser")


def ziskani_odkazu_obci(soup) -> list[tuple[str, str, str]]:
    """
    Ze zpracovaného HTML získá odkazy na jednotlivé obce.

    Parametry:
        soup (BeautifulSoup): HTML stránka s výpisem obcí.

    Vrací:
        list[tuple]: Seznam trojic (kód obce, název obce, URL obce).
    """
    odkazy = soup.find_all("td", class_="cislo")
    hlavni_url = "https://www.volby.cz/pls/ps2017nss/"
    vysledky_obci = []

    for odkaz in odkazy:
        a = odkaz.find("a")
        if a and a.get("href"):
            obec_url = hlavni_url + a.get("href")
            kod = a.text.strip()
            jmeno_td = odkaz.find_next_sibling("td")
            jmeno = jmeno_td.text.strip() if jmeno_td else ""
            vysledky_obci.append((kod, jmeno, obec_url))

    return vysledky_obci

def najdi_udaj(soup, vzor_popisku):
    """
    Najde údaj na základě popisku v buňce tabulky.
    
    Parametry:
        soup (BeautifulSoup): HTML obsah stránky.
        vzor_popisku (str): Regulární výraz hledaného popisku (např. "Odevzdané\\s*obálky").

    Vrací:
        str: Hodnota z vedlejší buňky, nebo prázdný řetězec, pokud nebyla nalezena.
    """
    td = soup.find("td", string=re.compile(vzor_popisku))
    if td:
        sourozenec = td.find_next_sibling("td")
        return sourozenec.text.strip() if sourozenec else ""
    return ""


def ziskani_dat_z_obce(url) -> dict[str, str]:
    """
    Získá volební údaje z dané obce na základě její URL.

    Parametry:
    url (str): Odkaz na stránku konkrétní obce.

    Vrací:
    dict[str, str]: Slovník s údaji o voličích a počtech hlasů pro strany 
    """
    hlavicka = {"User-Agent": "Mozilla/5.0"}
    odpoved = requests.get(url, headers=hlavicka)
    soup = BeautifulSoup(odpoved.text, "html.parser")

    volici = najdi_udaj(soup, r"Voli[čc]i")
    obalky = najdi_udaj(soup, r"Odevzdané\s*obálky")
    platne = najdi_udaj(soup, r"Platné\s*hlasy")

    strany = {}
    for tabulka_tag in soup.find_all("div", {"class": "t2_470"}):
        radky_tagy = tabulka_tag.find_all("tr")[2:]
        for tr in radky_tagy:
            nazev = tr.find("td", class_="overflow_name")
            hlas_td = tr.find_all("td", class_="cislo")
            if nazev and hlas_td:
                strany[nazev.text.strip()] = hlas_td[1].text.strip()

    return {
        "Voliči v seznamu": volici,
        "Vydané obálky": obalky,
        "Platné hlasy": platne,
        **strany
    }


def zapsani_do_csv(vystupni_soubor, vysledky):
    """
    Zapíše získaná data do CSV souboru.

    Parametry:
    vystupni_soubor (str): Název výstupního CSV souboru.
    vysledky (list[dict]): Seznam řádků (slovníků) s volebními výsledky.Zapíše výsledná data do souboru.
    """
    if not vysledky:
        print("Nebyla získána žádná data k zápisu.")
        return

    hlavicka = vysledky[0].keys()
    with open(vystupni_soubor, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=hlavicka)
        writer.writeheader()
        writer.writerows(vysledky)


def main():
    """
    Hlavní funkce, která řídí zpracování volebních výsledků:
    - ověří vstupní argumenty
    - stáhne HTML obsah
    - zpracuje výsledky všech obcí
    - uloží je do CSV souboru
    """
    url, vystupni_soubor = zkontrolovani_vstupu()

    hlavni_soup = zpracovani_uzemniho_celku(url)
    obce = ziskani_odkazu_obci(hlavni_soup)

    print(f"Nalezeno obcí: {len(obce)}")
    vysledky = []

    for kod_obce, jmeno_obce, obec_url in obce:
        try:
            data = ziskani_dat_z_obce(obec_url)
            obec_data = {
                "Kód obce": kod_obce,
                "Název obce": jmeno_obce,
                **data
            }
            vysledky.append(obec_data)
            print(f"Zpracováno: {jmeno_obce}")
        except Exception as e:
            print(f"Chyba při zpracování obce {jmeno_obce}: {e}")

        time.sleep(1) 

    zapsani_do_csv(vystupni_soubor, vysledky)
    print(f"\nHotovo! Výstupní soubor: {vystupni_soubor}")


if __name__ == "__main__":
    main()



# cd main_projekt
# .\main_virtualni_prostredi\Scripts\activate
# .\main_virtualni_prostredi\Scripts\deactivate
# python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" vysledky_benesov.csv

