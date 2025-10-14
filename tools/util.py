import os, httpx

def _ok(data): return {"success": True, **data}
def _err(msg): return {"success": False, "error": msg}

async_client = httpx.AsyncClient

def weather_any(city: str) -> dict:
    key = os.getenv("OPENWEATHER_KEY", "").strip()
    try:
        if key:
            url = "https://api.openweathermap.org/data/2.5/weather"
            r = httpx.get(url, params={"q": city, "appid": key, "units": "metric", "lang": "vi"}, timeout=15)
            j = r.json()
            if r.status_code == 200:
                desc = j["weather"][0]["description"]
                t = j["main"]["temp"]
                return _ok({"text": f"{city}: {t}°C, {desc}."})
        # Fallback Open-Meteo
        g = httpx.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1}, timeout=15).json()
        if not g.get("results"): return _err("Không tìm thấy địa danh")
        lat, lon, name = g["results"][0]["latitude"], g["results"][0]["longitude"], g["results"][0]["name"]
        fm = httpx.get("https://api.open-meteo.com/v1/forecast",
                       params={"latitude": lat, "longitude": lon, "current": ["temperature_2m","weather_code"]},
                       timeout=15).json()
        t = fm["current"]["temperature_2m"]
        return _ok({"text": f"{name}: {t}°C (Open-Meteo)."})
    except Exception as e:
        return _err(str(e))

def translate_text(text: str, target_lang="vi", source_lang="auto") -> dict:
    url = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.de").rstrip("/") + "/translate"
    try:
        r = httpx.post(url, json={
            "q": text, "source": source_lang, "target": target_lang, "format": "text"
        }, timeout=20)
        j = r.json()
        if "translatedText" in j:
            return _ok({"text": j["translatedText"]})
        return _err(str(j))
    except Exception as e:
        return _err(str(e))
