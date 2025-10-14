
from mcp.server.fastmcp import FastMCP
import logging, os, json, time
from datetime import datetime
from typing import List, Dict, Any

import requests

from tools.storage import Storage
from tools.media import resolve_radio, yt_audio_search
from tools.rss_tool import fetch_rss

logger = logging.getLogger("mcp_vn_tools")
logging.basicConfig(level=logging.INFO)

mcp = FastMCP("VN-Tools")

# ---------- WEATHER ----------
@mcp.tool()
def weather(city: str) -> dict:
    """Lấy thời tiết hiện tại (°C) cho một thành phố. Cần env OPENWEATHER_KEY. Trả về JSON gồm temp, desc, humidity, wind, city."""
    key = os.getenv("OPENWEATHER_KEY")
    if not key:
        return {"success": False, "error": "Missing OPENWEATHER_KEY env."}
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": key, "units": "metric", "lang": "vi"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    data = r.json()
    return {
        "success": True,
        "city": data.get("name", city),
        "temp_c": data["main"]["temp"],
        "desc": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_ms": data["wind"]["speed"],
        "source": "openweathermap"
    }

# ---------- MUSIC (search preview) ----------
@mcp.tool()
def music_search(query: str, limit: int = 5) -> dict:
    """Tìm bài hát bằng iTunes Search API (không cần API key). Trả về danh sách tên, ca sĩ và previewUrl (30s)."""
    url = "https://itunes.apple.com/search"
    params = {"term": query, "media": "music", "limit": max(1, min(limit, 25)), "country": "vn"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    items = []
    for it in r.json().get("results", []):
        items.append({
            "title": it.get("trackName"),
            "artist": it.get("artistName"),
            "album": it.get("collectionName"),
            "previewUrl": it.get("previewUrl"),
            "artwork": it.get("artworkUrl100"),
            "itunesUrl": it.get("trackViewUrl")
        })
    return {"success": True, "items": items, "note": "previewUrl chỉ 30s, dùng youtube_audio hoặc music_full để phát bài đầy đủ."}

# ---------- FULL MUSIC via YouTube ----------
@mcp.tool()
def youtube_audio(query_or_url: str) -> dict:
    """Tìm/resolve YouTube audio và trả về liên kết audio stream (m4a/webm) để thiết bị phát trực tiếp.
    Input có thể là URL YouTube hoặc chuỗi tìm kiếm.
    Trả về: {title, webpage_url, audio_url, duration}"""
    try:
        info = yt_audio_search(query_or_url)
        return {"success": True, **info}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def music_full(query: str) -> dict:
    """Alias của youtube_audio: nhập tên bài hát/ca sĩ tiếng Việt để lấy audio_url phát toàn bộ bài."""
    return youtube_audio(query)

# ---------- RADIO ----------
@mcp.tool()
def radio_play(name_or_url: str) -> dict:
    """Phát radio Việt Nam: nhập tên đài (ví dụ 'VOV1', 'VOH FM 99.9', 'VOV3') hoặc dán thẳng URL stream.
    Trả về {name, url}. Nếu không tìm thấy, sẽ cố gắng tra cứu qua Radio-Browser."""
    try:
        resolved = resolve_radio(name_or_url)
        return {"success": True, **resolved}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- RSS ----------
@mcp.tool()
def rss_read(url: str, limit: int = 5) -> dict:
    """Đọc và tóm tắt RSS/Atom feed (tiếng Việt). Trả về danh sách {title, link, published}."""
    try:
        items = fetch_rss(url, limit=limit)
        return {"success": True, "items": items}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- TRANSLATE ----------
@mcp.tool()
def translate(text: str, target_lang: str = "vi", source_lang: str = "auto") -> dict:
    """Dịch nhanh dùng LibreTranslate (miễn phí). Có thể đặt env LIBRETRANSLATE_URL để trỏ tới instance của bạn."""
    base = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.de")
    try:
        r = requests.post(
            f"{base}/translate",
            data={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text",
            },
            timeout=15
        )
        if r.status_code != 200:
            return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
        return {"success": True, "translated": r.json().get("translatedText", "")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- NEWS ----------
@mcp.tool()
def news(query: str = "", country: str = "vn", limit: int = 5) -> dict:
    """Tin tức: nếu có NEWS_API_KEY sẽ dùng NewsAPI; nếu không có, lấy tin từ Google News RSS tiếng Việt.
    Trả về list {title, link, published}."""
    key = os.getenv("NEWS_API_KEY")
    items = []
    try:
        if key:
            url = "https://newsapi.org/v2/top-headlines"
            params = {"apiKey": key, "pageSize": max(1, min(limit, 20))}
            if country:
                params["country"] = country
            if query:
                url = "https://newsapi.org/v2/everything"
                params = {"apiKey": key, "q": query, "pageSize": max(1, min(limit, 20)), "language": "vi"}
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            for a in r.json().get("articles", []):
                items.append({
                    "title": a.get("title"),
                    "link": a.get("url"),
                    "published": a.get("publishedAt")
                })
        else:
            # Fallback Google News RSS tiếng Việt
            if query:
                rss = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=vi&gl=VN&ceid=VN:vi"
            else:
                rss = "https://news.google.com/rss?hl=vi&gl=VN&ceid=VN:vi"
            items = fetch_rss(rss, limit=limit)
        return {"success": True, "items": items}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- ALARMS ----------
store = Storage("/data/alarms.json")

@mcp.tool()
def alarm_set(iso_time: str, title: str) -> dict:
    """Tạo báo thức. iso_time dùng ISO8601 (vd: 2025-10-15T07:30:00+07:00). Lưu vào JSON (ephemeral)."""
    try:
        # basic validation
        datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    except Exception:
        return {"success": False, "error": "iso_time must be ISO8601, e.g. 2025-10-15T07:30:00+07:00"}
    alarm = store.add_alarm(iso_time, title)
    return {"success": True, "alarm": alarm}

@mcp.tool()
def alarm_list() -> dict:
    """Liệt kê báo thức đã lưu."""
    return {"success": True, "alarms": store.list_alarms()}

@mcp.tool()
def alarm_delete(id: str) -> dict:
    """Xoá 1 báo thức theo id."""
    ok = store.delete_alarm(id)
    return {"success": ok}

if __name__ == "__main__":
    # Bridge ws <-> stdio is implemented in mcp_pipe.py; here we just run stdio tool server
    mcp.run(transport="stdio")
