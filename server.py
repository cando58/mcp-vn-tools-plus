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
