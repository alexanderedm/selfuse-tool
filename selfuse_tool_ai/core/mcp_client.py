import asyncio
import json
import signal
from asyncio.subprocess import PIPE


class ChromeMCP:
    def __init__(self):
        self.proc = None
        self._seq = 0
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the chrome-devtools-mcp server via npx."""
        self.proc = await asyncio.create_subprocess_exec(
            "npx", "-y", "chrome-devtools-mcp@latest",
            stdin=PIPE, stdout=PIPE, stderr=PIPE
        )

    async def stop(self):
        """Stop the MCP server cleanly."""
        if self.proc and self.proc.returncode is None:
            self.proc.send_signal(signal.SIGINT)
            try:
                await asyncio.wait_for(self.proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.proc.kill()
        self.proc = None

    async def call_tool(self, method: str, params: dict = None):
        """Send a JSON-RPC request to the MCP server and return the result."""
        params = params or {}
        async with self._lock:
            self._seq += 1
            req_id = str(self._seq)
            request = {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": method,
                "params": params,
            }
            data = json.dumps(request) + "\n"
            # Send request
            self.proc.stdin.write(data.encode())
            await self.proc.stdin.drain()
            # Await response
            while True:
                line = await self.proc.stdout.readline()
                if not line:
                    continue
                response = json.loads(line.decode())
                if response.get("id") == req_id:
                    if "result" in response:
                        return response["result"]
                    else:
                        raise RuntimeError(f"MCP error: {response}")
