from PIL import Image, ImageDraw

def render_train_frame(led_image, train, dot_size=10):
    """
    LED表示器画像(led_image)の周囲に車両外観を描画して合成する
    :param led_image: PIL.Image (表示器本体のレンダリング画像)
    :param train: Train インスタンス
    :param dot_size: 格子設定の1ドットあたりのピクセルサイズ (規定値: 10px)
    :return: PIL.Image (車両全体画像)
    """
    led_w_px, led_h_px = led_image.size
    led_w_dots = led_w_px // dot_size
    led_h_dots = led_h_px // dot_size

    # 周囲マージン (左右32ドット, 上下16ドット)
    margin_x_dots = 32
    margin_y_dots = 16

    # 全体サイズ (px)
    total_w_dots = led_w_dots + margin_x_dots * 2
    total_h_dots = led_h_dots + margin_y_dots * 2
    
    total_w_px = total_w_dots * dot_size
    total_h_px = total_h_dots * dot_size

    # 表示器本体の左上原点座標 (px)
    led_origin_x = margin_x_dots * dot_size
    led_origin_y = margin_y_dots * dot_size

    # 1. 車体背景作成 (背景色で塗りつぶし)
    canvas = Image.new("RGB", (total_w_px, total_h_px), train.body_color)
    draw = ImageDraw.Draw(canvas)

    # 2. 車体帯（追加長方形）の描画
    for band in train.bands:
        bx1 = led_origin_x + band.x * dot_size
        by1 = led_origin_y + band.y * dot_size
        bx2 = bx1 + band.width * dot_size
        by2 = by1 + band.height * dot_size
        bradius = band.radius * dot_size

        if bradius > 0:
            draw.rounded_rectangle([bx1, by1, bx2, by2], radius=bradius, fill=band.color)
        else:
            draw.rectangle([bx1, by1, bx2, by2], fill=band.color)

    # 3. 表示窓の描画（黒ベゼル・切り欠きエリア）
    gap_px = train.window_gap * dot_size
    win_radius_px = train.window_radius * dot_size

    win_x1 = led_origin_x - gap_px
    win_y1 = led_origin_y - gap_px
    win_x2 = led_origin_x + led_w_px + gap_px
    win_y2 = led_origin_y + led_h_px + gap_px

    if win_radius_px > 0:
        draw.rounded_rectangle([win_x1, win_y1, win_x2, win_y2], radius=win_radius_px, fill="#000000")
    else:
        draw.rectangle([win_x1, win_y1, win_x2, win_y2], fill="#000000")

    # 4. 表示窓内にLED表示器画像を配置
    canvas.paste(led_image, (led_origin_x, led_origin_y))

    return canvas