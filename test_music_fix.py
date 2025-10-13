# -*- coding: utf-8 -*-
"""Test music manager with UNC path fix"""
import sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from music_manager import MusicManager
from config_manager import ConfigManager

print('=' * 60)
print('Testing Music Manager with UNC Path Fix')
print('=' * 60)

# Initialize managers
cm = ConfigManager()
mm = MusicManager(cm)

print(f'\nMusic root path: {mm.music_root_path}')
is_net = mm.music_root_path.startswith("//") or mm.music_root_path.startswith("\\\\")
print(f'Is network path: {is_net}')

# Scan music library
print('\nScanning music library...')
result = mm.scan_music_library()

print(f'Success: {result["success"]}')
print(f'Message: {result["message"]}')

if result['success']:
    categories = mm.get_all_categories()
    all_songs = mm.get_all_songs()

    print(f'\nCategories found: {len(categories)}')
    print(f'Total songs: {len(all_songs)}')

    if categories:
        print(f'\nFirst 5 categories: {categories[:5]}')

    if all_songs:
        print('\nFirst song:')
        song = all_songs[0]
        print(f'  Title: {song["title"]}')
        print(f'  Category: {song["category"]}')
        print(f'  Duration: {mm.format_duration(song["duration"])}')

print('\n' + '=' * 60)
print('Test completed!')
print('=' * 60)
