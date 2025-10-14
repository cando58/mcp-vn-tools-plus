import re, httpx
from .util import _ok, _err

# Chuẩn hoá tên đài -> chuỗi tìm kiếm cho RadioBrowser
def _norm(name: str) -> str:
    n = name.lower().strip()
    reps = {
        "vov gt hn": "vov giao thong ha noi",
        "vov gt hcm": "vov giao thong tp ho chi minh",
        "vov gt": "vov giao thong",
        "voh": "voh 99.9",
        "htv radio": "htv radio",
    }
    return reps.get(n, n)

# Một số preset alias -> để “dính” đúng kết quả
PRESET_QUERIES = {
    "vov1": "vov1",
    "vov2": "vov2",
    "vov3": "vov3",
    "vov giao thong": "vov giao thong",
    "vov gt hn": "vov giao thong ha noi",
    "vov gt hcm": "vov giao thong tp ho chi minh",
    "voh 99.9": "voh 99.9",
    "voh 95.6": "voh 95.6",
    "htv": "htv radio",
    "htv radio": "htv radio",
}

def vov_presets():
    return list(PRESET_QUERIES.keys())

def _is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")

def find_radio_stream(name_or_url: str) -> dict:
    """
    - Nếu là URL => trả thẳng.
    - Nếu là tên => dùng RadioBrowser để tìm stream Việt Nam, ưu tiên url_resolved.
    """
    if _is_url(name_or_url):
        return _ok({"title": name_or_url, "url": name_or_url, "type": "audio"})
    q = PRESET_QUERIES.get(name_or_url.lower().strip(), _norm(name_or_url))
    try:
        # RadioBrowser: chọn endpoint bất kỳ
        params = {
            "name": q,
            "countrycode": "VN",
            "hidebroken": "true",
            "order": "votes",
            "reverse": "true",
            "limit": 5
        }
        rb = httpx.get("https://de1.api.radio-browser.info/json/stations/search",
                       params=params, timeout=20).json()
        if not rb:
            return _err("Không tìm thấy đài phù hợp")
        st = rb[0]
        title = st.get("name") or q
        url = st.get("url_resolved") or st.get("url")
        if not url:
            return _err("Đài không có URL phát")
        return _ok({"title": title, "url": url, "type": "audio"})
    except Exception as e:
        return _err(str(e))

# ======= YouTube audio (Piped API) =======
def _extract_video_id(s: str) -> str | None:
    m = re.search(r"v=([A-Za-z0-9_\-]{6,})", s)
    if m: return m.group(1)
    # youtu.be/
    m = re.search(r"youtu\.be/([A-Za-z0-9_\-]{6,})", s)
    return m.group(1) if m else None

def search_youtube_audio(query_or_url: str) -> dict:
    try:
        vid = _extract_video_id(query_or_url)
        base = "https://piped.video"
        if not vid:
            # search
            sj = httpx.get(f"{base}/api/v1/search", params={"q": query_or_url, "region":"VN"}, timeout=20).json()
            for it in sj:
                if it.get("type") == "video":
                    vid = it.get("url","").split("watch?v=")[-1] or it.get("id")
                    if vid: break
        if not vid:
            return _err("Không tìm thấy video phù hợp")

        streams = httpx.get(f"{base}/api/v1/streams/{vid}", timeout=20).json()
        auds = streams.get("audioStreams") or []
        if not auds:
            return _err("Không lấy được audio stream")
        # chọn bitrate cao nhất
        auds.sort(key=lambda a: a.get("bitrate",0), reverse=True)
        url = auds[0]["url"]
        title = streams.get("title","YouTube Audio")
        return _ok({"title": title, "url": url, "type": "audio"})
    except Exception as e:
        return _err(str(e))
