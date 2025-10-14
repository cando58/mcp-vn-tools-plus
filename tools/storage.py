
import json, os, uuid, threading

class Storage:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"alarms": []}, f)
        self._lock = threading.Lock()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_alarm(self, iso_time: str, title: str):
        with self._lock:
            data = self._load()
            alarm = {"id": str(uuid.uuid4())[:8], "time": iso_time, "title": title}
            data["alarms"].append(alarm)
            self._save(data)
            return alarm

    def list_alarms(self):
        return self._load().get("alarms", [])

    def delete_alarm(self, id: str) -> bool:
        with self._lock:
            data = self._load()
            before = len(data["alarms"])
            data["alarms"] = [a for a in data["alarms"] if a["id"] != id]
            self._save(data)
            return len(data["alarms"]) < before
