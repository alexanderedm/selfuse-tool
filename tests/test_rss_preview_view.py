"""RSS Preview View 模組測試"""
import unittest
from unittest.mock import Mock, patch
import tkinter as tk
from tkinter import scrolledtext


class TestRSSPreviewView(unittest.TestCase):
    """RSSPreviewView 測試套件"""

    def setUp(self):
        """測試前置設定"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """測試後清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_init(self):
        """測試初始化"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        self.assertIsNotNone(view.preview_text)
        self.assertIsNotNone(view.open_browser_button)

    def test_show_preview(self):
        """測試顯示預覽"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        entry = {
            'title': 'Test Title',
            'published': '2025-01-01',
            'link': 'https://example.com',
            'content': 'Test content'
        }

        view.show_preview(entry)

        # 檢查預覽文字包含標題
        content = view.preview_text.get("1.0", tk.END)
        self.assertIn('Test Title', content)
        self.assertIn('2025-01-01', content)

    def test_show_preview_with_summary(self):
        """測試顯示預覽（使用摘要）"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        entry = {
            'title': 'Test Title',
            'published': '2025-01-01',
            'link': 'https://example.com',
            'summary': 'Test summary'
        }

        view.show_preview(entry)

        content = view.preview_text.get("1.0", tk.END)
        self.assertIn('Test summary', content)

    def test_clear_preview(self):
        """測試清空預覽"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        # 先顯示內容
        entry = {
            'title': 'Test',
            'published': '2025-01-01',
            'link': 'https://example.com',
            'content': 'Content'
        }
        view.show_preview(entry)

        # 然後清空
        view.clear_preview()

        content = view.preview_text.get("1.0", tk.END)
        self.assertIn('請選擇文章', content)

    def test_set_current_entry(self):
        """測試設定當前文章"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        entry = {
            'title': 'Test',
            'link': 'https://example.com'
        }

        view.set_current_entry(entry)

        self.assertEqual(view.current_entry, entry)

    @patch('webbrowser.open')
    def test_open_in_browser(self, mock_open):
        """測試在瀏覽器開啟"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        entry = {
            'title': 'Test',
            'link': 'https://example.com'
        }

        view.set_current_entry(entry)
        view._open_in_browser()

        mock_open.assert_called_once_with('https://example.com')

    @patch('tkinter.messagebox.showwarning')
    def test_open_in_browser_no_entry(self, mock_warning):
        """測試無文章時開啟瀏覽器"""
        from src.rss.rss_preview_view import RSSPreviewView

        parent = tk.Frame(self.root)
        view = RSSPreviewView(parent)

        view._open_in_browser()

        mock_warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
