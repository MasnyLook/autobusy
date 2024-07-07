from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from geopy.distance import geodesic

"""
Moduł przetwarzający zebrane dane i stwierdzający dla każdego przyjazdu
autobusu czy nastąpiło opóźnienie.
Dla każdego planowanego postoju na przystanku szacuje rzeczywisty czas
dojazdu autobusu na podstawie rekordów danego autobusu na trasie 
(najbliższy rekord + liniowe szacowanie).
"""
def makeGoodDateTime(date, time):
    if int(time[0:2]) >= 24:
        return datetime(2050,1,1) #non-meaningful-data
    goodtime = datetime.strptime(time, '%H:%M:%S').time()
    gooddate = date.date()
    return datetime.combine(gooddate, goodtime)

def preprocessStops(file):
    df = pd.read_json(
        file,
        dtype={
            "zespol": "string", #stopid
            "slupek": "string", #stopnr
            "nazwa_zespolu": "string", #delete
            "id_ulicy": "string", #delete
            "szer_geo": "float", #stopLat
            "dlug_geo": "float", #stopLon
            "kierunek": "object", #delete
            "obowiazuje_od": "datetime64[ms]", #delete
        }
    )
    df.drop(['nazwa_zespolu', 'id_ulicy', 'kierunek', 'obowiazuje_od'], axis=1, inplace=True)
    df.rename(columns={'szer_geo':'stopLat', 'dlug_geo':'stopLon'}, inplace=True)
    df.rename(columns= {'zespol':'stopid', 'slupek':'stopnr'}, inplace=True)
    return df

def preprocessSchedules(file, date): #date of downloading buses data
    df = pd.read_json(
        file,
        dtype={
            "line": "string",
            "stopid": "string",
            "stopnr": "string",
            "brygada": "string", #brigade
            "kierunek": "string", #delete
            "trasa": "string", #delete
            "czas": "string" #plannedTime
        }
    )
    df["czas"] = df.apply(lambda x: makeGoodDateTime(date, x["czas"]), axis=1)
    df.sort_values("czas", ignore_index=True, inplace=True)
    df.rename(columns={'czas':'plannedTime', 'brygada':'brigade'}, inplace=True)
    df.drop(['kierunek', 'trasa'], axis=1, inplace=True)
    return df

def preprocess(file, start, end):
    res = pd.read_json(
        file,
        dtype = {
            "Lines": "string",
            "Lon": "float",
            "VehicleNumber": "string",
            "Time": "datetime64[ns]", #shotTime
            "Lat": "float",
            "Brigade": "string"
        }
    )
    res.rename(columns={'Time': 'shotTime'}, inplace=True)
    res = res.loc[(res["shotTime"] >= start) & (res["shotTime"] <= end)]
    res = res.sort_values(by=["VehicleNumber", "shotTime"])
    res = res.drop_duplicates(ignore_index=True)
    return res

def Dist(x, stopcoord):
    coord1 = (x['Lon'], x['Lat'])
    coord2 = stopcoord
    return geodesic(coord1, coord2).m

def Dist0(x,y):
    coord1 = (x['Lon'], x['Lat'])
    coord2 = (y['Lon'], y['Lat'])
    return geodesic(coord1, coord2).m

def findNearestShot(stopcoord, route):
    distances = route.apply(lambda row: Dist(row, stopcoord), axis=1)
    minimal_index = distances.idxmin()
    return minimal_index

def estimatedTimeandScalar(shot1, shot2, stop):
    #skalar to stosunek boków długości trójkąta powyższych rekordów
    #służy do stwierdzenia czy autobus już dojechał czy nie
    dist1 = Dist(shot1, stop)
    dist2 = Dist(shot2, stop)
    diff = abs(shot2['shotTime']-shot1['shotTime'])
    dist0 = Dist0(shot1, shot2)
    try:
        diff = diff * (dist1/(dist1+dist2))
        scalar = (dist1+dist2)/dist0
    except ZeroDivisionError:
        #dzielenie przez zero
        return 0, shot1['shotTime']
    return scalar, shot1['shotTime'] + diff

def estimatedTime(stopLat, stopLon, route):
    stop_coord = (stopLon, stopLat)
    minimal_index = findNearestShot(stop_coord, route)
    prevroute = route.shift()
    nextroute = route.shift(periods=-1)
    if Dist(route.loc[minimal_index], stop_coord) < 50:
        return route['shotTime'][minimal_index]
    if np.isnan(prevroute.loc[minimal_index]['Lon']):
        return None
    else:
        scalar1, t1 = estimatedTimeandScalar(prevroute.loc[minimal_index], route.loc[minimal_index], stop_coord)
    if np.isnan(nextroute.loc[minimal_index]['Lon']):
        return None
    else:
        scalar2, t2 = estimatedTimeandScalar(route.loc[minimal_index], nextroute.loc[minimal_index], stop_coord)

    if scalar1 < scalar2:
        return t1
    else:
        return t2

def findDepartureTime(real_route, plannedTime, stopLat, stopLon):
    begin = plannedTime - timedelta(minutes=10)
    end = plannedTime + timedelta(minutes=15)
    main_route = real_route.loc[(begin < real_route['shotTime']) & (real_route['shotTime'] < end)]
    if main_route.shape[0] == 0:
        return None
    return estimatedTime(stopLat, stopLon, main_route)

def getDelayinSeconds(row):
    return (row['departureTime'] - row['plannedTime']).total_seconds()

def calculate_delays(outfile, dataBus, dataStop, dataSchedule, Start, End, Date):
    if Start is None:
        raise Exception("Brak godziny rozpoczęcia pobierania rekordów autobusów")
    if End is None:
        raise Exception("Brak godziny zakończenia pobierania rekordów autobusów")
    if Date is None:
        raise Exception("Brak daty pobierania rekordów autobusów")
    result = []
    try:
        stops = preprocessStops(dataStop)
        schedules = preprocessSchedules(dataSchedule, Date)
        buses = preprocess(dataBus, Start, End)
    except:
        raise Exception("Nie udało się pobrać danych z plików.")

    schedules = schedules.loc[(schedules["plannedTime"] > Start) & (schedules["plannedTime"] < End)]
    schedules = pd.merge(schedules, stops, on=['stopid', 'stopnr'])

    planned_routes = schedules.groupby(['line', 'brigade'])
    real_routes = buses.groupby(['Lines', 'Brigade'])

    for name, route in real_routes:
        try:
            group = planned_routes.get_group(name)
        except:
            print("Nie ma klucza", name)
            continue
        group["departureTime"] = group.apply(lambda row: findDepartureTime(route, row["plannedTime"], row["stopLat"], row["stopLon"]), axis=1)
        group['departureTime'] = group['departureTime'].values.astype('datetime64[s]')
        dep_times = group.dropna()
        result += dep_times.values.tolist()

    df = pd.DataFrame(result, columns=[
        'line',
        'stopid',
        'stopnr',
        'brigade',
        'plannedTime',
        'stopLat',
        'stopLon',
        'departureTime'
    ])
    if df.shape[0] != 0:
        df['diff'] = df.apply(lambda row: getDelayinSeconds(row), axis=1)
    try:
        df.to_json(outfile)
    except:
        raise Exception("Nie udało się zapisać do pliku.")