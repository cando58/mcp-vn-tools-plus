
# VN MCP Tools (Plus)
Dịch vụ MCP miễn phí chạy trên Railway: Thời tiết, Nhạc (preview), Nhạc full qua YouTube, Radio, Đọc RSS, Tin tức, Dịch thuật, Báo thức (JSON).

## Biến môi trường
- `MCP_ENDPOINT` *(bắt buộc)*: URL `wss://...` lấy từ XiaoZhi → MCP Settings → **Get MCP Endpoint**.
- `OPENWEATHER_KEY` *(khuyến nghị)*: OpenWeather API Key để dùng tool `weather`.
- `NEWS_API_KEY` *(tuỳ chọn)*: nếu không có sẽ dùng Google News RSS.
- `LIBRETRANSLATE_URL` *(tuỳ chọn)*: endpoint LibreTranslate (mặc định `https://libretranslate.de`).

## Deploy
1. Push repo này lên GitHub.
2. Railway → New Project → Deploy from GitHub.
3. Vào **Variables** thêm các biến ở trên.
4. Deploy & kiểm tra logs: thấy `Connected to endpoint` là OK.

## Dùng trên XiaoZhi
- Ở trang Agent → MCP Settings → Official Services: tick các dịch vụ bạn muốn.
- Nhớ **Save** và **khởi động lại** thiết bị.

## Các tool
- `weather(city)`
- `music_search(query, limit=5)` – preview 30s (iTunes)
- `youtube_audio(query_or_url)` – trả về `audio_url` để phát full bài
- `music_full(query)` – alias của youtube_audio
- `radio_play(name_or_url)` – ví dụ: "VOV1", "VOH FM 99.9"
- `rss_read(url, limit=5)` – đọc tin từ RSS/Atom
- `news(query="", country="vn", limit=5)`
- `translate(text, target_lang="vi", source_lang="auto")`
- `alarm_set(iso_time, title)`, `alarm_list()`, `alarm_delete(id)`

> Lưu ý: Bộ nhớ JSON của báo thức là ephemeral. Redeploy/restart có thể mất dữ liệu.
