"""
Entry point for the AI Browser Assistant.
This script sets up a system tray icon that launches a CustomTkinter UI for controlling
an AI-driven browser assistant built on chrome-devtools-mcp. The implementation here
is intentionally lightweight; extend each component in the core/ and ui/ modules to
support your desired workflows.
"""

import asyncio
import threading
import sys
import os

import pystray
from PIL import Image
import customtkinter as ctk

from selfuse_tool_ai.ui.main_window import MainWindow
from selfuse_tool_ai.core.mcp_client import ChromeMCP
from selfuse_tool_ai.core.orchestrator import Orchestrator
from selfuse_tool_ai.core.memory import Memory
from selfuse_tool_ai.core.rag import Rag
from selfuse_tool_ai.core.llm import ChatLLM


def run_app():
    """Initialise and start the tray icon and event loop."""
    # Load a simple placeholder icon. Replace `icon.png` with your own logo.
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    image = Image.open(icon_path)

    # Create instances of core components.
    mcp_client = ChromeMCP()
    memory = Memory(db_path="./data/memory.sqlite")
    rag = Rag(index_path="./data/chroma")
    llm = ChatLLM()
    orchestrator = Orchestrator(mcp_client=mcp_client, memory=memory, rag=rag, llm=llm)

    # Start MCP client in a background thread so it can run asynchronously.
    async def start_mcp():
        await mcp_client.start()

    threading.Thread(target=asyncio.run, args=(start_mcp(),), daemon=True).start()

    # Setup CTk UI main window.
    app_window = MainWindow(orchestrator)

    # Define tray menu actions.
    def on_open(icon, item):
        # Show or focus the main window.
        app_window.show()

    def on_quit(icon, item):
        icon.stop()
        # Perform cleanup before exit.
        asyncio.run(mcp_client.stop())
        sys.exit(0)

    menu = (pystray.MenuItem("Open AI Browser Assistant", on_open),
            pystray.MenuItem("Quit", on_quit))

    tray_icon = pystray.Icon(name="ai_browser_assistant", icon=image, title="AI Browser Assistant", menu=pystray.Menu(*menu))
    tray_icon.run()


if __name__ == "__main__":
    run_app()
