"""
Moduł formatujący dane pobrane z systemu do odpowiedniej formy.
"""
def Format(data):
    return list(
        dict((item["key"], item["value"]) for item in sublist["values"])
        for sublist in data
    )

def ScheduleFormat(data, line, stopid, stopnr):
    result = []
    for d in data:
        res = {}
        res['line'] = line
        res['stopid'] = stopid
        res['stopnr'] = stopnr
        res['brygada'] = d['brygada']
        res['kierunek'] = d['kierunek']
        res['trasa'] = d['trasa']
        res['czas'] = d['czas']
        result.append(res)
    return result
