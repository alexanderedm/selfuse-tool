"""測試 MusicWindow._play_next 函數的完整測試套件"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.music.windows.music_window import MusicWindow


@pytest.fixture
def mock_music_manager():
    """建立 Mock 音樂管理器"""
    manager = Mock()
    manager.music_root_path = "test_music"
    manager.config_manager = Mock()
    manager.config_manager.get_music_volume.return_value = 50
    manager.format_duration.return_value = "03:30"
    return manager


@pytest.fixture
def sample_playlist():
    """建立範例播放清單"""
    return [
        {
            'id': 'song1',
            'title': 'Song 1',
            'audio_path': 'path/to/song1.mp3',
            'uploader': 'Artist 1',
            'category': 'Category 1',
            'duration': 210
        },
        {
            'id': 'song2',
            'title': 'Song 2',
            'audio_path': 'path/to/song2.mp3',
            'uploader': 'Artist 2',
            'category': 'Category 2',
            'duration': 180
        },
        {
            'id': 'song3',
            'title': 'Song 3',
            'audio_path': 'path/to/song3.mp3',
            'uploader': 'Artist 3',
            'category': 'Category 3',
            'duration': 240
        }
    ]


@pytest.fixture
def music_window(mock_music_manager):
    """建立測試用的 MusicWindow 實例"""
    with patch('pygame.mixer.init'):
        window = MusicWindow(mock_music_manager, tk_root=None)
        window._play_song = Mock()  # Mock _play_song 以避免實際播放
    return window


class TestPlayNextEmptyPlaylist:
    """測試空播放清單的情況"""

    def test_play_next_empty_playlist(self, music_window):
        """測試播放清單為空時的行為"""
        music_window.playlist = []
        music_window._play_next()
        # 不應該播放任何歌曲
        music_window._play_song.assert_not_called()


class TestPlayNextRepeatOneMode:
    """測試單曲循環模式"""

    def test_repeat_one_valid_index(self, music_window, sample_playlist):
        """測試單曲循環模式 - 有效索引"""
        music_window.playlist = sample_playlist
        music_window.current_index = 1
        music_window.play_mode = 'repeat_one'

        music_window._play_next()

        # 應該重播當前歌曲
        music_window._play_song.assert_called_once_with(sample_playlist[1])
        assert music_window.current_index == 1

    def test_repeat_one_first_song(self, music_window, sample_playlist):
        """測試單曲循環模式 - 第一首歌"""
        music_window.playlist = sample_playlist
        music_window.current_index = 0
        music_window.play_mode = 'repeat_one'

        music_window._play_next()

        music_window._play_song.assert_called_once_with(sample_playlist[0])
        assert music_window.current_index == 0

    def test_repeat_one_last_song(self, music_window, sample_playlist):
        """測試單曲循環模式 - 最後一首歌"""
        music_window.playlist = sample_playlist
        music_window.current_index = 2
        music_window.play_mode = 'repeat_one'

        music_window._play_next()

        music_window._play_song.assert_called_once_with(sample_playlist[2])
        assert music_window.current_index == 2

    def test_repeat_one_invalid_index_negative(self, music_window, sample_playlist):
        """測試單曲循環模式 - 無效索引（負數）"""
        music_window.playlist = sample_playlist
        music_window.current_index = -1
        music_window.play_mode = 'repeat_one'

        music_window._play_next()

        # 索引無效時不應該播放
        music_window._play_song.assert_not_called()

    def test_repeat_one_invalid_index_too_large(self, music_window, sample_playlist):
        """測試單曲循環模式 - 無效索引（超出範圍）"""
        music_window.playlist = sample_playlist
        music_window.current_index = 5
        music_window.play_mode = 'repeat_one'

        music_window._play_next()

        # 索引無效時不應該播放
        music_window._play_song.assert_not_called()


class TestPlayNextShuffleMode:
    """測試隨機播放模式"""

    @patch('random.choice')
    def test_shuffle_no_played_indices(self, mock_random_choice, music_window, sample_playlist):
        """測試隨機模式 - 沒有已播放記錄"""
        music_window.playlist = sample_playlist
        music_window.current_index = 0
        music_window.play_mode = 'shuffle'
        music_window.played_indices = []
        mock_random_choice.return_value = 1

        music_window._play_next()

        # 應該從所有歌曲中隨機選擇
        mock_random_choice.assert_called_once()
        called_list = mock_random_choice.call_args[0][0]
        assert len(called_list) == 3  # 所有歌曲都可選
        assert set(called_list) == {0, 1, 2}

        music_window._play_song.assert_called_once_with(sample_playlist[1])
        assert music_window.current_index == 1
        assert 1 in music_window.played_indices

    @patch('random.choice')
    def test_shuffle_with_played_indices(self, mock_random_choice, music_window, sample_playlist):
        """測試隨機模式 - 有已播放記錄"""
        music_window.playlist = sample_playlist
        music_window.current_index = 0
        music_window.play_mode = 'shuffle'
        music_window.played_indices = [0, 1]  # 已播放前兩首
        mock_random_choice.return_value = 2

        music_window._play_next()

        # 應該只從未播放的歌曲中選擇
        mock_random_choice.assert_called_once()
        called_list = mock_random_choice.call_args[0][0]
        assert called_list == [2]  # 只有第三首未播放

        music_window._play_song.assert_called_once_with(sample_playlist[2])
        assert music_window.current_index == 2
        assert music_window.played_indices == [0, 1, 2]

    @patch('random.choice')
    def test_shuffle_all_songs_played_reset(self, mock_random_choice, music_window, sample_playlist):
        """測試隨機模式 - 所有歌曲都已播放，重置記錄"""
        music_window.playlist = sample_playlist
        music_window.current_index = 2
        music_window.play_mode = 'shuffle'
        music_window.played_indices = [0, 1, 2]  # 所有歌曲都已播放
        mock_random_choice.return_value = 0

        music_window._play_next()

        # 應該清空記錄並重新開始
        assert music_window.played_indices == [0]  # 重置後只有新播放的歌曲

        # 應該從所有歌曲中隨機選擇
        mock_random_choice.assert_called_once()
        called_list = mock_random_choice.call_args[0][0]
        assert len(called_list) == 3
        assert set(called_list) == {0, 1, 2}

        music_window._play_song.assert_called_once_with(sample_playlist[0])
        assert music_window.current_index == 0


class TestPlayNextSequentialMode:
    """測試順序播放模式"""

    def test_sequential_middle_song(self, music_window, sample_playlist):
        """測試順序模式 - 中間的歌曲"""
        music_window.playlist = sample_playlist
        music_window.current_index = 1
        music_window.play_mode = 'sequential'

        music_window._play_next()

        music_window._play_song.assert_called_once_with(sample_playlist[2])
        assert music_window.current_index == 2

    def test_sequential_last_song_wraps_to_first(self, music_window, sample_playlist):
        """測試順序模式 - 最後一首歌，跳到第一首"""
        music_window.playlist = sample_playlist
        music_window.current_index = 2
        music_window.play_mode = 'sequential'

        music_window._play_next()

        # 應該循環回第一首
        music_window._play_song.assert_called_once_with(sample_playlist[0])
        assert music_window.current_index == 0

    def test_sequential_first_song(self, music_window, sample_playlist):
        """測試順序模式 - 第一首歌"""
        music_window.playlist = sample_playlist
        music_window.current_index = 0
        music_window.play_mode = 'sequential'

        music_window._play_next()

        music_window._play_song.assert_called_once_with(sample_playlist[1])
        assert music_window.current_index == 1


class TestPlayNextRepeatAllMode:
    """測試列表循環模式"""

    def test_repeat_all_middle_song(self, music_window, sample_playlist):
        """測試列表循環模式 - 中間的歌曲"""
        music_window.playlist = sample_playlist
        music_window.current_index = 1
        music_window.play_mode = 'repeat_all'

        music_window._play_next()

        music_window._play_song.assert_called_once_with(sample_playlist[2])
        assert music_window.current_index == 2

    def test_repeat_all_last_song_wraps_to_first(self, music_window, sample_playlist):
        """測試列表循環模式 - 最後一首歌，循環回第一首"""
        music_window.playlist = sample_playlist
        music_window.current_index = 2
        music_window.play_mode = 'repeat_all'

        music_window._play_next()

        # 應該循環回第一首
        music_window._play_song.assert_called_once_with(sample_playlist[0])
        assert music_window.current_index == 0


class TestPlayNextEdgeCases:
    """測試邊界情況"""

    def test_single_song_playlist_sequential(self, music_window):
        """測試單首歌曲的播放清單 - 順序模式"""
        single_song_playlist = [{
            'id': 'song1',
            'title': 'Only Song',
            'audio_path': 'path/to/song.mp3',
            'uploader': 'Artist',
            'category': 'Category',
            'duration': 180
        }]
        music_window.playlist = single_song_playlist
        music_window.current_index = 0
        music_window.play_mode = 'sequential'

        music_window._play_next()

        # 應該循環播放同一首歌
        music_window._play_song.assert_called_once_with(single_song_playlist[0])
        assert music_window.current_index == 0

    def test_single_song_playlist_shuffle(self, music_window):
        """測試單首歌曲的播放清單 - 隨機模式"""
        single_song_playlist = [{
            'id': 'song1',
            'title': 'Only Song',
            'audio_path': 'path/to/song.mp3',
            'uploader': 'Artist',
            'category': 'Category',
            'duration': 180
        }]
        music_window.playlist = single_song_playlist
        music_window.current_index = 0
        music_window.play_mode = 'shuffle'
        music_window.played_indices = []

        music_window._play_next()

        # 應該播放唯一的歌曲
        music_window._play_song.assert_called_once_with(single_song_playlist[0])
        assert music_window.current_index == 0

    def test_unknown_play_mode_defaults_to_sequential(self, music_window, sample_playlist):
        """測試未知播放模式 - 應該按順序播放"""
        music_window.playlist = sample_playlist
        music_window.current_index = 1
        music_window.play_mode = 'unknown_mode'

        music_window._play_next()

        # 應該按順序播放
        music_window._play_song.assert_called_once_with(sample_playlist[2])
        assert music_window.current_index == 2
