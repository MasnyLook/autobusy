import requests

"""
Moduł wysyłający żądania do systemu z pobraniem odpowiednich danych.
"""

def send_request(url, query_params):
    r = requests.get(url = url, params = query_params)
    if r.status_code == requests.codes.ok:
        response = r.json()
    else:
        raise Exception("Błąd w pobieraniu danych")
    if response.get("error"):
        raise Exception("Błąd w pobieraniu danych")
    if response["result"] == "Błędna metoda lub parametry wywołania":
        raise Exception("Błędna metoda lub parametry wywołania")
    return response["result"]

def get_requested_data(url, params):
    tries = 3
    result = None
    while tries > 0:
        try:
            result = send_request(url=url, query_params=params)
            break
        except Exception as e:
            tries -= 1
            if tries == 0:
                raise e
    return result