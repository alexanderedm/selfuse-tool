"""
Web-enabled Orchestrator that pushes real-time updates via WebSocket.
"""
import asyncio
from typing import Any, Dict, Callable, Optional
import sys
import os

# 確保可以導入 selfuse_tool_ai 模組
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from selfuse_tool_ai.core.llm import chat_structured
from selfuse_tool_ai.core.mcp_client import ChromeMCP

CONFIRM_REQUIRED = {"click", "type", "navigate", "submit"}


class WebOrchestrator:
    """Orchestrator with WebSocket support for real-time UI updates."""

    def __init__(self, mcp: ChromeMCP, memory, rag):
        self.mcp = mcp
        self.memory = memory
        self.rag = rag
        self.log_callback: Optional[Callable] = None
        self.confirm_callback: Optional[Callable] = None

    def set_log_callback(self, callback: Callable):
        """Set callback for logging messages to WebSocket."""
        self.log_callback = callback

    def set_confirm_callback(self, callback: Callable):
        """Set callback for requesting user confirmation."""
        self.confirm_callback = callback

    async def log(self, message: str, level: str = "info"):
        """Send log message to WebSocket."""
        if self.log_callback:
            await self.log_callback({"type": "log", "level": level, "message": message})

    async def run_task(self, user_goal: str) -> None:
        """Plan and execute a task based on the user goal."""
        try:
            await self.log(f"📝 收到任務: {user_goal}", "info")

            # Gather context from memory and RAG
            await self.log("🔍 收集上下文資訊...", "info")
            context = self.rag.search(user_goal, k=5) if self.rag else []
            history = self.memory.fetch_recent() if self.memory else []

            # Generate plan using LLM
            await self.log("🤖 使用 AI 規劃執行步驟...", "info")
            plan = await chat_structured(
                system="You are a safe browser agent. Only perform sensitive actions with user confirmation.",
                messages=[*history, {"role": "user", "content": user_goal}],
                schema={
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "selector": {"type": "string"},
                                "text": {"type": "string"},
                                "url": {"type": "string"}
                            },
                            "required": ["action"]
                        }
                    }
                },
                extra_context=context,
            )

            steps = plan.get("steps", [])
            if not steps:
                await self.log("⚠️ 未生成任何執行步驟", "warning")
                return

            await self.log(f"✅ 已規劃 {len(steps)} 個步驟", "success")

            # Execute each step
            for i, step in enumerate(steps, 1):
                action = step.get("action")
                await self.log(f"▶️ 步驟 {i}/{len(steps)}: {action}", "info")

                # Request confirmation for sensitive actions
                if action in CONFIRM_REQUIRED:
                    if self.confirm_callback:
                        ok = await self.confirm_callback(i, step)
                        if not ok:
                            await self.log(f"🛑 用戶取消步驟 {i}", "warning")
                            break
                    else:
                        await self.log(f"⚠️ 敏感操作 '{action}' 需要確認，但未設定確認回調", "warning")

                # Execute step
                try:
                    await self.execute_step(step)
                    await self.log(f"✅ 步驟 {i} 完成", "success")
                except Exception as e:
                    await self.log(f"❌ 步驟 {i} 失敗: {str(e)}", "error")
                    raise

            await self.log("🎉 任務完成！", "success")

        except Exception as e:
            await self.log(f"❌ 任務執行失敗: {str(e)}", "error")
            raise

    async def execute_step(self, step: Dict[str, Any]) -> None:
        """Execute a single step using the MCP client."""
        action = step.get("action")

        if action == "navigate":
            url = step.get("url")
            await self.log(f"🌐 導航到: {url}", "info")
            await self.mcp.call_tool("page.navigate", {"url": url})

        elif action == "click":
            selector = step.get("selector")
            await self.log(f"🖱️ 點擊元素: {selector}", "info")
            await self.mcp.call_tool("page.click", {"selector": selector})

        elif action == "type":
            selector = step.get("selector")
            text = step.get("text")
            await self.log(f"⌨️ 輸入文字到 {selector}", "info")
            await self.mcp.call_tool("page.type", {
                "selector": selector,
                "text": text
            })

        elif action == "screenshot":
            await self.log("📸 截圖", "info")
            await self.mcp.call_tool("page.screenshot", {})

        else:
            await self.log(f"⚠️ 未知操作: {action}", "warning")
