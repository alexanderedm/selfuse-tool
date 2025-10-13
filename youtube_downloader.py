"""YouTube 下載器模組"""
import os
import json
import subprocess
from logger import logger


class YouTubeDownloader:
    """YouTube 影片/音樂下載器"""

    def __init__(self, output_dir=None):
        """初始化下載器

        Args:
            output_dir (str): 輸出目錄
        """
        self.output_dir = output_dir or "Z:/Shuvi/下載"

    def extract_video_id(self, url):
        """從 URL 提取影片 ID

        Args:
            url (str): YouTube URL

        Returns:
            str: 影片 ID,失敗則返回 None
        """
        import re

        # 支援多種 YouTube URL 格式
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|music\.youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def search_youtube(self, query, max_results=10):
        """搜尋 YouTube 影片

        Args:
            query (str): 搜尋關鍵字
            max_results (int): 最大結果數

        Returns:
            list: 搜尋結果列表
        """
        try:
            # 使用 yt-dlp 搜尋
            cmd = [
                'yt-dlp',
                f'ytsearch{max_results}:{query}',
                '--dump-json',
                '--skip-download',
                '--no-warnings',
                '--extractor-args', 'youtube:player_client=android',  # 使用 Android 客戶端避開 bot 檢測
                '--no-check-certificate'  # 跳過 SSL 憑證檢查
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,  # 改為 False,手動處理編碼
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if result.returncode != 0:
                stderr = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "未知錯誤"
                logger.error(f"搜尋失敗: {stderr}")
                return []

            # 解析 JSON 結果
            stdout = result.stdout.decode('utf-8', errors='ignore')
            results = []
            for line in stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    video_info = json.loads(line)
                    results.append({
                        'id': video_info.get('id', ''),
                        'title': video_info.get('title', '未知標題'),
                        'duration': video_info.get('duration', 0),
                        'thumbnail': video_info.get('thumbnail', ''),
                        'webpage_url': video_info.get('webpage_url', ''),
                        'uploader': video_info.get('uploader', '未知作者')
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"解析 JSON 失敗: {e}, 內容: {line[:100]}")
                    continue

            logger.info(f"搜尋完成,找到 {len(results)} 個結果")
            return results

        except subprocess.TimeoutExpired:
            logger.error("搜尋超時")
            return []
        except Exception as e:
            logger.exception(f"搜尋時發生錯誤: {e}")
            return []

    def download_audio(self, url, category="下載", progress_callback=None):
        """下載 YouTube 音訊

        Args:
            url (str): YouTube URL
            category (str): 分類名稱
            progress_callback (callable): 進度回調函數

        Returns:
            dict: {'success': bool, 'message': str, 'song_info': dict}
        """
        try:
            # 建立輸出目錄
            output_path = os.path.join(self.output_dir, category)
            os.makedirs(output_path, exist_ok=True)

            # 下載音訊和元數據
            logger.info(f"開始下載: {url}")

            # 先獲取影片資訊
            info_cmd = [
                'yt-dlp',
                '--dump-json',
                '--skip-download',
                '--no-warnings',
                '--extractor-args', 'youtube:player_client=android',
                '--no-check-certificate',
                url
            ]

            info_result = subprocess.run(
                info_cmd,
                capture_output=True,
                text=False,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if info_result.returncode != 0:
                stderr = info_result.stderr.decode('utf-8', errors='ignore') if info_result.stderr else "未知錯誤"
                return {
                    'success': False,
                    'message': f'無法獲取影片資訊: {stderr}',
                    'song_info': None
                }

            stdout = info_result.stdout.decode('utf-8', errors='ignore')
            video_info = json.loads(stdout)
            video_id = video_info.get('id', '')
            video_title = video_info.get('title', '未知標題')

            # 清理檔名中的非法字元
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            audio_filename = f"{safe_title}-{video_id}.mp3"
            json_filename = f"{safe_title}-{video_id}.json"

            audio_path = os.path.join(output_path, audio_filename)
            json_path = os.path.join(output_path, json_filename)

            # 檢查是否已下載
            if os.path.exists(audio_path) and os.path.exists(json_path):
                logger.info(f"檔案已存在: {audio_filename}")
                return {
                    'success': True,
                    'message': '檔案已存在',
                    'song_info': {
                        'audio_path': audio_path,
                        'json_path': json_path
                    }
                }

            # 下載音訊
            # 使用更新的策略避開 YouTube 的 bot 檢測
            download_cmd = [
                'yt-dlp',
                '-x',  # 只下載音訊
                '--audio-format', 'mp3',
                '--audio-quality', '0',  # 最佳品質
                '-o', os.path.join(output_path, f'{safe_title}-{video_id}.%(ext)s'),
                '--embed-thumbnail',  # 嵌入縮圖
                '--add-metadata',  # 添加元數據
                '--no-warnings',
                '--extractor-args', 'youtube:player_client=android',  # 使用 Android 客戶端
                '--no-check-certificate',
                # 添加更多避開 bot 檢測的參數
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                url
            ]

            # 嘗試使用瀏覽器 cookies (依序嘗試 Chrome, Edge, Firefox)
            # cookies 是避開 403 錯誤的最有效方法
            browser_found = False
            try:
                for browser in ['chrome', 'edge', 'firefox']:
                    test_cmd = ['yt-dlp', '--cookies-from-browser', browser, '--skip-download', '--no-warnings', url]
                    test_result = subprocess.run(
                        test_cmd,
                        capture_output=True,
                        timeout=15,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    if test_result.returncode == 0:
                        download_cmd.extend(['--cookies-from-browser', browser])
                        logger.info(f"使用 {browser} 的 cookies 來避開 bot 檢測")
                        browser_found = True
                        break

                if not browser_found:
                    logger.warning("無法從瀏覽器讀取 cookies,將使用基本模式下載")
            except Exception as e:
                logger.warning(f"無法從瀏覽器讀取 cookies: {e}")
                # 繼續執行下載,不使用 cookies

            download_result = subprocess.run(
                download_cmd,
                capture_output=True,
                text=False,
                timeout=300,  # 5 分鐘超時
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if download_result.returncode != 0:
                stderr = download_result.stderr.decode('utf-8', errors='ignore') if download_result.stderr else "未知錯誤"
                logger.error(f"下載失敗: {stderr}")
                return {
                    'success': False,
                    'message': f'下載失敗: {stderr}',
                    'song_info': None
                }

            # 儲存 JSON 元數據
            song_metadata = {
                'id': video_id,
                'title': video_title,
                'webpage_url': video_info.get('webpage_url', url),
                'duration': video_info.get('duration', 0),
                'thumbnail': video_info.get('thumbnail', ''),
                'audio_filename': audio_filename,
                'uploader': video_info.get('uploader', '未知作者'),
                'upload_date': video_info.get('upload_date', ''),
                'description': video_info.get('description', '')
            }

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(song_metadata, f, ensure_ascii=False, indent=4)

            logger.info(f"下載完成: {audio_filename}")

            return {
                'success': True,
                'message': '下載成功',
                'song_info': {
                    'audio_path': audio_path,
                    'json_path': json_path,
                    'metadata': song_metadata
                }
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': '下載超時(超過5分鐘)',
                'song_info': None
            }
        except Exception as e:
            logger.exception(f"下載時發生錯誤: {e}")
            return {
                'success': False,
                'message': f'下載時發生錯誤: {str(e)}',
                'song_info': None
            }

    def check_ytdlp_installed(self):
        """檢查 yt-dlp 是否已安裝

        Returns:
            bool: 是否已安裝
        """
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
