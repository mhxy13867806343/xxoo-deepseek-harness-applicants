"""
Harness Index — Theme Manager
Manages Dark/Light mode theme switching and persists settings to data/settings.json
"""

import os
import json

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'settings.json')


def load_theme_setting():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('theme', 'dark')
        except Exception:
            pass
    return 'dark'


def save_theme_setting(theme_name):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump({'theme': theme_name}, f, indent=2)
    except Exception as e:
        print(f"Error saving theme setting: {e}")
