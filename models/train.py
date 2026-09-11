import json
import os

class TrainBand:
    """車体帯（長方形/角丸長方形）データクラス"""
    def __init__(self, x=0, y=0, width=100, height=20, radius=0, color="#FF0000"):
        self.x = int(x)          # 表示器左上からの相対X (ドット)
        self.y = int(y)          # 表示器左上からの相対Y (ドット)
        self.width = int(width)  # 幅 (ドット)
        self.height = int(height)# 高さ (ドット)
        self.radius = int(radius)# 角丸半径 (ドット)
        self.color = color       # 塗りつぶし色 (Hex)

    def to_dict(self):
        return {
            "x": self.x, "y": self.y,
            "width": self.width, "height": self.height,
            "radius": self.radius, "color": self.color
        }

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

class Train:
    """車両設定クラス"""
    def __init__(self, prefix="AAABBBBBBB", body_color="#C0C0C0", window_gap=4, window_radius=4, bands=None):
        self.prefix = prefix
        self.body_color = body_color  # ステンレス風灰色（デフォルト）
        self.window_gap = int(window_gap)      # 隙間幅 (ドット, デフォルト4)
        self.window_radius = int(window_radius) # 半径 (ドット, デフォルト4)
        self.bands = bands if bands is not None else []  # TrainBandのリスト

    @property
    def filepath(self):
        os.makedirs("./data/trains", exist_ok=True)
        return f"./data/trains/{self.prefix}.tra"

    def save(self):
        data = {
            "prefix": self.prefix,
            "body_color": self.body_color,
            "window_gap": self.window_gap,
            "window_radius": self.window_radius,
            "bands": [b.to_dict() for b in self.bands]
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath_or_prefix):
        path = filepath_or_prefix
        if not path.endswith(".tra"):
            path = f"./data/trains/{filepath_or_prefix}.tra"
        
        if not os.path.exists(path):
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        bands = [TrainBand.from_dict(b) for b in data.get("bands", [])]
        return cls(
            prefix=data.get("prefix", "AAABBBBBBB"),
            body_color=data.get("body_color", "#C0C0C0"),
            window_gap=data.get("window_gap", 4),
            window_radius=data.get("window_radius", 4),
            bands=bands
        )