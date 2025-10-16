"""批次更新測試檔案中的 @patch 裝飾器路徑"""
import os
import re
from pathlib import Path

# patch 路徑映射
PATCH_MAPPINGS = {
    # RSS相關模組的 patch
    r"@patch\('rss_window\.": r"@patch('src.rss.rss_window.",
    r"patch\('rss_window\.": r"patch('src.rss.rss_window.",

    # Settings window 相關
    r"@patch\('settings_window\.": r"@patch('src.windows.settings_window.",
    r"patch\('settings_window\.": r"patch('src.windows.settings_window.",

    # Stats window 相關
    r"@patch\('stats_window\.": r"@patch('src.windows.stats_window.",
    r"patch\('stats_window\.": r"patch('src.windows.stats_window.",

    # Music window 相關
    r"@patch\('music_window\.": r"@patch('src.music.windows.music_window.",
    r"patch\('music_window\.": r"patch('src.music.windows.music_window.",
}


def update_patches_in_file(file_path):
    """更新單一檔案中的 patch 路徑"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # 應用所有映射（使用正則表達式）
        for old_pattern, new_pattern in PATCH_MAPPINGS.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes_made.append(f"{old_pattern} -> {new_pattern}")

        # 只有當內容改變時才寫入
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


def main():
    """Main function"""
    import sys
    # Fix Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    base_dir = Path(__file__).parent
    tests_dir = base_dir / 'tests'

    total_files = 0
    updated_files = 0

    print(f"Processing directory: {tests_dir}")
    print("=" * 80)

    for file_path in tests_dir.glob('test_*.py'):
        total_files += 1
        if update_patches_in_file(file_path):
            updated_files += 1

    print("\n" + "=" * 80)
    print(f"Done! Processed {total_files} files, updated {updated_files} files")


if __name__ == '__main__':
    main()
