import webbrowser
import folium.map
import pandas as pd
import matplotlib.pyplot as plt

"""
Moduł wyświetlający na mapie z biblioteki 'folium' miejsca, na których autobus
przekroczył dozwoloną prędkość w odpowiednim kolorze (czytaj chooseColour).
Miejsce takie jest zdefiniowane jako środek dwóch kolejnych punktów, w których 
został zmierzony autobus, który w założeniu porusza się w linii prostej ze
stałą prędkością.
"""

def chooseColour(speed, graph):
    if speed < 60:
        graph[0] += 1
        return 'yellow'
    if speed < 70:
        graph[1] += 1
        return 'orange'
    if speed < 80:
        graph[2] += 1
        return 'red'
    graph[3] += 1
    return 'darkred'

def makeMarks(df, graph):
    marks = folium.map.FeatureGroup()
    for i in range(0, len(df)):
        color = chooseColour(df.iloc[i]['speed'], graph)
        marks.add_child(
            folium.features.CircleMarker(
                [df.iloc[i]['midLat'], df.iloc[i]['midLon']],
                radius = 3,
                color = color
            )
        )
    return marks

def read_speedData(datafile):
    try:
        df = pd.read_json(datafile, dtype={
            "Lines": "string",
            "Lon": "float",
            "VehicleNumber": "string",
            "Time": "datetime64[ns]",
            "Lat": "float",
            "Brigade": "string",
            "prevLon": "float",
            "prevLat": "float",
            "prevTime": "datetime64[ns]",
            "speed": "float"
        })
    except:
        raise Exception("Nie udało się pobrać danych")
    return df

def plotspeed(datafile):
    names = ['50-60', '60-70', '70-80', '>80']
    graph = [0,0,0,0]
    df = read_speedData(datafile)
    df = df.dropna()
    df["midLon"] = (df["Lon"] + df["prevLon"])/2
    df["midLat"] = (df["Lat"] + df["prevLat"])/2

    m = folium.Map(location=[52.23, 21.07], tiles="OpenStreetMap", zoom_start=11)
    marks = makeMarks(df, graph)
    m.add_child(marks)
    m.save("mapSpeed.html")
    webbrowser.open("./mapSpeed.html")

    plt.bar(names, graph)
    plt.show()