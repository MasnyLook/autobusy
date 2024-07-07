import argparse
import pathlib
import datetime

from Tester import *
from analyzer import *
from dataGetter import *
from visualizer import *

listOfActions = ['pobierz_autobusy', 'pobierz_przystanki', 'pobierz_rozklady',
                 'analizuj_predkosci', 'analizuj_opoznienia',
                 'pokaz_predkosci', 'pokaz_opoznienia',
                 'testuj','wykonaj_Profile', 'pokaz_Profile']

def makeParser():
    parser = argparse.ArgumentParser(description="Pakiet analizy danych Warszawskiej Komunikacji Miejskiej")
    parser.add_argument('--akcja', type=str, required=True, dest='akcja', choices=listOfActions,
                        help='wybór działania')
    parser.add_argument('--api_key', type=str, dest='key', default='fbba07bd-ee76-47da-b566-f37f21555856',
                        help='klucz użytkownika potrzebny do pobierania danych')
    parser.add_argument('--start', dest='start', type=lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S'),
                        help='poczatkowa data i godzina wczytywania lokalizacji autobusów')
    parser.add_argument('--koniec', dest='koniec', type=lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S'),
                        help='końcowa data i godzina wczytywania lokalizacji autobusów')
    parser.add_argument('--plik',  type=pathlib.Path, dest = 'plik',
                        help='plik do którego ma być zapisany wynik, zalecane jest korzystaie z domyślnych'
                             'plików')
    parser.add_argument('--daneBusow', type=pathlib.Path, dest='busy', default='./files/localization',
                        help='plik z rekordami autobusów')
    parser.add_argument('--danePrzystankow', type=pathlib.Path, dest='przystanki', default='./files/stops',
                        help='plik z przystankami')
    parser.add_argument('--daneJazdy', type=pathlib.Path, dest='drogi', default='./files/schedules',
                        help='plik z rozkładami jazdy')
    parser.add_argument('--data', type=lambda d: datetime.strptime(d, '%Y-%m-%d'), dest='data',
                        help='dzień pobierania lokalizacji autobusów')
    parser.add_argument('--prędkosc', type=pathlib.Path, dest='pr', default='./files/speed',
                        help='plik z analizą prędkości')
    parser.add_argument('--opoznienia', type=pathlib.Path, dest='op', default='./files/delays',
                        help='plik z analizą opóźnień')
    return parser

def run(args):
    if args.akcja == 'pobierz_autobusy':
        pathfile = args.plik
        if pathfile is None:
            pathfile = './files/localization'
        get_Autobuses_location(pathfile, args.start, args.koniec, args.key)
    if args.akcja == 'pobierz_przystanki':
        pathfile = args.plik
        if pathfile is None:
            pathfile = './files/stops'
        get_Stops(pathfile, args.key)
    if args.akcja == 'pobierz_rozklady':
        pathfile = args.plik
        if pathfile is None:
            pathfile = './files/schedules'
        get_Schedules(pathfile, args.przystanki, args.key)
    if args.akcja == 'analizuj_predkosci':
        pathfile = args.plik
        if pathfile is None:
            pathfile = './files/speed'
        calculateSpeed(pathfile, args.busy, args.start, args.koniec)
    if args.akcja == 'analizuj_opoznienia':
        pathfile = args.plik
        if pathfile is None:
            pathfile = './files/delay'
        calculate_delays(pathfile, args.busy, args.przystanki, args.drogi, args.start, args.koniec, args.data)
    if args.akcja == 'pokaz_predkosci':
        plotspeed(args.pr)
    if args.akcja == 'pokaz_opoznienia':
        plotdelay(args.op)
    if args.akcja == 'testuj':
        Tests()
    if args.akcja == 'wykonaj_Profile':
        profilerTester()
    if args.akcja == 'pokaz_Profile':
        printProfile()

def main():
    parser = makeParser()
    args = parser.parse_args()
    run(args)

main()