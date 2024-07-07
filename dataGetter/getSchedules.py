import pandas as pd
from .sendRequest import send_request
from .formatter import Format, ScheduleFormat

"""
Moduł pobierający informacje o wszystkich dostępnych rozkładach jazdy.
"""

url = "https://api.um.warszawa.pl/api/action/dbtimetable_get"

def ReadStops(output):
    try:
        res = pd.read_json(
            output,
            dtype={
                "zespol": "string",
                "slupek": "string",
                "nazwa_zespolu": "string",
                "id_ulicy": "string",
                "szer_geo": "float",
                "dlug_geo": "float",
                "kierunek": "object",
                "obowiazuje_od": "datetime64[ms]",
            }
        )
    except:
        raise Exception("Nie udało się pobrać danych.")
    return res

#Funkcja pobierające linie autobusowe przejeżdżające przez dany przystanek.
def getLinesFromGivenStop(elem, stops, apikey):
    lines = None
    tries = 5
    while lines is None and tries > 0:
        try:
            tries -= 1
            params = {
                "id": "88cd555f-6f31-43ca-9de4-66c479ad5942",
                "apikey": apikey,
                "busstopId": stops["zespol"][elem],
                "busstopNr": stops["slupek"][elem],
            }
            requested_data = send_request(url=url, query_params=params)
            lines = Format(requested_data)
        except Exception as e:
            print(e)
            if tries == 0:
                raise e
    if lines is not None:
        return lines
    else:
        raise Exception("Nie udało się pobrać linii autobusów z przystanku")

#Funkcja pobierająca rozkład danej linii na zadanym przystanku
def getSchedulesFromGivenLineandStop(line, stops, elem, apikey):
    schedule = None
    params = {
        "id": "e923fa0e-d96c-43f9-ae6e-60518c9f3238",
        "apikey": apikey,
        "busstopId": stops["zespol"][elem],
        "busstopNr": stops["slupek"][elem],
        "line": line['linia']
    }
    tries = 5
    while schedule is None and tries > 0:
        try:
            tries -= 1
            requested_data = send_request(url=url, query_params=params)
            raw_schedule = Format(requested_data)
            schedule = ScheduleFormat(raw_schedule, line['linia'], stops["zespol"][elem], stops["slupek"][elem])
        except Exception as e:
            print(e)
            if tries == 0:
                raise e
    if schedule is not None:
        return schedule
    else:
        raise Exception("Nie udało się pobrać rozkładów z przystanku")

def get_Schedules(output, file_stops, apikey):
    stops = ReadStops(file_stops)
    schedules = list()
    for elem in stops.index:
        try:
            lines = getLinesFromGivenStop(elem, stops, apikey)
        except Exception as e:
            print(e)
            continue
        for line in lines:
            try:
                schedule = getSchedulesFromGivenLineandStop(line, stops, elem, apikey)
                schedules += schedule
            except Exception as e:
                print(e)
                continue
    df = pd.DataFrame(schedules)
    try:
        df.to_json(output)
    except:
        raise Exception("Nie udało się zapisać do pliku.")