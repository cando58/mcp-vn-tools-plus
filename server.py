from mcp.server.fastmcp import FastMCP
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO, format="SRV %(levelname)s: %(message)s")

mcp = FastMCP("SanityTools")

@mcp.tool()
def ping(text: str) -> str:
    """Echo văn bản; dùng để test đường MCP."""
    return f"pong: {text}"

@mcp.tool()
def time_now() -> str:
    """Trả về thời gian hiện tại theo ISO 8601."""
    return datetime.now().isoformat(timespec="seconds")

if __name__ == "__main__":
    logging.info("Starting FastMCP stdio server…")
    mcp.run(transport="stdio")
# server.py
import logging

try:
    from mcp.server.fastmcp import FastMCP
    logging.warning("Using FastMCP from mcp.server.fastmcp")
except Exception:
    try:
        from fastmcp import FastMCP  # fallback nếu môi trường đóng gói tách riêng
        logging.warning("Using FastMCP from fastmcp")
    except Exception as e:
        logging.exception("Cannot import FastMCP: %s", e)
        raise

mcp = FastMCP("VN Tools")

# ... (đăng ký tools của bạn như trước)
if __name__ == "__main__":
    # Chạy server theo giao thức STDIO cho MCP
    mcp.run(transport="stdio")
