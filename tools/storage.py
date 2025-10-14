import json, os, uuid, datetime as dt
from .util import _ok, _err

STORE = "/tmp/alarms.json"

def _load():
    if not os.path.exists(STORE): return []
    try:
        return json.load(open(STORE,"r",encoding="utf-8"))
    except: return []

def _save(arr): json.dump(arr, open(STORE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def alarm_set(iso_time: str, title: str) -> dict:
    try:
        dt.datetime.fromisoformat(iso_time)  # validate
        arr = _load()
        i = {"id": str(uuid.uuid4())[:8], "time": iso_time, "title": title}
        arr.append(i); _save(arr)
        return _ok({"created": i})
    except Exception as e:
        return _err(str(e))

def alarm_list() -> dict:
    return _ok({"items": _load()})

def alarm_delete(alarm_id: str) -> dict:
    arr = _load()
    n = [x for x in arr if x["id"] != alarm_id]
    _save(n)
    return _ok({"deleted": alarm_id, "remain": len(n)})
