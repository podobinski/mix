import pandas as pd
import numpy as np
import datetime
from decimal import Decimal, ROUND_HALF_UP
# Removed the unnecessary import of openpyxl.Workbook

def ostatni_dzien_miesiaca(data):
    nastepny_miesiac = data.replace(day=28) + datetime.timedelta(days=4)
    return nastepny_miesiac - datetime.timedelta(days=nastepny_miesiac.day)

def oblicz_rate_annuitetowa(kwota, oprocentowanie, liczba_miesiecy, adjust=0):
    miesieczne_oprocentowanie = oprocentowanie / 12
    return kwota * miesieczne_oprocentowanie / (1 - (1 + miesieczne_oprocentowanie) ** -liczba_miesiecy) - adjust

def dni_od_poprzedniej_splaty(data_obecna, data_poprzednia):
    return (data_obecna - data_poprzednia).days

def wylicz_harmonogram(kwota, oprocentowanie, liczba_miesiecy, calkowita_rata, data_wyplaty):
    harmonogram = []
    saldo = kwota
    data_splaty = ostatni_dzien_miesiaca(datetime.datetime.strptime(data_wyplaty, "%Y-%m-%d"))
    data_poprzedniej_splaty = datetime.datetime.strptime(data_wyplaty, "%Y-%m-%d")

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
        harmonogram.append([data_splaty.strftime("%Y-%m-%d"), saldo, rata_kapitalowa, rata_odsetkowa, laczna_rata, saldo_po_splacie])
        data_poprzedniej_splaty = data_splaty
        saldo = saldo_po_splacie
        data_splaty = ostatni_dzien_miesiaca(data_splaty + datetime.timedelta(days=1))

    return harmonogram

def symulacja_splaty_annuitetowej():
    kwota = Decimal(input("Podaj kwotę kredytu: ").replace(',', '.'))  
    oprocentowanie = Decimal(input("Podaj stopę oprocentowania (w procentach): ").replace(',', '.')) / 100
    liczba_miesiecy = int(input("Podaj ilość miesięcy kredytu: "))
    data_wyplaty = input("Podaj datę wypłaty kredytu (YYYY-MM-DD): ")

    adjust = Decimal('0.00')
    calkowita_rata = oblicz_rate_annuitetowa(kwota, oprocentowanie, liczba_miesiecy, adjust).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    harmonogram = wylicz_harmonogram(kwota, oprocentowanie, liczba_miesiecy, calkowita_rata, data_wyplaty)
    ostatnia_rata = harmonogram[-1][4]
    rozjazd = ostatnia_rata - calkowita_rata
    rozjazd_bezwzgledny = abs(rozjazd)

    while True:
        new_adjust = adjust + Decimal('0.01') * (-1 if rozjazd > 0 else 1)
        new_calkowita_rata = oblicz_rate_annuitetowa(kwota, oprocentowanie, liczba_miesiecy, new_adjust).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        new_harmonogram = wylicz_harmonogram(kwota, oprocentowanie, liczba_miesiecy, new_calkowita_rata, data_wyplaty)
        new_ostatnia_rata = new_harmonogram[-1][4]
        new_rozjazd = new_ostatnia_rata - new_calkowita_rata
        new_rozjazd_bezwzgledny = abs(new_rozjazd)

        if new_rozjazd_bezwzgledny >= rozjazd_bezwzgledny:
            break

        adjust = new_adjust
        calkowita_rata = new_calkowita_rata
        harmonogram = new_harmonogram
        rozjazd = new_rozjazd
        rozjazd_bezwzgledny = new_rozjazd_bezwzgledny

    df = pd.DataFrame(harmonogram, index=range(1, liczba_miesiecy+1), columns=["Data", "Saldo przed spłatą", "Rata kapitału", "Rata odsetek", "Łączna rata", "Saldo po spłacie"])
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print(df)
    df.to_excel("symulacja_annuitetowa.xlsx", index_label="Nr raty")

symulacja_splaty_annuitetowej()
