
import asyncio, json, os, sys, logging, websockets, subprocess, signal

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("MCP_PIPE")

ENDPOINT = os.getenv("MCP_ENDPOINT")

async def bridge(ws_url: str, cmd: list):
    log.info("Connecting to WebSocket server...")
    async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as ws:
        # start child
        log.info("Successfully connected to WebSocket server")
        proc = await asyncio.create_subprocess_exec(*cmd, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        log.info("Started %s process", cmd[-1])

        async def ws_to_stdio():
            async for msg in ws:
                proc.stdin.write(msg.encode("utf-8") + b"\n")
                await proc.stdin.drain()

        async def stdio_to_ws():
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                await ws.send(line.decode("utf-8").rstrip("\n"))

        await asyncio.gather(ws_to_stdio(), stdio_to_ws())

def main():
    if not ENDPOINT:
        log.error("ERROR: Missing MCP_ENDPOINT env.")
        sys.exit(1)
    server_script = os.environ.get("SERVER_SCRIPT", "server.py")
    cmd = [sys.executable, server_script]
    asyncio.run(bridge(ENDPOINT, cmd))

if __name__ == "__main__":
    main()
