"""批次更新 import 路徑的腳本"""
import os
import re
from pathlib import Path

# 定義舊 import 到新 import 的映射
IMPORT_MAPPINGS = {
    # 核心模組
    'from audio_manager import': 'from src.core.audio_manager import',
    'from config_manager import': 'from src.core.config_manager import',
    'from logger import': 'from src.core.logger import',
    'from constants import': 'from src.core.constants import',

    # 音訊處理模組
    'from audio_player import': 'from src.audio.audio_player import',
    'from audio_processor import': 'from src.audio.audio_processor import',
    'from equalizer_filter import': 'from src.audio.equalizer_filter import',

    # 音樂播放器 - 視窗
    'from music_window import': 'from src.music.windows.music_window import',
    'from music_equalizer_dialog import': 'from src.music.windows.music_equalizer_dialog import',

    # 音樂播放器 - 視圖
    'from music_header_view import': 'from src.music.views.music_header_view import',
    'from music_library_view import': 'from src.music.views.music_library_view import',
    'from music_playback_view import': 'from src.music.views.music_playback_view import',
    'from music_search_view import': 'from src.music.views.music_search_view import',
    'from music_lyrics_view import': 'from src.music.views.music_lyrics_view import',

    # 音樂播放器 - 對話框
    'from music_download_dialog import': 'from src.music.dialogs.music_download_dialog import',
    'from music_history_dialog import': 'from src.music.dialogs.music_history_dialog import',
    'from music_playlist_dialog import': 'from src.music.dialogs.music_playlist_dialog import',

    # 音樂播放器 - 管理器
    'from music_manager import': 'from src.music.managers.music_manager import',
    'from playlist_manager import': 'from src.music.managers.playlist_manager import',
    'from play_history_manager import': 'from src.music.managers.play_history_manager import',

    # 音樂播放器 - 動作
    'from music_song_actions import': 'from src.music.actions.music_song_actions import',
    'from music_folder_actions import': 'from src.music.actions.music_folder_actions import',

    # 音樂播放器 - 工具
    'from music_metadata_fetcher import': 'from src.music.utils.music_metadata_fetcher import',
    'from music_metadata_multi_source import': 'from src.music.utils.music_metadata_multi_source import',
    'from music_file_manager import': 'from src.music.utils.music_file_manager import',
    'from lyrics_parser import': 'from src.music.utils.lyrics_parser import',
    'from subtitle_converter import': 'from src.music.utils.subtitle_converter import',
    'from youtube_downloader import': 'from src.music.utils.youtube_downloader import',
    'from music_equalizer import': 'from src.music.utils.music_equalizer import',
    'from music_player_controller import': 'from src.music.utils.music_player_controller import',

    # RSS 模組
    'from rss_manager import': 'from src.rss.rss_manager import',
    'from rss_window import': 'from src.rss.rss_window import',
    'from rss_filter_manager import': 'from src.rss.rss_filter_manager import',
    'from rss_entry_list_view import': 'from src.rss.rss_entry_list_view import',
    'from rss_feed_list_view import': 'from src.rss.rss_feed_list_view import',
    'from rss_preview_view import': 'from src.rss.rss_preview_view import',

    # 視窗模組
    'from settings_window import': 'from src.windows.settings_window import',
    'from stats_window import': 'from src.windows.stats_window import',
    'from changelog_window import': 'from src.windows.changelog_window import',

    # 工具模組
    'from clipboard_monitor import': 'from src.utils.clipboard_monitor import',
    'from path_utils import': 'from src.utils.path_utils import',
    'from discord_presence import': 'from src.utils.discord_presence import',
    'from ui_theme import': 'from src.utils.ui_theme import',
}


def update_imports_in_file(file_path):
    """Update import paths in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Apply all mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made.append(f"{old_import} -> {new_import}")

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"OK Updated: {file_path}")
            for change in changes_made:
                print(f"  - {change}")
            return True
        else:
            return False

    except Exception as e:
        print(f"ERROR {file_path}: {e}")
        return False


def find_python_files(directory):
    """Recursively find all Python files"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Exclude __pycache__ and .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache', 'venv', 'env']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    """Main function"""
    import sys
    # Fix Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    base_dir = Path(__file__).parent

    # Directories to process
    directories = [
        base_dir / 'src',
        base_dir / 'tests',
    ]

    total_files = 0
    updated_files = 0

    for directory in directories:
        if not directory.exists():
            print(f"Warning: Directory does not exist: {directory}")
            continue

        print(f"\nProcessing directory: {directory}")
        print("=" * 80)

        python_files = find_python_files(directory)

        for file_path in python_files:
            total_files += 1
            if update_imports_in_file(file_path):
                updated_files += 1

    print("\n" + "=" * 80)
    print(f"Done! Processed {total_files} files, updated {updated_files} files")


if __name__ == '__main__':
    main()
