import webbrowser
from datetime import timedelta
import folium.map
import pandas as pd
import matplotlib.pyplot as plt

"""
Moduł wyświetlający na mapie z biblioteki 'folium' przystanki, na których wystąpiło
opóźnienie w odpowiednim kolorze (czytaj: chooseColor).
"""

def chooseColor(difftime, graph):
    if timedelta(minutes=2).total_seconds() < difftime <= timedelta(minutes=4).total_seconds():
        graph[0] += 1
        return True, 'yellow'
    if timedelta(minutes=4).total_seconds() < difftime <= timedelta(minutes=6).total_seconds():
        graph[1] += 1
        return True, 'orange'
    if timedelta(minutes=6).total_seconds() < difftime <= timedelta(minutes=12).total_seconds():
        graph[2] += 1
        return True, 'red'
    if timedelta(minutes=12).total_seconds() < difftime <= timedelta(minutes=20).total_seconds():
        graph[3] += 1
        return True, 'darkred'
    return False, 'pass'

def makeMarks(df, graph):
    marks = folium.map.FeatureGroup()
    for i in range(0, len(df)):
        check, color = chooseColor(df.iloc[i]['diff'], graph)
        if not check:
            continue
        marks.add_child(
            folium.features.CircleMarker(
                [df.iloc[i]['stopLat'], df.iloc[i]['stopLon']],
                radius=3,
                color=color
            )
        )
    return marks

def read_delayData(datafile):
    try:
        df = pd.read_json(datafile, dtype={
            'line': 'string',
            'stopid': 'string',
            'stopnr': 'string',
            'brigade': 'string',
            'plannedTime': 'datetime64[ns]',
            'stopLat': 'float',
            'stopLon': 'float',
            'departureTime': 'datetime64[ns]',
            'diff': 'float'
        })
    except:
        raise Exception("Nie udało się pobrać danych")
    return df

def plotdelay(datafile):
    names = ['2-4', '4-6', '6-12', '12-20']
    graph = [0,0,0,0]
    df = read_delayData(datafile)
    m = folium.Map(location=[52.23, 21.07], tiles="OpenStreetMap", zoom_start=11)
    marks = makeMarks(df, graph)
    m.add_child(marks)
    m.save("mapDelay.html")
    webbrowser.open("./mapDelay.html")
    plt.bar(names, graph)
    plt.show()