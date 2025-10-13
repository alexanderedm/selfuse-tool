"""pytest 配置檔案"""
import pytest
import os
import sys
import tempfile
import json

# 將專案根目錄加入 Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def temp_config_file():
    """建立臨時配置檔案"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        config = {
            'device_a': None,
            'device_b': None,
            'current_device': None,
            'auto_start': False,
            'usage_stats': {},
            'last_switch_time': None,
            'rss_feeds': {},
            'music_volume': 70
        }
        json.dump(config, f)
        temp_path = f.name

    yield temp_path

    # 清理
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def temp_music_dir():
    """建立臨時音樂目錄"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
