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
import tkinter as tk
from tkinter import messagebox

import pystray
from PIL import Image
import customtkinter as ctk

from selfuse_tool_ai.ui.main_window import MainWindow
from selfuse_tool_ai.core.mcp_client import ChromeMCP
from selfuse_tool_ai.core.orchestrator import Orchestrator
from selfuse_tool_ai.core.memory import MemoryStore
from selfuse_tool_ai.core.rag import Rag


def run_app():
    """Initialise and start the tray icon and event loop."""
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "配置錯誤",
            "未設定 OpenAI API 金鑰！\n\n"
            "請設定環境變數 OPENAI_API_KEY 或在系統環境變數中新增。\n\n"
            "範例：\n"
            "set OPENAI_API_KEY=sk-your-api-key-here\n\n"
            "或在 Windows 系統設定中新增環境變數。"
        )
        root.destroy()
        sys.exit(1)

    # Load a simple placeholder icon. Replace `icon.png` with your own logo.
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")

    # 如果找不到圖示，創建一個簡單的臨時圖示
    if not os.path.exists(icon_path):
        from PIL import ImageDraw
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.text((10, 20), 'AI', fill='white')
    else:
        image = Image.open(icon_path)

    # Create instances of core components.
    mcp_client = ChromeMCP()
    memory = MemoryStore(db_path="./data/memory.sqlite")
    rag = Rag(index_path="./data/chroma")
    orchestrator = Orchestrator(mcp=mcp_client, memory=memory, rag=rag)

    # Start MCP client in a background thread so it can run asynchronously.
    async def start_mcp():
        await mcp_client.start()

    threading.Thread(target=asyncio.run, args=(start_mcp(),), daemon=True).start()

    # Setup CTk UI main window.
    app_window = None

    # Define tray menu actions.
    def on_open(icon, item):
        # Show or focus the main window.
        global app_window
        if app_window is None:
            app_window = MainWindow()
        else:
            app_window.deiconify()
            app_window.lift()

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
