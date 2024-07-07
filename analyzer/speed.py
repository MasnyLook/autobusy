from geopy.distance import geodesic

import pandas as pd

"""
Moduł analizujący przekroczenia prędkości autobusów w danym okresie.
Do jego wykonania potrzbne są dane autbusów zebrane z danego okresu.
Pakiet śledzi kolejne rekordy autobusów o tym samym numerze i 
symuluje jego ruch po odcinkach z jednostajną prędkością.
"""

def preprocess(file, start, end):
    try:
        res = pd.read_json(
            file,
            dtype = {
                "Lines": "string",
                "Lon": "float",
                "VehicleNumber": "string",
                "Time": "datetime64[ns]",
                "Lat": "float",
                "Brigade": "string"
            }
        )
    except:
        raise Exception("Nie udało się pobrać danych z pliku.")
    res = res.loc[(res["Time"] >= start) & (res["Time"] <= end)]
    res = res.sort_values(by=["VehicleNumber", "Time"])
    res = res.drop_duplicates(ignore_index=True)
    return res

def calculateMeanSpeed(x1, y1, x2, y2, t1, t2):
    coord1 = (x1, y1)
    coord2 = (x2, y2)
    dist = geodesic(coord1, coord2).km
    time = (t1-t2).total_seconds()
    if time == 0:
        return 0
    return dist/time * 3600

def calculateOneSpeed(group):
    group.drop_duplicates("Time", inplace=True)
    group["previousLon"] = group["Lon"].shift()
    group["previousLat"] = group["Lat"].shift()
    group["prevTime"] = group["Time"].shift()
    group.dropna(ignore_index=True, inplace=True)
    if group.shape[0] == 0:
        return None
    group["speed"] = group.apply(lambda x: calculateMeanSpeed(x["Lat"],x["Lon"], x["previousLat"], x["previousLon"], x["Time"], x["prevTime"]), axis=1)
    return group

def calculateSpeed(outfile, file, start, end):
    result = []
    data = preprocess(file, start, end)
    groups = data.groupby("VehicleNumber")
    for name, group in groups:
        group = calculateOneSpeed(group)
        if group is not None:
            result += group.values.tolist()
    df = pd.DataFrame(result, columns = [
        "Lines",
        "Lon",
        "VehicleNumber",
        "Time",
        "Lat",
        "Brigade",
        "prevLon",
        "prevLat",
        "prevTime",
        "speed"
    ])
    df = df.loc[(df["speed"] > 50) & (df["speed"] < 100)]
    try:
        df.to_json(outfile)
    except:
        raise Exception("Nie udało się zapisać danych do pliku.")