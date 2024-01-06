import pandas as pd
import numpy as np
import datetime
from openpyxl import Workbook

def ostatni_dzien_miesiaca(data):
    nastepny_miesiac = data.replace(day=28) + datetime.timedelta(days=4)
    return nastepny_miesiac - datetime.timedelta(days=nastepny_miesiac.day)

def symulacja_splaty():
    kwota = float(input("Podaj kwotę kredytu: "))
    oprocentowanie = float(input("Podaj stopę oprocentowania (w procentach): ")) / 100
    liczba_miesiecy = int(input("Podaj ilość miesięcy kredytu: "))
    data_wyplaty = input("Podaj datę wypłaty kredytu (YYYY-MM-DD): ")

    data_wyplaty = datetime.datetime.strptime(data_wyplaty, "%Y-%m-%d")
    rata_kapitalowa = kwota / liczba_miesiecy

    harmonogram = []
    saldo = kwota
    data_splaty = ostatni_dzien_miesiaca(data_wyplaty)

    for i in range(liczba_miesiecy):
        dni_do_splaty = (data_splaty - data_wyplaty).days
        rata_odsetkowa = saldo * oprocentowanie * dni_do_splaty / 365
        calkowita_rata = rata_kapitalowa + rata_odsetkowa
        saldo -= rata_kapitalowa

        harmonogram.append([
            data_splaty.strftime("%Y-%m-%d"),
            f'{kwota - rata_kapitalowa * i:.2f}'.replace('.',','),
            f'{rata_kapitalowa:.2f}'.replace('.',','),
            f'{rata_odsetkowa:.2f}'.replace('.',','),
            f'{calkowita_rata:.2f}'.replace('.',','),
            f'{saldo:.2f}'.replace('.',',')
        ])

        data_wyplaty = data_splaty + datetime.timedelta(days=1)
        data_splaty = ostatni_dzien_miesiaca(data_wyplaty)

    df = pd.DataFrame(harmonogram, columns=["Data", "Saldo przed spłatą", "Rata kapitału", "Rata odsetek", "Łączna rata", "Saldo po spłacie"])
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print(df)

    df.to_excel("symulacja.ods", index=False)

symulacja_splaty()
