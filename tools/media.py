
import re, requests
from typing import Dict
from yt_dlp import YoutubeDL

# Một số đài radio Việt Nam thông dụng
RADIO_MAP: Dict[str, str] = {
    "vov1": "http://stream.vov.gov.vn/vov1",
    "vov2": "http://stream.vov.gov.vn/vov2",
    "vov3": "http://stream.vov.gov.vn/vov3",
    "vov giao thong": "http://113.164.246.38:1935/vovgt/vovgthn_aac/playlist.m3u8",
    "voh fm 99.9": "https://strm.voh.com.vn/fm-999",
    "voh fm 95.6": "https://strm.voh.com.vn/fm-956",
}

def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def resolve_radio(name_or_url: str) -> dict:
    s = name_or_url.strip()
    if s.startswith("http"):
        return {"name": s, "url": s}

    key = normalize(s)
    for k, v in RADIO_MAP.items():
        if key in k or k in key:
            return {"name": k, "url": v}

    # fallback search with Radio Browser (no key)
    q = requests.get("https://de1.api.radio-browser.info/json/stations/search", params={"name": s, "limit": 1}, timeout=10)
    data = q.json()
    if data:
        st = data[0]
        return {"name": st.get("name", s), "url": st.get("url_resolved") or st.get("url")}
    raise RuntimeError("Không tìm thấy đài radio phù hợp. Hãy nhập tên khác hoặc dán trực tiếp URL stream.")

def yt_audio_search(query_or_url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "format": "bestaudio/best",
        "extract_flat": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        if query_or_url.startswith("http"):
            info = ydl.extract_info(query_or_url, download=False)
        else:
            info = ydl.extract_info(f"ytsearch1:{query_or_url}", download=False)["entries"][0]
        # find direct audio url
        url = None
        for f in info.get("formats", []):
            if f.get("acodec") != "none" and not f.get("vcodec"):
                url = f.get("url")
                break
        if not url:
            # fallback: bestaudio
            url = info.get("url")
        return {
            "title": info.get("title"),
            "webpage_url": info.get("webpage_url"),
            "audio_url": url,
            "duration": info.get("duration")
        }
