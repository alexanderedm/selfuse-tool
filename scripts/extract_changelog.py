#!/usr/bin/env python3
"""
從 CHANGELOG.md 提取特定版本的更新內容

用法:
    python extract_changelog.py v1.0.0
"""

import sys
import re
from pathlib import Path


def extract_version_changelog(version: str, changelog_path: Path = None) -> str:
    """提取特定版本的 changelog 內容

    Args:
        version: 版本號（例如 "v1.0.0" 或 "1.0.0"）
        changelog_path: CHANGELOG.md 的路徑

    Returns:
        該版本的 changelog 內容（Markdown 格式）
    """
    if changelog_path is None:
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"

    if not changelog_path.exists():
        return f"## {version}\n\n無法找到 CHANGELOG.md 文件。"

    # 移除版本號前綴 'v'
    version_clean = version.lstrip('v')

    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配版本區塊：## [版本號] - 日期
    # 例如：## [1.0.0] - 2025-10-28
    pattern = rf"## \[{re.escape(version_clean)}\].*?(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        # 嘗試匹配不帶括號的版本號
        pattern = rf"## {re.escape(version_clean)}.*?(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)

    if match:
        changelog_text = match.group(0).strip()

        # 移除底部的連結區段（如果有）
        # 例如：[1.0.0]: https://github.com/...
        changelog_text = re.sub(
            r'\n\[.*?\]:.*?$',
            '',
            changelog_text,
            flags=re.MULTILINE
        )

        return changelog_text
    else:
        return f"## {version}\n\n無法找到此版本的更新內容。請參閱 CHANGELOG.md。"


def main():
    if len(sys.argv) < 2:
        print("錯誤：請提供版本號", file=sys.stderr)
        print("用法：python extract_changelog.py v1.0.0", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]
    changelog = extract_version_changelog(version)
    print(changelog)


if __name__ == "__main__":
    main()
