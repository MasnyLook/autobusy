from cProfile import Profile
from pstats import Stats, SortKey

import pytest

from analyzer import *
from dataGetter import *
from visualizer import *

Start = datetime(2024, 2,16,17,30)
End = datetime(2024,2,16,18,30)

def Test1():
    calculateSpeed("./test/test1", "./test/route", Start, End)
    df = read_speedData("./test/test1")
    assert len(df) == 1

def Test2():
    calculateSpeed("./test/test2", "./test/fastBus", Start, End)
    df = read_speedData("./test/test2")
    assert len(df) == 0

def Test3():
    calculate_delays("./test/test3", "./test/route", "./test/oneStop",
                     "./test/oneLine", Start, End, Start)
    df = read_delayData("./test/test3")
    assert len(df) == 1 and df['diff'][0] == 300

def Test4():
    with pytest.raises(Exception) as e:
        get_Autobuses_location("./test/result", Start, None, None)
    assert str(e.value) == "Nie ustawiono godziny zakończenia pobierania danych"

def Test5():
    with pytest.raises(Exception) as e:
        get_Schedules("./whatever", None, None)
    assert str(e.value) == "Nie udało się pobrać danych."

def Tests():
    Test1()
    Test2()
    Test3()
    Test4()
    Test5()
    print("Testy zakończnone pomyślnie")

def profilerTester():
    with Profile() as profile:
        start = datetime.now()
        end = datetime.now() + timedelta(minutes=5)
        apikey = 'fbba07bd-ee76-47da-b566-f37f21555856'
        get_Autobuses_location("./files/tempBus", start, end, apikey)
        calculateSpeed("./files/tempSpeed", "./files/tempBus", start, end)
        calculate_delays("./files/tempDelay", "./files/tempBus", "./files/stops", "./files/schedules",
                         start, end, start)
    results = Stats(profile)
    results.dump_stats("./test/profileData")

def printProfile():
    stats = Stats('./test/profileData')
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats()