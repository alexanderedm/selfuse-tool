from src.plugins.plugin_base import Plugin
from src.core.logger import logger
from src.core.secure_config import get_openai_api_key
from pystray import MenuItem as item
import os
import sys
import subprocess
import webbrowser
import time
import threading

class AIWebPlugin(Plugin):
    @property
    def name(self) -> str:
        return "ai_web_assistant"

    @property
    def description(self) -> str:
        return "Web-based AI Browser Assistant."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def default_enabled(self) -> bool:
        return True

    def start(self) -> None:
        pass

    def on_load(self, context) -> None:
        super().on_load(context)
        self.app = context
        self.server_process = None

    def on_unload(self) -> None:
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process = None
                logger.info("AI Web Server process terminated.")
            except:
                pass
        super().on_unload()

    def get_menu_items(self) -> list:
        return [
            item("🤖 AI 瀏覽器助手", self.open_ai_browser)
        ]

    def open_ai_browser(self):
        try:
            # Check if server running
            if self.server_process is not None and self.server_process.poll() is None:
                logger.info("AI Server already running, opening browser...")
                webbrowser.open("http://127.0.0.1:8000")
                self.app.show_notification("已開啟 AI 瀏覽器助手", "成功")
                return

            logger.info("Starting AI Web Server...")
            
            # Locate server.py
            # Current file is src/plugins/ai_web_plugin.py
            # Root is d:/VS
            # server is at d:/VS/../selfuse_tool_ai_web/server.py? 
            # In main.py: os.path.dirname(os.path.dirname(os.path.abspath(__file__))) -> project root (d:/VS)
            # server path: os.path.join(project_root, "selfuse_tool_ai_web", "server.py")
            
            # get project root from app context or calculate
            # context is usually main.py instance. 
            # main.py is in src/. 
            # We can use os.getcwd() if run from root.
            project_root = os.getcwd()
            server_script = os.path.join(project_root, "selfuse_tool_ai_web", "server.py")

            if not os.path.exists(server_script):
                # Try relative to src location if different
                # main.py logic: project_root = os.path.dirname(current_dir) where current_dir is src
                pass

            if not os.path.exists(server_script):
                self.app.show_notification("找不到 AI 瀏覽器助手伺服器", "錯誤")
                logger.error(f"Server script not found: {server_script}")
                return

            # Config API Key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                try:
                    api_key = get_openai_api_key()
                    if api_key:
                        os.environ["OPENAI_API_KEY"] = api_key
                except Exception as e:
                    logger.error(f"Failed to get API Key: {e}")

            if not api_key:
                self.app.show_notification("未設定 OpenAI API 金鑰", "配置錯誤")
                return

            # Python executable
            python_dir = os.path.dirname(sys.executable)
            pythonw_exe = os.path.join(python_dir, 'pythonw.exe')
            if not os.path.exists(pythonw_exe):
                pythonw_exe = sys.executable

            env = os.environ.copy()
            env["OPENAI_API_KEY"] = api_key

            log_file_path = os.path.join(project_root, "ai_browser_server.log")
            self.log_file = open(log_file_path, 'w', encoding='utf-8')

            self.server_process = subprocess.Popen(
                [pythonw_exe, "-m", "uvicorn",
                 "selfuse_tool_ai_web.server:app",
                 "--host", "127.0.0.1",
                 "--port", "8000"],
                cwd=project_root,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
                stdout=self.log_file,
                stderr=subprocess.STDOUT
            )

            logger.info("Waiting for server startup...")
            for i in range(10):
                time.sleep(0.5)
                try:
                    import urllib.request
                    urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1)
                    break
                except:
                    continue
            
            webbrowser.open("http://127.0.0.1:8000")
            self.app.show_notification("AI 瀏覽器助手已啟動", "成功")

        except Exception as e:
            logger.exception("Error starting AI browser")
            self.app.show_notification(f"啟動失敗: {e}", "錯誤")
