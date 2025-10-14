
import feedparser, time
from typing import List, Dict

def fetch_rss(url: str, limit: int = 5) -> List[Dict]:
    d = feedparser.parse(url)
    items = []
    for e in d.entries[: max(1, min(limit, 20))]:
        items.append({
            "title": getattr(e, "title", ""),
            "link": getattr(e, "link", ""),
            "published": getattr(e, "published", getattr(e, "updated", ""))
        })
    return items
