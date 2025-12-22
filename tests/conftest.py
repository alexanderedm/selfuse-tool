"""pytest 配置檔案"""
import pytest
import os
import sys
import tempfile
import json

# 將專案根目錄加入 Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
from unittest.mock import MagicMock

# ==================== Global UI Mocks ====================
# 必須在任何 src 模組被匯入前執行

# Mock tkinter
# Mock tkinter
class MockTk:
    def __init__(self, *args, **kwargs):
        pass
    def withdraw(self):
        pass
    def destroy(self):
        pass
    def lift(self):
        pass
    def focus_force(self):
        pass
    def mainloop(self):
        pass
    def attributes(self, *args, **kwargs):
        pass
    def winfo_exists(self):
        return 1
    def quit(self):
        pass

mock_tk = MagicMock()
mock_tk.Tk = MockTk
# 讓 TclError 存在，因為有些程式碼可能會捕獲它
mock_tk.TclError = Exception 
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()

# Smart Mock for Treeview
class MockTreeview(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.item_data = {}
        
    def insert(self, parent, index, iid=None, **kwargs):
        if iid is None:
            import uuid
            iid = str(uuid.uuid4())
        self.items.append(iid)
        self.item_data[iid] = kwargs
        return iid
        
    def get_children(self, item=None):
        return tuple(self.items)
        
    def item(self, iid, option=None, **kwargs):
        if kwargs:
            # Setting values
             if iid in self.item_data:
                 self.item_data[iid].update(kwargs)
        
        # Getting values
        if iid in self.item_data:
            if option == 'values':
                return self.item_data[iid].get('values', [])
            return self.item_data[iid]
        return {}
        
    def delete(self, *items):
        for item in items:
            if item in self.items:
                self.items.remove(item)
            if item in self.item_data:
                del self.item_data[item]
                
    def selection(self):
        return []

mock_ttk = MagicMock()
mock_ttk.Treeview = MockTreeview
sys.modules['tkinter.ttk'] = mock_ttk
mock_tk.ttk = mock_ttk

# Mock customtkinter (depends on tkinter)
class MockCTk(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def winfo_exists(self):
        return 1

class MockCTkFrame(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MockCTkButton(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MockCTkLabel(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockCTkFrame
mock_ctk.CTkButton = MockCTkButton
mock_ctk.CTkLabel = MockCTkLabel
sys.modules['customtkinter'] = mock_ctk

# Mock pystray
sys.modules['pystray'] = MagicMock()

# Mock pygame
mock_pygame = MagicMock()
mock_pygame.mixer = MagicMock()
mock_pygame.mixer.music = MagicMock()
sys.modules['pygame'] = mock_pygame
sys.modules['pygame.mixer'] = mock_pygame.mixer
# =========================================================


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
