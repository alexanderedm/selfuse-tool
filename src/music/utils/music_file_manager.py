"""音樂檔案管理模組

此模組負責處理音樂檔案和資料夾的操作，包括：
- 建立、重新命名、刪除資料夾
- 移動、刪除歌曲檔案
- 檔案路徑管理
"""
import os
import shutil
from src.core.logger import logger


class MusicFileManager:
    """音樂檔案管理器

    負責處理音樂檔案和資料夾的所有檔案系統操作。
    """

    def __init__(self, music_root_path):
        """初始化音樂檔案管理器

        Args:
            music_root_path (str): 音樂根目錄路徑
        """
        self.music_root_path = music_root_path

    def create_folder(self, folder_name):
        """建立新資料夾

        Args:
            folder_name (str): 資料夾名稱

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        # 驗證輸入
        if not folder_name or not folder_name.strip():
            logger.warning("資料夾名稱不能為空")
            return False

        folder_name = folder_name.strip()

        # 檢查資料夾是否已存在
        folder_path = os.path.join(self.music_root_path, folder_name)
        if os.path.exists(folder_path):
            logger.warning(f"資料夾已存在: {folder_name}")
            return False

        # 建立資料夾
        try:
            os.makedirs(folder_path, exist_ok=True)
            logger.info(f"成功建立資料夾: {folder_name}")
            return True
        except Exception as e:
            logger.error(f"建立資料夾失敗: {e}")
            return False

    def rename_folder(self, old_name, new_name):
        """重新命名資料夾

        Args:
            old_name (str): 舊資料夾名稱
            new_name (str): 新資料夾名稱

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        # 驗證輸入
        if not new_name or not new_name.strip():
            logger.warning("新資料夾名稱不能為空")
            return False

        new_name = new_name.strip()

        # 檢查是否為相同名稱
        if old_name == new_name:
            logger.warning("新舊名稱相同，無需重新命名")
            return False

        # 檢查舊資料夾是否存在
        old_path = os.path.join(self.music_root_path, old_name)
        if not os.path.exists(old_path):
            logger.warning(f"舊資料夾不存在: {old_name}")
            return False

        # 檢查新資料夾名稱是否已存在
        new_path = os.path.join(self.music_root_path, new_name)
        if os.path.exists(new_path):
            logger.warning(f"新資料夾名稱已存在: {new_name}")
            return False

        # 重新命名
        try:
            os.rename(old_path, new_path)
            logger.info(f"成功重新命名資料夾: {old_name} -> {new_name}")
            return True
        except Exception as e:
            logger.error(f"重新命名資料夾失敗: {e}")
            return False

    def delete_folder(self, folder_name):
        """刪除資料夾及其所有內容

        Args:
            folder_name (str): 資料夾名稱

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        folder_path = os.path.join(self.music_root_path, folder_name)

        # 檢查資料夾是否存在
        if not os.path.exists(folder_path):
            logger.warning(f"資料夾不存在: {folder_name}")
            return False

        # 刪除資料夾
        try:
            shutil.rmtree(folder_path)
            logger.info(f"成功刪除資料夾: {folder_name}")
            return True
        except Exception as e:
            logger.error(f"刪除資料夾失敗: {e}")
            return False

    def delete_song(self, song):
        """刪除歌曲檔案（包括音訊和 JSON 檔案）

        Args:
            song (dict): 歌曲資訊字典，必須包含 audio_path 和 json_path

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        audio_path = song.get('audio_path')
        json_path = song.get('json_path')

        # 檢查音訊檔案是否存在
        if not audio_path or not os.path.exists(audio_path):
            logger.warning("音訊檔案不存在或路徑無效")
            return False

        try:
            # 刪除音訊檔案
            os.remove(audio_path)
            logger.info(f"刪除音訊檔案: {audio_path}")

            # 刪除 JSON 檔案（如果存在）
            if json_path and os.path.exists(json_path):
                os.remove(json_path)
                logger.info(f"刪除 JSON 檔案: {json_path}")

            return True
        except Exception as e:
            logger.error(f"刪除歌曲失敗: {e}")
            return False

    def move_song(self, song, target_category):
        """移動歌曲到目標分類

        Args:
            song (dict): 歌曲資訊字典，必須包含 audio_path 和 json_path
            target_category (str): 目標分類名稱

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        audio_path = song.get('audio_path')
        json_path = song.get('json_path')

        # 檢查目標分類是否存在
        target_path = os.path.join(self.music_root_path, target_category)
        if not os.path.exists(target_path):
            logger.warning(f"目標分類不存在: {target_category}")
            return False

        # 取得檔名
        audio_filename = os.path.basename(audio_path)
        json_filename = os.path.basename(json_path) if json_path else None

        # 建立目標路徑
        target_audio_path = os.path.join(target_path, audio_filename)
        target_json_path = os.path.join(target_path, json_filename) if json_filename else None

        # 檢查目標檔案是否已存在
        if os.path.exists(target_audio_path):
            logger.warning(f"目標位置已存在同名檔案: {audio_filename}")
            return False

        try:
            # 移動音訊檔案
            shutil.move(audio_path, target_audio_path)
            logger.info(f"移動音訊檔案: {audio_path} -> {target_audio_path}")

            # 移動 JSON 檔案（如果存在）
            if json_path and os.path.exists(json_path):
                shutil.move(json_path, target_json_path)
                logger.info(f"移動 JSON 檔案: {json_path} -> {target_json_path}")

            return True
        except Exception as e:
            logger.error(f"移動歌曲失敗: {e}")
            return False

    def folder_exists(self, folder_name):
        """檢查資料夾是否存在

        Args:
            folder_name (str): 資料夾名稱

        Returns:
            bool: 存在返回 True，否則返回 False
        """
        folder_path = os.path.join(self.music_root_path, folder_name)
        return os.path.exists(folder_path)

    def get_folder_path(self, folder_name):
        """取得資料夾的完整路徑

        Args:
            folder_name (str): 資料夾名稱

        Returns:
            str: 資料夾的完整路徑
        """
        return os.path.join(self.music_root_path, folder_name)
