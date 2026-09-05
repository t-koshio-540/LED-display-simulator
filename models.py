import os
import json
from config import SECTIONS_DIR, DATA_DIR

class Page:
    """1つの静止画（ページ）を表すモデル"""
    def __init__(self, duration=1000, items=None):
        self.duration = duration  # 持続時間 (ミリ秒)
        self.items = items or []  # [{'code': '0000', 'x': 0, 'y': 0}, ...]

    def to_dict(self):
        return {
            "duration": self.duration,
            "items": self.items
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            duration=data.get("duration", 1000),
            items=data.get("items", [])
        )

class Section:
    """セクションデータのモデル（複数のページと切り替え条件を保持）"""
    def __init__(self, prefix="", section_id="00000000", condition_type="REPEAT", condition_val=1, pages=None):
        self.prefix = prefix                # 10桁の文字列 (例: AAABBBBBBB)
        self.section_id = section_id        # 8桁の数字 (例: 00000000)
        self.condition_type = condition_type # "REPEAT" または "SPACE"
        self.condition_val = condition_val   # REPEAT時の繰り返し回数
        self.pages = pages or []            # [Page, Page, ...]

    @property
    def filename(self):
        return f"{self.prefix}-S{self.section_id}.sec"

    def save(self):
        path = os.path.join(SECTIONS_DIR, self.filename)
        data = {
            "prefix": self.prefix,
            "section_id": self.section_id,
            "condition_type": self.condition_type,
            "condition_val": self.condition_val,
            "pages": [p.to_dict() for p in self.pages]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def load(cls, filename):
        path = os.path.join(SECTIONS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        pages_data = data.get("pages", [])
        pages = [Page.from_dict(p) for p in pages_data]
        
        # 過去フォーマットとの互換性（直下に items や duration がある場合）
        if not pages and "items" in data:
            pages = [Page(duration=data.get("duration", 1000), items=data.get("items", []))]

        return cls(
            prefix=data.get("prefix", ""),
            section_id=data.get("section_id", "00000000"),
            condition_type=data.get("condition_type", "REPEAT"),
            condition_val=data.get("condition_val", 1),
            pages=pages
        )

class Project:
    """プロジェクトデータのモデル"""
    def __init__(self, prefix="", name="", section_files=None):
        self.prefix = prefix                # 10桁の共通文字列
        self.name = name                    # 可変長文字列 ("あいうえお")
        self.section_files = section_files or [] # [.sec ファイル名のリスト]

    @property
    def filename(self):
        return f"{self.prefix}{self.name}.prj"

    def save(self):
        path = os.path.join(DATA_DIR, self.filename)
        data = {
            "prefix": self.prefix,
            "name": self.name,
            "section_files": self.section_files
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def load(cls, filename):
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            prefix=data.get("prefix", ""),
            name=data.get("name", ""),
            section_files=data.get("section_files", [])
        )