from mcp.server.fastmcp import FastMCP
import logging
from tools.media import search_youtube_audio, find_radio_stream, vov_presets
from tools.rss_tool import read_rss, search_news
from tools.storage import alarm_set, alarm_list, alarm_delete
from tools.util import weather_any, translate_text

log = logging.getLogger("mcp_vn")
mcp = FastMCP("VN-Tools Plus")

@mcp.tool()
def selftest() -> str:
    """Dùng để kiểm tra MCP có hoạt động: trả về 'OK' với timestamp."""
    import datetime as dt
    return f"OK {dt.datetime.now().isoformat()}"

@mcp.tool()
def weather(city: str) -> dict:
    """Thời tiết thành phố (dùng OpenWeather nếu có key, fallback Open-Meteo)."""
    return weather_any(city)

@mcp.tool()
def translate(text: str, target_lang: str = "vi", source_lang: str = "auto") -> dict:
    """Dịch văn bản bằng LibreTranslate (miễn phí)."""
    return translate_text(text, target_lang, source_lang)

@mcp.tool()
def rss_read(url: str, limit: int = 5) -> dict:
    """Đọc RSS/Atom, trả tiêu đề + link."""
    return read_rss(url, limit)

@mcp.tool()
def news(query: str = "", country: str = "vn", limit: int = 5) -> dict:
    """Tin tức (NewsAPI nếu có key, nếu không thì Google News RSS)."""
    return search_news(query, country, limit)

@mcp.tool()
def youtube_audio(query_or_url: str) -> dict:
    """Lấy URL phát âm thanh YouTube (Piped api) để phát full bài."""
    return search_youtube_audio(query_or_url)

@mcp.tool()
def music_full(query: str) -> dict:
    """Alias của youtube_audio."""
    return search_youtube_audio(query)

@mcp.tool()
def radio_play(name_or_url: str) -> dict:
    """
    Phát radio Việt Nam. Nhận tên ('VOVGT HN','VOVGT HCM','VOH 99.9','HTV Radio',...) hoặc URL.
    Trả về {title, url, type:'audio'}.
    """
    return find_radio_stream(name_or_url)

# Báo thức
@mcp.tool()
def alarm_create(iso_time: str, title: str) -> dict:
    """Tạo báo thức ISO8601 (vd '2025-10-16T07:30:00+07:00')."""
    return alarm_set(iso_time, title)

@mcp.tool()
def alarm_list_all() -> dict:
    """Liệt kê báo thức."""
    return alarm_list()

@mcp.tool()
def alarm_delete_id(alarm_id: str) -> dict:
    """Xoá báo thức theo id."""
    return alarm_delete(alarm_id)

if __name__ == "__main__":
    mcp.run(transport="stdio")
