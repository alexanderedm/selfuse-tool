import os
import sys
import json
import time
import requests
import zipfile
import shutil
import threading
import subprocess
from packaging import version
from src.plugins.plugin_base import Plugin
from src.core.logger import logger
from src.core.constants import APP_VERSION

GITHUB_REPO = "YOUR_GITHUB_USER/YOUR_REPO_NAME"  # TODO: Replace with actual repo
CHECK_INTERVAL = 3600 * 24  # Check once a day if running continuously, or on startup

class UpdaterPlugin(Plugin):
    @property
    def name(self) -> str:
        return "auto_updater"

    @property
    def description(self) -> str:
        return "Automatically checks for updates from GitHub and installs them."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def default_enabled(self) -> bool:
        return True

    def start(self) -> None:
        """Runs the update check in a background thread."""
        logger.info("UpdaterPlugin started. Checking for updates...")
        self.check_for_updates()

    def check_for_updates(self):
        try:
            # check config if allowed
            # For this 'modular' system, the plugin being enabled IS the permission.
            # But we might want a 'dry run' or 'notify only' mode? 
            # User said "If yes, automatically pull and update". So allow fully auto.
            
            latest_release = self._get_latest_release()
            if not latest_release:
                return

            remote_ver_str = latest_release['tag_name'].lstrip('v')
            local_ver = version.parse(APP_VERSION)
            remote_ver = version.parse(remote_ver_str)

            logger.info(f"Current version: {local_ver}, Latest version: {remote_ver}")

            if remote_ver > local_ver:
                logger.info("New version found! Starting update process...")
                asset_url = self._get_zip_asset_url(latest_release)
                if asset_url:
                    self._perform_update(asset_url)
                else:
                    logger.warning("No suitable asset found in release.")
            else:
                logger.info("Application is up to date.")

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")

    def _get_latest_release(self):
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Repository {GITHUB_REPO} not found or no releases.")
                return None
            else:
                logger.warning(f"GitHub API returned {response.status_code}")
                return None
        except requests.RequestException as e:
            logger.warning(f"Network error checking updates: {e}")
            return None

    def _get_zip_asset_url(self, release_data):
        for asset in release_data.get('assets', []):
            if asset['name'].endswith('.zip') or asset['content_type'] == 'application/zip':
                return asset['browser_download_url']
        # Fallback to source code zip
        return release_data.get('zipball_url')

    def _perform_update(self, asset_url):
        try:
            # 1. Download
            logger.info(f"Downloading update from {asset_url}...")
            download_path = "update_pkg.zip"
            extract_path = "update_temp"
            
            response = requests.get(asset_url, stream=True)
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 2. Extract
            logger.info("Extracting update...")
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # GitHub source zips usually have a root folder (repo-name-sha).
            # We need to find that folder and verify contents.
            # If it's a release artifact, it might be flat or nested.
            # Strategy: Find 'src' folder or 'main.py' in the extracted tree.
            
            update_source = extract_path
            # Check for nested root
            items = os.listdir(extract_path)
            if len(items) == 1 and os.path.isdir(os.path.join(extract_path, items[0])):
                update_source = os.path.join(extract_path, items[0])
            
            # 3. Create Updater Script
            bat_script = "update_restart.bat"
            
            # Application root is current working directory
            app_root = os.getcwd()
            
            # Command to restart execution
            # If we are running from python: python src/main.py
            # If exe, direct execution.
            # We assume python for this dev environment
            restart_cmd = f'"{sys.executable}" "{sys.argv[0]}"'
            if len(sys.argv) > 1:
                restart_cmd += " " + " ".join(f'"{arg}"' for arg in sys.argv[1:])

            script_content = f"""@echo off
echo Waiting for application to exit...
timeout /t 3 /nobreak > NUL
echo Updating files...
xcopy "{os.path.abspath(update_source)}\\*" "{app_root}" /E /H /Y /Q
echo Cleaning up...
rd /s /q "{os.path.abspath(extract_path)}"
del "{os.path.abspath(download_path)}"
echo Restarting application...
start "" {restart_cmd}
del "%~f0"
"""
            with open(bat_script, 'w') as f:
                f.write(script_content)

            logger.info("Update prepared. Restarting...")
            
            # 4. Execute and Exit
            subprocess.Popen([bat_script], shell=True)
            os._exit(0) # Force exit

        except Exception as e:
            logger.error(f"Update failed: {e}")
