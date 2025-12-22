"""播放統計分析模組

提供進階的播放統計和分析功能：
- 時段分析（熱力圖數據）
- 播放趨勢分析
- 分類統計
- 播放時長統計
"""
import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.core.logger import logger


class StatisticsManager:
    """播放統計分析管理器"""

    def __init__(self, history_manager):
        """初始化統計管理器

        Args:
            history_manager: PlayHistoryManager 實例
        """
        self.history_manager = history_manager

    def get_hourly_heatmap(self, days: int = 30) -> Dict[str, List[int]]:
        """取得按小時的播放熱力圖數據

        Args:
            days: 分析最近幾天的數據

        Returns:
            熱力圖數據 {
                'hours': [0-23],
                'weekdays': ['Monday', 'Tuesday', ...],
                'data': [[hour0_mon, hour1_mon, ...], [hour0_tue, ...], ...]
            }
        """
        # 初始化數據結構 [weekday][hour]
        heatmap_data = [[0 for _ in range(24)] for _ in range(7)]

        # 取得最近播放記錄
        recent_plays = self.history_manager.get_recent_plays(limit=1000)

        # 計算時間範圍
        now = datetime.now()
        start_date = now - timedelta(days=days)

        # 統計播放次數
        for play in recent_plays:
            try:
                played_at = datetime.fromisoformat(play['played_at'])

                # 檢查是否在時間範圍內
                if played_at < start_date:
                    continue

                weekday = played_at.weekday()  # 0=Monday, 6=Sunday
                hour = played_at.hour

                heatmap_data[weekday][hour] += 1

            except (ValueError, KeyError):
                continue

        return {
            'hours': list(range(24)),
            'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                        'Friday', 'Saturday', 'Sunday'],
            'data': heatmap_data
        }

    def get_daily_plays(self, days: int = 30) -> Dict[str, List]:
        """取得每日播放次數

        Args:
            days: 分析最近幾天的數據

        Returns:
            每日播放數據 {
                'dates': ['2024-01-01', '2024-01-02', ...],
                'counts': [10, 15, 8, ...]
            }
        """
        # 初始化數據
        date_counts = defaultdict(int)

        # 計算日期範圍
        now = datetime.now()
        start_date = now - timedelta(days=days)

        # 初始化所有日期
        for i in range(days + 1):
            date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            date_counts[date] = 0

        # 統計播放次數
        recent_plays = self.history_manager.get_recent_plays(limit=1000)

        for play in recent_plays:
            try:
                played_at = datetime.fromisoformat(play['played_at'])

                if played_at < start_date:
                    continue

                date = played_at.strftime('%Y-%m-%d')
                date_counts[date] += 1

            except (ValueError, KeyError):
                continue

        # 排序並返回
        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[date] for date in sorted_dates]

        return {
            'dates': sorted_dates,
            'counts': counts
        }

    def get_category_statistics(self, songs_getter) -> Dict[str, int]:
        """取得分類播放統計

        Args:
            songs_getter: 取得歌曲資訊的函數 (song_id -> song_dict)

        Returns:
            分類統計 {category_name: play_count}
        """
        category_counts = defaultdict(int)

        # 取得播放次數統計
        play_counts = self.history_manager.history_data.get('play_counts', {})

        for song_id, count in play_counts.items():
            song = songs_getter(song_id)
            if song:
                category = song.get('category', '未分類')
                category_counts[category] += count

        return dict(category_counts)

    def get_duration_statistics(self, songs_getter) -> Dict:
        """取得播放時長統計

        Args:
            songs_getter: 取得歌曲資訊的函數 (song_id -> song_dict)

        Returns:
            時長統計 {
                'total_duration': 總播放時長（秒）,
                'average_duration': 平均歌曲時長（秒）,
                'duration_distribution': 時長分布 {range: count}
            }
        """
        total_duration = 0
        durations = []
        duration_distribution = defaultdict(int)

        # 取得播放次數統計
        play_counts = self.history_manager.history_data.get('play_counts', {})

        for song_id, count in play_counts.items():
            song = songs_getter(song_id)
            if song and song.get('duration'):
                duration = song['duration']
                durations.append(duration)
                total_duration += duration * count

                # 計算時長分布（按分鐘區間）
                duration_range = f"{int(duration // 60)}-{int(duration // 60) + 1} 分鐘"
                duration_distribution[duration_range] += count

        average_duration = sum(durations) / len(durations) if durations else 0

        return {
            'total_duration': total_duration,
            'average_duration': average_duration,
            'duration_distribution': dict(duration_distribution)
        }

    def get_top_artists(self, songs_getter, limit: int = 10) -> List[Dict]:
        """取得最常播放的藝術家排行

        Args:
            songs_getter: 取得歌曲資訊的函數 (song_id -> song_dict)
            limit: 返回的數量

        Returns:
            藝術家排行 [{'artist': name, 'play_count': count}, ...]
        """
        artist_counts = defaultdict(int)

        # 取得播放次數統計
        play_counts = self.history_manager.history_data.get('play_counts', {})

        for song_id, count in play_counts.items():
            song = songs_getter(song_id)
            if song:
                artist = song.get('uploader', '未知')
                artist_counts[artist] += count

        # 排序並返回
        sorted_artists = sorted(
            artist_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {'artist': artist, 'play_count': count}
            for artist, count in sorted_artists
        ]

    def get_listening_time_by_period(self, songs_getter, days: int = 30) -> Dict:
        """取得時段聆聽時間統計

        Args:
            songs_getter: 取得歌曲資訊的函數 (song_id -> song_dict)
            days: 分析最近幾天的數據

        Returns:
            時段統計 {
                'morning': 早上總時長（秒）,
                'afternoon': 下午總時長（秒）,
                'evening': 晚上總時長（秒）,
                'night': 深夜總時長（秒）
            }
        """
        period_durations = {
            'morning': 0,     # 6:00-12:00
            'afternoon': 0,   # 12:00-18:00
            'evening': 0,     # 18:00-22:00
            'night': 0        # 22:00-6:00
        }

        # 取得最近播放記錄
        recent_plays = self.history_manager.get_recent_plays(limit=1000)

        # 計算時間範圍
        now = datetime.now()
        start_date = now - timedelta(days=days)

        for play in recent_plays:
            try:
                played_at = datetime.fromisoformat(play['played_at'])

                if played_at < start_date:
                    continue

                hour = played_at.hour
                song_id = play['song_id']
                song = songs_getter(song_id)

                if not song or not song.get('duration'):
                    continue

                duration = song['duration']

                # 判斷時段
                if 6 <= hour < 12:
                    period_durations['morning'] += duration
                elif 12 <= hour < 18:
                    period_durations['afternoon'] += duration
                elif 18 <= hour < 22:
                    period_durations['evening'] += duration
                else:
                    period_durations['night'] += duration

            except (ValueError, KeyError):
                continue

        return period_durations

    def get_summary_statistics(self, songs_getter) -> Dict:
        """取得總覽統計

        Args:
            songs_getter: 取得歌曲資訊的函數 (song_id -> song_dict)

        Returns:
            統計總覽
        """
        total_plays = self.history_manager.get_total_plays()
        play_counts = self.history_manager.history_data.get('play_counts', {})
        unique_songs = len(play_counts)

        # 計算總播放時長
        total_duration = 0
        for song_id, count in play_counts.items():
            song = songs_getter(song_id)
            if song and song.get('duration'):
                total_duration += song['duration'] * count

        # 取得最常播放的歌曲
        most_played = self.history_manager.get_most_played(limit=1)
        favorite_song = None
        if most_played:
            song_id = most_played[0]['song_id']
            song = songs_getter(song_id)
            if song:
                favorite_song = {
                    'title': song.get('title', '未知'),
                    'play_count': most_played[0]['play_count']
                }

        # 取得最常播放的分類
        category_stats = self.get_category_statistics(songs_getter)
        favorite_category = None
        if category_stats:
            favorite_category = max(category_stats.items(), key=lambda x: x[1])

        return {
            'total_plays': total_plays,
            'unique_songs': unique_songs,
            'total_duration_seconds': total_duration,
            'total_duration_hours': total_duration / 3600,
            'favorite_song': favorite_song,
            'favorite_category': {
                'name': favorite_category[0],
                'play_count': favorite_category[1]
            } if favorite_category else None,
            'average_plays_per_song': total_plays / unique_songs if unique_songs > 0 else 0
        }
