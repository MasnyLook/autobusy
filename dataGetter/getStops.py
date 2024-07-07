import pandas as pd
from .sendRequest import get_requested_data
from .formatter import Format

"""
Moduł pobierający informacje o przystankach znajduąjcych się w Warszawie.
"""

url = "https://api.um.warszawa.pl/api/action/dbstore_get"

def get_Stops(file, apikey):
    params = {
        "id": "ab75c33d-3a26-4342-b36a-6e5fef0a3ac3",
        "apikey": apikey
    }
    try:
        requested_data = get_requested_data(url= url, params= params)
        result = Format(requested_data)
        df = pd.DataFrame(result)
        df.to_json(file)
    except Exception as e:
        print(e)