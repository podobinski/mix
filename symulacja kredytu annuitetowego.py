import pandas as pd
import numpy as np
import datetime
from decimal import Decimal, ROUND_HALF_UP
from openpyxl import Workbook

def ostatni_dzien_miesiaca(data):
    nastepny_miesiac = data.replace(day=28) + datetime.timedelta(days=4)
    return nastepny_miesiac - datetime.timedelta(days=nastepny_miesiac.day)

def oblicz_rate_annuitetowa(kwota, oprocentowanie, liczba_miesiecy):
    miesieczne_oprocentowanie = oprocentowanie / 12
    return kwota * miesieczne_oprocentowanie / (1 - (1 + miesieczne_oprocentowanie) ** -liczba_miesiecy)

def dni_od_poprzedniej_splaty(data_obecna, data_poprzednia):
    return (data_obecna - data_poprzednia).days

def symulacja_splaty_annuitetowej():
    kwota = Decimal(input("Podaj kwotę kredytu: ").replace(',', '.'))  # Akceptowanie przecinka jako separatora dziesiętnego
    oprocentowanie = Decimal(input("Podaj stopę oprocentowania (w procentach): ").replace(',', '.')) / 100
    liczba_miesiecy = int(input("Podaj ilość miesięcy kredytu: "))
    data_wyplaty = input("Podaj datę wypłaty kredytu (YYYY-MM-DD): ")

    data_wyplaty = datetime.datetime.strptime(data_wyplaty, "%Y-%m-%d")
    calkowita_rata = oblicz_rate_annuitetowa(kwota, oprocentowanie, liczba_miesiecy).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    harmonogram = []
    saldo = kwota
    data_splaty = ostatni_dzien_miesiaca(data_wyplaty)
    data_poprzedniej_splaty = data_wyplaty

    for i in range(liczba_miesiecy):
        dni_miedzy_splatami = dni_od_poprzedniej_splaty(data_splaty, data_poprzedniej_splaty)
        rata_odsetkowa = (saldo * oprocentowanie * dni_miedzy_splatami / 365).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if i == liczba_miesiecy - 1:
            rata_kapitalowa = saldo
            saldo_po_splacie = Decimal('0.00')
        else:
            rata_kapitalowa = (calkowita_rata - rata_odsetkowa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            saldo_po_splacie = saldo - rata_kapitalowa

        laczna_rata = rata_kapitalowa + rata_odsetkowa

        harmonogram.append([
            data_splaty.strftime("%Y-%m-%d"),
            saldo,  # Użycie bieżącego salda
            rata_kapitalowa,
            rata_odsetkowa,
            laczna_rata,
            saldo_po_splacie
        ])

        data_poprzedniej_splaty = data_splaty
        saldo = saldo_po_splacie  # Aktualizacja salda dla następnego cyklu

        data_wyplaty = data_splaty + datetime.timedelta(days=1)
        data_splaty = ostatni_dzien_miesiaca(data_wyplaty)

    df = pd.DataFrame(harmonogram, columns=["Data", "Saldo przed spłatą", "Rata kapitału", "Rata odsetek", "Łączna rata", "Saldo po spłacie"])
    pd.set_option('display.max_rows', None)  # Wyświetlanie wszystkich wierszy
    pd.set_option('display.max_columns', None)  # Wyświetlanie wszystkich kolumn
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print(df)

    df.to_excel("symulacja_annuitetowa.xlsx", index=False)

symulacja_splaty_annuitetowej()
