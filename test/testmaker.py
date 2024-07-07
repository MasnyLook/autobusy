from datetime import datetime
import pandas as pd

def CorrectBusData():
    df = pd.DataFrame({
        "Lines": [709, 709, 709],
        "Lon": [21.01, 21.02, 21.03],
        "VehicleNumber": [20, 20, 20],
        "Time": ["2024-02-16 18:00:00.0", "2024-02-16 18:01:30.0", "2024-02-16 18:05:00.0"],
        "Lat": [52, 52.01, 52.02],
        "Brigade": [2, 2, 2]
    })
    #pierwsza prędkość >50km/h a druga <50 km/h
    df.to_json("./route")

def SuperFastBus():
    df = pd.DataFrame({
        "Lines": [709, 709],
        "Lon": [20, 30],
        "VehicleNumber": [20, 20],
        "Time": ["2024-02-16 18:00:00.0", "2024-02-16 18:01:30.0"],
        "Lat": [52, 52.01],
        "Brigade": [2, 2]
    })
    #prędkość >100 km/h
    df.to_json("./fastBus")

def MakeStop():
    df = pd.DataFrame({
        "zespol": ["44"],
        "slupek": ["01"],
        "nazwa_zespolu" : ["arka Noego"],
        "id_ulicy": ["4132"],
        "szer_geo": [52.005],
        "dlug_geo": [21.015],
        "kierunek": ["na mazury"],
        "obowiazuje_od": [datetime(2020,12,12)]
    })
    df.to_json("./oneStop")
    #w połowie między rekordami, więc szacowany czas dojazdu powinien wynieść 18:00:45

def MakeLine():
    df = pd.DataFrame({
        "line": [709],
        "stopid": ["44"],
        "stopnr": ["01"],
        "brygada": [2],
        "kierunek": ["na mazury"],
        "trasa": ["dobrze znana"],
        "czas": ["17:55:45"]
        #opoznienie 5 min
    })
    df.to_json("./oneLine")

def main():
    CorrectBusData()
    SuperFastBus()
    MakeLine()
    MakeStop()

main()