# server.py
import logging
try:
    from mcp.server.fastmcp import FastMCP
    logging.warning("Using FastMCP from mcp.server.fastmcp")
except Exception:
    from fastmcp import FastMCP
    logging.warning("Using FastMCP from fastmcp")

mcp = FastMCP("VN Tools Minimal")

@mcp.tool()
def ping(text: str) -> str:
    """Echo input to verify tool pipeline."""
    return f"pong: {text}"

@mcp.tool()
def time_now() -> str:
    """Return current server time ISO."""
    import datetime
    return datetime.datetime.now().isoformat()

if __name__ == "__main__":
    mcp.run(transport="stdio")
