from datetime import datetime, timedelta
from time import sleep

import pandas as pd
from .sendRequest import get_requested_data

"""
Moduł pobierający dane o lokalizacji warszawskich autobusów, w rzeczywistym
przedziale czasowym [start, end].
"""

url = "https://api.um.warszawa.pl/api/action/busestrams_get"
def wait_for_begin(start):
    delay = (start - datetime.now()).total_seconds()
    if delay > 0:
        print("Rozpoczęcie oczekiwania do startu (w sekundach):", delay)
        sleep(delay)

class Item:
    def __init__(self, line, lon, busnr, time, lat, brigade):
        self.line = line
        self.lon = lon
        self.nr = busnr
        self.time = time
        self.lat = lat
        self.brigade = brigade

def downloadData(params, end):
    api_data = list()
    seen = set()

    while True:
        try:
            result = get_requested_data(url, params)
            newresult = []
            for item in result:
                element = Item(item["Lines"], item["Lon"], item["VehicleNumber"], item["Time"], item["Lat"],
                               item["Brigade"])
                if not element in seen:
                    newresult.append(item)
                    seen.add(element)
            api_data.extend(newresult)
        except Exception as e:
            print(e)
        if datetime.now() + timedelta(seconds=30) > end:
            break
        sleep(30)
    return api_data

def get_Autobuses_location(file, start, end, apikey):
    if start is None:
        raise Exception("Nie ustawiono godziny rozpoczęcia pobierania danych")
    if end is None:
        raise Exception("Nie ustawiono godziny zakończenia pobierania danych")
    if start > end:
        raise Exception("Błędny przedział czasowy")

    wait_for_begin(start)

    params = {
        "resource_id": "f2e5503e-927d-4ad3-9500-4ab9e55deb59",
        "apikey": apikey,
        "type": "1"
    }

    api_data = downloadData(params, end)
    df = pd.DataFrame(api_data)
    try:
        df.to_json(file)
    except:
        raise Exception("Nie udało się zapisać do pliku.")