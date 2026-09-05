import os
from PIL import Image
from config import IMAGE_DIR

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

def apply_led_simulation(base_img, matrix):
    """再生用：格子サイズ（N倍）に拡大し、NxNのドットマスク行列を動的適用"""
    if not matrix or not isinstance(matrix, list) or not matrix[0]:
        grid_h, grid_w = 10, 10
    else:
        grid_h = len(matrix)
        grid_w = len(matrix[0])

    w, h = base_img.size
    scaled_w, scaled_h = w * grid_w, h * grid_h

    # 1. ニアレストネイバーで格子サイズ倍に拡大
    scaled_img = base_img.resize((scaled_w, scaled_h), Image.NEAREST)

    # 2. 格子サイズのドットマスク作成 (点灯: 255, 消灯: 0)
    mask_tile = Image.new("L", (grid_w, grid_h), 0)
    for y in range(grid_h):
        for x in range(grid_w):
            if y < len(matrix) and x < len(matrix[y]) and matrix[y][x] == 1:
                mask_tile.putpixel((x, y), 255)

    # 3. 画面全体にマスクをタイル配置
    full_mask = Image.new("L", (scaled_w, scaled_h))
    for y in range(0, scaled_h, grid_h):
        for x in range(0, scaled_w, grid_w):
            full_mask.paste(mask_tile, (x, y))

    # 4. 消灯時背景色 #000000 (RGB: 0, 0, 0)
    off_bg = Image.new("RGB", (scaled_w, scaled_h), (0, 0, 0))

    # 5. 点灯画像と消灯背景を合成
    return Image.composite(scaled_img, off_bg, full_mask)