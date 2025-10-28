import asyncio
from typing import Any, Dict

from .llm import chat_structured
from .mcp_client import ChromeMCP

CONFIRM_REQUIRED = {"click", "type", "navigate", "submit"}


class Orchestrator:
    def __init__(self, mcp: ChromeMCP, memory, rag):
        self.mcp = mcp
        self.memory = memory
        self.rag = rag

    async def run_task(self, user_goal: str) -> None:
        """Plan and execute a task based on the user goal."""
        # Gather context from memory and RAG
        context = self.rag.search(user_goal, k=5) if self.rag else []
        history = self.memory.fetch_recent() if self.memory else []
        plan = await chat_structured(
            system="You are a safe browser agent. Only perform sensitive actions with user confirmation.",
            messages=[*history, {"role": "user", "content": user_goal}],
            schema={"steps": [{"action": "string", "selector": "string?", "text": "string?", "url": "string?"}]},
            extra_context=context,
        )
        for i, step in enumerate(plan.get("steps", []), 1):
            action = step.get("action")
            if action in CONFIRM_REQUIRED:
                ok = await self.ask_user_confirmation(i, step)
                if not ok:
                    break
            await self.execute_step(step)

    async def ask_user_confirmation(self, idx: int, step: Dict[str, Any]) -> bool:
        """Request confirmation from the user before executing a sensitive step.
        This is a placeholder that should be overridden by UI integration."""
        # Always return True by default; implement UI prompt in production
        return True

    async def execute_step(self, step: Dict[str, Any]) -> None:
        """Execute a single step using the MCP client."""
        action = step.get("action")
        if action == "navigate":
            await self.mcp.call_tool("page.navigate", {"url": step.get("url")})
        elif action == "click":
            await self.mcp.call_tool("page.click", {"selector": step.get("selector")})
        elif action == "type":
            await self.mcp.call_tool(
                "page.type",
                {"selector": step.get("selector"), "text": step.get("text")},
            )
        elif action == "screenshot":
            await self.mcp.call_tool("page.screenshot", {})
