import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "image")
DATA_DIR = os.path.join(BASE_DIR, "data")
SECTIONS_DIR = os.path.join(DATA_DIR, "sections")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# デフォルトの 10x10 LED行列形状
DEFAULT_LED_MATRIX = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

def init_directories():
    """必要なディレクトリを作成"""
    for path in [IMAGE_DIR, DATA_DIR, SECTIONS_DIR]:
        os.makedirs(path, exist_ok=True)

def load_led_matrix():
    """設定ファイルからLEDドット行列を読み込む"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("led_matrix", DEFAULT_LED_MATRIX)
        except Exception:
            pass
    return DEFAULT_LED_MATRIX

def save_led_matrix(matrix):
    """設定ファイルへLEDドット行列を保存"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"led_matrix": matrix}, f, indent=4)