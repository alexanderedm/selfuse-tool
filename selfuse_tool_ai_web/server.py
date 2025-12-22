"""
FastAPI server for AI Browser Assistant Web UI.
"""
import asyncio
import os
import sys
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# 確保可以導入 selfuse_tool_ai 模組
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from selfuse_tool_ai.core.mcp_client import ChromeMCP
from selfuse_tool_ai.core.memory import MemoryStore
from selfuse_tool_ai.core.rag import Rag
from selfuse_tool_ai_web.web_orchestrator import WebOrchestrator

# FastAPI app
app = FastAPI(title="AI Browser Assistant")

# Global instances
mcp_client: ChromeMCP = None
orchestrator: WebOrchestrator = None
active_websockets: Set[WebSocket] = set()
pending_confirmations: Dict[str, asyncio.Event] = {}
confirmation_results: Dict[str, bool] = {}

# 掛載靜態檔案
static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class TaskRequest(BaseModel):
    goal: str


@app.on_event("startup")
async def startup_event():
    """Initialize MCP client and orchestrator on startup."""
    global mcp_client, orchestrator

    print("[INFO] Starting AI Browser Assistant Web Server...")

    # 檢查 API key - 必須在導入其他模組前完成
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        try:
            from src.core.secure_config import get_openai_api_key
            api_key = get_openai_api_key()
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                print(f"[INFO] API key loaded from secure config (starts with: {api_key[:10]}...)")
        except Exception as e:
            print(f"[WARN] Could not load API key from secure config: {e}")

    if not api_key:
        print("[WARN] No OpenAI API key found - AI features will not work")
    else:
        print(f"[INFO] OpenAI API key is configured (starts with: {api_key[:10]}...)")

    # 重置 LLM 客戶端以確保使用新的 API key
    try:
        from selfuse_tool_ai.core.llm import reset_client
        reset_client()
        print("[INFO] LLM client reset to use new API key")
    except Exception as e:
        print(f"[WARN] Could not reset LLM client: {e}")

    # Initialize components
    mcp_client = ChromeMCP()
    memory = MemoryStore(db_path="./data/memory.sqlite")
    rag = Rag(index_path="./data/chroma")
    orchestrator = WebOrchestrator(mcp=mcp_client, memory=memory, rag=rag)

    print("[INFO] Core components initialized")

    # Start MCP client in background (optional - server will still work without it)
    try:
        await mcp_client.start()
        print("[INFO] MCP client (Chrome DevTools) started successfully")
    except Exception as e:
        # MCP is optional - server can still run without it
        print(f"[WARN] MCP client not available (this is OK): {type(e).__name__}")
        print("[INFO] Browser automation features will be unavailable")
        print("[INFO] You can still use the web interface for other tasks")

    print("[INFO] Server startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if mcp_client:
        await mcp_client.stop()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    html_path = os.path.join(static_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "ok",
        "mcp_running": mcp_client is not None and mcp_client.proc is not None,
        "active_connections": len(active_websockets)
    })


@app.post("/api/task")
async def submit_task(request: TaskRequest):
    """Submit a new task for execution."""
    if not orchestrator:
        return JSONResponse(
            {"error": "Orchestrator not initialized"},
            status_code=503
        )

    # Run task in background
    asyncio.create_task(orchestrator.run_task(request.goal))

    return JSONResponse({"status": "Task submitted", "goal": request.goal})


async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients."""
    disconnected = set()
    for ws in active_websockets:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)

    # Remove disconnected clients
    active_websockets.difference_update(disconnected)


async def log_callback(message: dict):
    """Callback for orchestrator to send log messages."""
    await broadcast_message(message)


async def confirm_callback(step_index: int, step: dict) -> bool:
    """Callback for orchestrator to request user confirmation."""
    # Generate unique confirmation ID
    confirm_id = f"confirm_{step_index}"

    # Create event for waiting
    event = asyncio.Event()
    pending_confirmations[confirm_id] = event

    # Send confirmation request to all clients
    await broadcast_message({
        "type": "confirm_request",
        "confirm_id": confirm_id,
        "step_index": step_index,
        "step": step
    })

    # Wait for user response (with timeout)
    try:
        await asyncio.wait_for(event.wait(), timeout=60.0)
        result = confirmation_results.get(confirm_id, False)
    except asyncio.TimeoutError:
        result = False

    # Cleanup
    pending_confirmations.pop(confirm_id, None)
    confirmation_results.pop(confirm_id, None)

    return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    active_websockets.add(websocket)

    # Set callbacks on first connection
    if orchestrator:
        orchestrator.set_log_callback(log_callback)
        orchestrator.set_confirm_callback(confirm_callback)

    try:
        await websocket.send_json({
            "type": "connected",
            "message": "已連接到 AI 瀏覽器助手"
        })

        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle confirmation responses
            if data.get("type") == "confirm_response":
                confirm_id = data.get("confirm_id")
                approved = data.get("approved", False)

                if confirm_id in pending_confirmations:
                    confirmation_results[confirm_id] = approved
                    pending_confirmations[confirm_id].set()

    except WebSocketDisconnect:
        active_websockets.discard(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        active_websockets.discard(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
