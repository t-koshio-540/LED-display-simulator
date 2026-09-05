import os
import glob
from PIL import Image

# ==================== 設定項目 ====================
INPUT_FOLDER = r"C:\Users\t-kos\OneDrive\ドキュメント\鉄道\側面方向幕再現\電子幕シミュレーター\image\作業用\1ここから切り出し"    # 元のBMPファイルが入っているフォルダ
OUTPUT_FOLDER = r"C:\Users\t-kos\OneDrive\ドキュメント\鉄道\側面方向幕再現\電子幕シミュレーター\image\作業用\2ここに出力"  # 切り抜いた画像を保存するフォルダ
PREFIX = "種別変更_"                             # ファイル名の頭に付ける文字（例: img_1.bmp）

# 切り抜く矩形範囲（ピクセル単位で指定）
CROP_X = 0        # 切り抜きたい範囲の「左端」のX座標
CROP_Y = 18        # 切り抜きたい範囲の「上端」のY座標
CROP_WIDTH = 128   # 切り抜く「横幅」
CROP_HEIGHT = 14  # 切り抜く「縦幅」
# ==================================================

def crop_batch_process():
    # 保存先フォルダが存在しない場合は自動で作成
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"保存先フォルダを作成しました: {OUTPUT_FOLDER}")

    # 指定されたフォルダ内のすべての .bmp ファイルを取得
    bmp_files = glob.glob(os.path.join(INPUT_FOLDER, "*.bmp"))
    
    if not bmp_files:
        print(f"指定された入力フォルダにBMPファイルが見つかりませんでした: {INPUT_FOLDER}")
        return

    print(f"{len(bmp_files)} 個のファイルを切り抜き処理します...")

    # 切り抜き範囲の計算 (Pillowは 左, 上, 右, 下 の4点を指定する仕様です)
    crop_box = (CROP_X, CROP_Y, CROP_X + CROP_WIDTH, CROP_Y + CROP_HEIGHT)

    # 1から始まる連番でループ処理
    for index, bmp_path in enumerate(bmp_files, start=1):
        try:
            # 1. BMPファイルを開く
            img = Image.open(bmp_path)
            
            # 画像のサイズが切り抜き範囲より小さい場合のエラー防止
            if img.width < (CROP_X + CROP_WIDTH) or img.height < (CROP_Y + CROP_HEIGHT):
                print(f"警告: {os.path.basename(bmp_path)} は指定された切り抜き範囲よりサイズ({img.width} x {img.height})が小さいため、スキップします。")
                continue

            # 2. 予め指定した範囲の矩形部分を抜き出す
            cropped_img = img.crop(crop_box)
            
            # 3 & 4. 接頭辞 + 連番のファイル名を作成
            filename = f"{PREFIX}{index}.bmp"
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            
            # 指定したフォルダ内にbmpで保存
            cropped_img.save(output_path)
            print(f"保存完了: {filename} (元ファイル: {os.path.basename(bmp_path)})")
            
        except Exception as e:
            print(f"エラー発生 ({os.path.basename(bmp_path)}): {e}")

    print("すべての切り抜き処理が完了しました！")

if __name__ == "__main__":
    crop_batch_process()