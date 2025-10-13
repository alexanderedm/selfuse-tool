"""測試音樂播放控制器"""
import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from music_player_controller import MusicPlayerController


class TestMusicPlayerController:
    """測試 MusicPlayerController 類別"""

    @pytest.fixture
    def mock_music_manager(self, temp_config_file):
        """建立模擬的音樂管理器"""
        from config_manager import ConfigManager
        config_manager = ConfigManager(temp_config_file)

        music_manager = Mock()
        music_manager.config_manager = config_manager
        return music_manager

    @pytest.fixture
    def sample_songs(self, temp_music_dir):
        """建立測試用的歌曲列表"""
        # 建立測試音訊檔案
        song1_path = os.path.join(temp_music_dir, 'test1.mp3')
        song2_path = os.path.join(temp_music_dir, 'test2.mp3')
        song3_path = os.path.join(temp_music_dir, 'test3.mp3')

        # 建立空檔案
        for path in [song1_path, song2_path, song3_path]:
            with open(path, 'wb') as f:
                f.write(b'fake mp3 data')

        songs = [
            {
                'id': 'test1',
                'title': 'Test Song 1',
                'audio_path': song1_path,
                'duration': 180,
                'category': 'test'
            },
            {
                'id': 'test2',
                'title': 'Test Song 2',
                'audio_path': song2_path,
                'duration': 200,
                'category': 'test'
            },
            {
                'id': 'test3',
                'title': 'Test Song 3',
                'audio_path': song3_path,
                'duration': 150,
                'category': 'test'
            }
        ]
        return songs

    def test_init(self, mock_music_manager):
        """測試初始化"""
        controller = MusicPlayerController(mock_music_manager)

        assert controller.music_manager == mock_music_manager
        assert controller.current_song is None
        assert controller.playlist == []
        assert controller.current_index == -1
        assert controller.is_playing is False
        assert controller.is_paused is False
        assert controller.play_mode == 'sequential'
        assert controller.played_indices == []

    def test_set_playlist(self, mock_music_manager, sample_songs):
        """測試設定播放列表"""
        controller = MusicPlayerController(mock_music_manager)

        controller.set_playlist(sample_songs)
        assert controller.playlist == sample_songs
        assert controller.current_index == 0

        controller.set_playlist(sample_songs, index=2)
        assert controller.current_index == 2

    @patch('pygame.mixer.music')
    def test_play_song_success(self, mock_mixer, mock_music_manager, sample_songs):
        """測試播放歌曲成功"""
        controller = MusicPlayerController(mock_music_manager)

        result = controller.play_song(sample_songs[0])

        assert result is True
        assert controller.is_playing is True
        assert controller.is_paused is False
        assert controller.current_song == sample_songs[0]
        assert controller.start_time > 0
        mock_mixer.load.assert_called_once_with(sample_songs[0]['audio_path'])
        mock_mixer.play.assert_called_once()

    @patch('pygame.mixer.music')
    def test_play_song_failure(self, mock_mixer, mock_music_manager, sample_songs):
        """測試播放歌曲失敗"""
        controller = MusicPlayerController(mock_music_manager)

        # 模擬載入失敗
        mock_mixer.load.side_effect = Exception("File not found")

        result = controller.play_song(sample_songs[0])

        assert result is False
        assert controller.is_playing is False

    @patch('pygame.mixer.music')
    def test_toggle_play_pause(self, mock_mixer, mock_music_manager, sample_songs):
        """測試播放/暫停切換"""
        controller = MusicPlayerController(mock_music_manager)
        controller.set_playlist(sample_songs)

        # 第一次呼叫:沒有歌曲,播放第一首
        state = controller.toggle_play_pause()
        assert state == 'playing'
        assert controller.is_playing is True

        # 第二次呼叫:暫停
        state = controller.toggle_play_pause()
        assert state == 'paused'
        assert controller.is_paused is True
        mock_mixer.pause.assert_called_once()

        # 第三次呼叫:恢復播放
        state = controller.toggle_play_pause()
        assert state == 'playing'
        assert controller.is_paused is False
        mock_mixer.unpause.assert_called_once()

    @patch('pygame.mixer.music')
    def test_play_next_sequential(self, mock_mixer, mock_music_manager, sample_songs):
        """測試順序播放下一首"""
        controller = MusicPlayerController(mock_music_manager)
        controller.set_playlist(sample_songs, index=0)
        controller.play_mode = 'sequential'

        # 播放下一首
        song = controller.play_next()
        assert song == sample_songs[1]
        assert controller.current_index == 1

        # 再播放下一首
        song = controller.play_next()
        assert song == sample_songs[2]
        assert controller.current_index == 2

        # 最後一首後循環到第一首
        song = controller.play_next()
        assert song == sample_songs[0]
        assert controller.current_index == 0

    @patch('pygame.mixer.music')
    def test_play_next_repeat_one(self, mock_mixer, mock_music_manager, sample_songs):
        """測試單曲循環模式"""
        controller = MusicPlayerController(mock_music_manager)
        controller.set_playlist(sample_songs, index=1)
        controller.play_mode = 'repeat_one'

        # 播放下一首(應該重播當前歌曲)
        song = controller.play_next()
        assert song == sample_songs[1]
        assert controller.current_index == 1

        # 再次播放下一首(仍然是同一首)
        song = controller.play_next()
        assert song == sample_songs[1]
        assert controller.current_index == 1

    @patch('pygame.mixer.music')
    def test_play_next_shuffle(self, mock_mixer, mock_music_manager, sample_songs):
        """測試隨機播放模式"""
        controller = MusicPlayerController(mock_music_manager)
        controller.set_playlist(sample_songs, index=0)
        controller.play_mode = 'shuffle'

        # 播放 3 首歌曲
        played_songs = []
        for _ in range(3):
            song = controller.play_next()
            played_songs.append(song)

        # 確認所有歌曲都被播放過
        assert len(played_songs) == 3
        assert len(controller.played_indices) == 3

        # 播放第 4 首時,應該重置並重新隨機
        song = controller.play_next()
        assert len(controller.played_indices) == 1  # 重置後只有 1 個

    @patch('pygame.mixer.music')
    def test_play_previous(self, mock_mixer, mock_music_manager, sample_songs):
        """測試播放上一首"""
        controller = MusicPlayerController(mock_music_manager)
        controller.set_playlist(sample_songs, index=1)

        # 播放上一首
        song = controller.play_previous()
        assert song == sample_songs[0]
        assert controller.current_index == 0

        # 第一首的上一首是最後一首
        song = controller.play_previous()
        assert song == sample_songs[2]
        assert controller.current_index == 2

    @patch('pygame.mixer.music')
    def test_set_volume(self, mock_mixer, mock_music_manager):
        """測試設定音量"""
        controller = MusicPlayerController(mock_music_manager)

        controller.set_volume(70)
        assert controller.volume == 0.7
        mock_mixer.set_volume.assert_called_with(0.7)

        controller.set_volume(100)
        assert controller.volume == 1.0
        mock_mixer.set_volume.assert_called_with(1.0)

    def test_cycle_play_mode(self, mock_music_manager):
        """測試循環切換播放模式"""
        controller = MusicPlayerController(mock_music_manager)

        # sequential -> repeat_all
        mode = controller.cycle_play_mode()
        assert mode == 'repeat_all'

        # repeat_all -> repeat_one
        mode = controller.cycle_play_mode()
        assert mode == 'repeat_one'

        # repeat_one -> shuffle
        mode = controller.cycle_play_mode()
        assert mode == 'shuffle'
        assert controller.played_indices == []  # 切換到隨機時清空記錄

        # shuffle -> sequential
        mode = controller.cycle_play_mode()
        assert mode == 'sequential'

    def test_get_play_mode_config(self, mock_music_manager):
        """測試取得播放模式配置"""
        controller = MusicPlayerController(mock_music_manager)

        controller.play_mode = 'sequential'
        config = controller.get_play_mode_config()
        assert config['text'] == '➡️ 順序播放'

        controller.play_mode = 'shuffle'
        config = controller.get_play_mode_config()
        assert config['text'] == '🔀 隨機播放'

    @patch('pygame.mixer.music')
    def test_get_current_position(self, mock_mixer, mock_music_manager, sample_songs):
        """測試取得當前播放位置"""
        controller = MusicPlayerController(mock_music_manager)

        # 沒有歌曲時
        pos, duration = controller.get_current_position()
        assert pos == 0
        assert duration == 0

        # 播放歌曲
        controller.play_song(sample_songs[0])
        pos, duration = controller.get_current_position()
        assert pos >= 0
        assert duration == 180

    @patch('pygame.mixer.music')
    def test_stop(self, mock_mixer, mock_music_manager, sample_songs):
        """測試停止播放"""
        controller = MusicPlayerController(mock_music_manager)
        controller.play_song(sample_songs[0])

        controller.stop()
        assert controller.is_playing is False
        assert controller.is_paused is False
        mock_mixer.stop.assert_called_once()

    @patch('pygame.mixer.music')
    def test_cleanup(self, mock_mixer, mock_music_manager, sample_songs):
        """測試清理資源"""
        controller = MusicPlayerController(mock_music_manager)
        controller.play_song(sample_songs[0])

        controller.cleanup()
        mock_mixer.stop.assert_called_once()
