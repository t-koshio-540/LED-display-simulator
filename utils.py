import os
import re
from PIL import Image
from config import IMAGE_DIR

def parse_x_range(range_str):
    """'01-14,16,20-23' のような範囲文字列を解析し整数のリストを返す"""
    if not range_str or not range_str.strip():
        return []
    
    result = []
    parts = range_str.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            subparts = part.split('-')
            if len(subparts) == 2 and subparts[0].strip().isdigit() and subparts[1].strip().isdigit():
                start = int(subparts[0].strip())
                end = int(subparts[1].strip())
                step = 1 if start <= end else -1
                result.extend(list(range(start, end + step, step)))
        elif part.isdigit():
            result.append(int(part))
    
    seen = set()
    unique_result = []
    for item in result:
        if item not in seen:
            seen.add(item)
            unique_result.append(item)
    return unique_result

def replace_x(pattern, value):
    """文字列内の連続する'X'を指定した値（桁数ゼロ埋め合わせ）で置換"""
    match = re.search(r'[Xx]+', pattern)
    if not match:
        return pattern
    
    x_str = match.group(0)
    width = len(x_str)
    formatted_val = f"{value:0{width}d}"
    
    start, end = match.span()
    return pattern[:start] + formatted_val + pattern[end:]

def replace_x_for_preview(pattern, range_str=""):
    """プレビュー用: Xを範囲の最小値、未指定時は0で置換"""
    match = re.search(r'[Xx]+', pattern)
    if not match:
        return pattern
    
    nums = parse_x_range(range_str)
    min_val = nums[0] if nums else 0
    return replace_x(pattern, min_val)

def render_raw_page(prefix, items):
    """プレビュー用：ビットマップ画像を配置・合成した1倍の画像を生成"""
    if hasattr(items, 'items'):
        items = items.items

    if not items:
        return Image.new("RGB", (128, 32), (0, 0, 0))

    loaded = []
    max_w, max_h = 1, 1
    for item in items:
        code = item.get("code", "0000")
        x, y = item.get("x", 0), item.get("y", 0)
        filename = f"{prefix}{code}.bmp"
        path = os.path.join(IMAGE_DIR, filename)

        if os.path.exists(path):
            img = Image.open(path).convert("RGB")
        else:
            img = Image.new("RGB", (16, 16), (255, 0, 255))
        
        loaded.append((img, x, y))
        max_w = max(max_w, x + img.width)
        max_h = max(max_h, y + img.height)

    canvas = Image.new("RGB", (max_w, max_h), (0, 0, 0))
    for img, x, y in loaded:
        canvas.paste(img, (x, y))
    return canvas

def render_bmp_direct(filepath):
    """単体のBMPファイルを直接読み込む（簡易再生用）"""
    if os.path.exists(filepath):
        try:
            return Image.open(filepath).convert("RGB")
        except Exception:
            pass
    return Image.new("RGB", (128, 32), (0, 0, 0))

def apply_led_simulation(base_img, matrix):
    """再生用：格子サイズ（N倍）に拡大し、NxNのドットマスク行列を動的適用"""
    if not matrix or not isinstance(matrix, list) or not matrix[0]:
        grid_h, grid_w = 10, 10
    else:
        grid_h = len(matrix)
        grid_w = len(matrix[0])

    w, h = base_img.size
    scaled_w, scaled_h = w * grid_w, h * grid_h

    scaled_img = base_img.resize((scaled_w, scaled_h), Image.NEAREST)

    mask_tile = Image.new("L", (grid_w, grid_h), 0)
    for y in range(grid_h):
        for x in range(grid_w):
            if y < len(matrix) and x < len(matrix[y]) and matrix[y][x] == 1:
                mask_tile.putpixel((x, y), 255)

    full_mask = Image.new("L", (scaled_w, scaled_h))
    for y in range(0, scaled_h, grid_h):
        for x in range(0, scaled_w, grid_w):
            full_mask.paste(mask_tile, (x, y))

    off_bg = Image.new("RGB", (scaled_w, scaled_h), (0, 0, 0))
    return Image.composite(scaled_img, off_bg, full_mask)