# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller 打包配置文件
用於建立 selftool.exe 可執行檔

使用方法:
    pyinstaller selftool.spec
"""

import sys
from pathlib import Path

# 專案根目錄
root_dir = Path(SPECPATH)

# 收集所有需要的資料文件
datas = [
    ('src', 'src'),  # 包含整個 src 目錄
    ('README.md', '.'),
    ('LICENSE', '.'),
]

# 收集隱藏導入（某些動態導入的模組）
hiddenimports = [
    'comtypes',
    'pycaw',
    'pystray',
    'PIL',
    'PIL._tkinter_finder',
    'customtkinter',
    'feedparser',
    'psutil',
    'pygame',
    'sounddevice',
    'soundfile',
    'numpy',
    'requests',
    'yt_dlp',
    'mutagen',
    'pypresence',
    'chromadb',
    'openai',
    'pydantic',
    'pydantic_core',
]

# 排除不需要的模組以減小檔案大小
excludes = [
    'matplotlib',
    'scipy',
    'pandas',
    'jupyter',
    'notebook',
    'IPython',
    'pytest',
    'unittest',
]

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[str(root_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='selftool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不顯示控制台視窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有 .ico 檔案，在這裡指定路徑
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='selftool',
)
