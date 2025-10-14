import os, feedparser, httpx
from .util import _ok, _err

def read_rss(url: str, limit: int = 5) -> dict:
    try:
        d = feedparser.parse(url)
        items = []
        for e in d.entries[:limit]:
            items.append({"title": e.get("title",""), "link": e.get("link","")})
        return _ok({"items": items, "count": len(items)})
    except Exception as e:
        return _err(str(e))

def search_news(query: str = "", country: str = "vn", limit: int = 5) -> dict:
    key = os.getenv("NEWS_API_KEY","").strip()
    if key:
        try:
            r = httpx.get("https://newsapi.org/v2/top-headlines",
                          params={"q": query or None, "country": country, "pageSize": limit, "apiKey": key},
                          timeout=15)
            j = r.json()
            items=[{"title":a["title"],"link":a["url"]} for a in j.get("articles",[])[:limit]]
            return _ok({"items": items, "count": len(items)})
        except Exception as e:
            pass
    # Fallback Google News RSS
    q = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={q}+when:7d&hl=vi&gl=VN&ceid=VN:vi"
    return read_rss(url, limit)
