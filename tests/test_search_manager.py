"""測試 SearchManager 搜尋管理器

測試項目：
- 多條件搜尋
- 模糊匹配
- 搜尋歷史
"""
import pytest
from pathlib import Path
from src.music.managers.search_manager import SearchManager


class TestSearchManager:
    """測試搜尋管理器"""

    @pytest.fixture
    def manager(self, tmp_path):
        """創建測試用的搜尋管理器"""
        history_file = tmp_path / "search_history.json"
        return SearchManager(str(history_file), max_history=5)

    @pytest.fixture
    def sample_songs(self):
        """創建測試用的歌曲數據"""
        return [
            {
                'id': '1',
                'title': 'Shape of You',
                'category': 'Pop',
                'uploader': 'Ed Sheeran',
                'duration': 233
            },
            {
                'id': '2',
                'title': 'Bohemian Rhapsody',
                'category': 'Rock',
                'uploader': 'Queen',
                'duration': 354
            },
            {
                'id': '3',
                'title': 'Shape Up',
                'category': 'Pop',
                'uploader': 'Various',
                'duration': 180
            },
            {
                'id': '4',
                'title': 'Hello',
                'category': 'Pop',
                'uploader': 'Adele',
                'duration': 295
            },
        ]

    def test_basic_search(self, manager, sample_songs):
        """測試基本搜尋"""
        results = manager.search_songs(sample_songs, query='Shape', save_history=False)
        assert len(results) == 2
        assert results[0]['id'] in ['1', '3']

    def test_fuzzy_match(self, manager):
        """測試模糊匹配"""
        assert manager.fuzzy_match('Shape of You', 'shpe')
        assert manager.fuzzy_match('Bohemian Rhapsody', 'bohm')
        assert not manager.fuzzy_match('Hello', 'xyz')

    def test_category_filter(self, manager, sample_songs):
        """測試分類篩選"""
        results = manager.search_songs(
            sample_songs,
            categories=['Pop'],
            save_history=False
        )
        assert len(results) == 3
        assert all(s['category'] == 'Pop' for s in results)

    def test_duration_filter(self, manager, sample_songs):
        """測試時長篩選"""
        results = manager.search_songs(
            sample_songs,
            duration_min=200,
            duration_max=300,
            save_history=False
        )
        assert len(results) == 2
        assert all(200 <= s['duration'] <= 300 for s in results)

    def test_uploader_filter(self, manager, sample_songs):
        """測試上傳者篩選"""
        results = manager.search_songs(
            sample_songs,
            uploaders=['Ed Sheeran', 'Queen'],
            save_history=False
        )
        assert len(results) == 2

    def test_combined_filters(self, manager, sample_songs):
        """測試組合篩選"""
        results = manager.search_songs(
            sample_songs,
            query='Shape',
            categories=['Pop'],
            duration_max=250,
            save_history=False
        )
        assert len(results) == 2

    def test_search_history(self, manager, sample_songs):
        """測試搜尋歷史"""
        # 執行幾次搜尋
        manager.search_songs(sample_songs, query='Shape', save_history=True)
        manager.search_songs(sample_songs, query='Hello', save_history=True)
        manager.search_songs(sample_songs, query='Queen', save_history=True)

        # 檢查歷史
        history = manager.get_search_history()
        assert len(history) == 3
        assert history[0]['query'] == 'Queen'  # 最新的在前面

    def test_clear_history(self, manager, sample_songs):
        """測試清除歷史"""
        manager.search_songs(sample_songs, query='test', save_history=True)
        manager.clear_search_history()
        assert len(manager.get_search_history()) == 0

    def test_get_available_categories(self, manager, sample_songs):
        """測試取得可用分類"""
        categories = manager.get_available_categories(sample_songs)
        assert set(categories) == {'Pop', 'Rock'}

    def test_get_available_uploaders(self, manager, sample_songs):
        """測試取得可用上傳者"""
        uploaders = manager.get_available_uploaders(sample_songs)
        assert 'Ed Sheeran' in uploaders
        assert 'Queen' in uploaders
