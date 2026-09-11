import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk

from models.train import Train, TrainBand
from models import Section
from utils import render_raw_page
from utils.render_train import render_train_frame

class TrainEditorWindow(tk.Toplevel):
    """車両ファイル (.tra) 編集ウィンドウ"""
    def __init__(self, parent, prefix="AAABBBBBBB", dot_size=10):
        super().__init__(parent)
        self.title("車両ファイル設定")
        self.geometry("1000x700")

        self.dot_size = dot_size
        self.train = Train.load(prefix)
        
        # プレビュー用画像データ
        self.preview_led_image = None
        self.preview_photo = None
        
        self.init_ui()
        self.reload_bands_list()
        self.update_preview()

    def init_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame, width=420)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = tk.LabelFrame(main_frame, text="プレビュー", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- 基本設定 ---
        base_box = tk.LabelFrame(left_frame, text="基本設定", padx=10, pady=5)
        base_box.pack(fill=tk.X, pady=(0, 5))

        tk.Label(base_box, text="接頭辞:").grid(row=0, column=0, sticky="w")
        self.ent_prefix = tk.Entry(base_box, width=15)
        self.ent_prefix.insert(0, self.train.prefix)
        self.ent_prefix.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(base_box, text="車体色:").grid(row=1, column=0, sticky="w")
        color_frame = tk.Frame(base_box)
        color_frame.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        self.lbl_color_sample = tk.Label(color_frame, width=6, bg=self.train.body_color, relief="solid", bd=1)
        self.lbl_color_sample.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(color_frame, text="色選択", command=self.choose_body_color).pack(side=tk.LEFT)

        # --- 表示窓設定 ---
        win_box = tk.LabelFrame(left_frame, text="表示窓設定", padx=10, pady=5)
        win_box.pack(fill=tk.X, pady=5)

        tk.Label(win_box, text="隙間幅 (ドット):").grid(row=0, column=0, sticky="w")
        self.ent_gap = tk.Entry(win_box, width=8)
        self.ent_gap.insert(0, str(self.train.window_gap))
        self.ent_gap.grid(row=0, column=1, sticky="w", padx=5)
        self.ent_gap.bind("<KeyRelease>", lambda e: self.on_config_changed())

        tk.Label(win_box, text="角丸半径 (ドット):").grid(row=1, column=0, sticky="w")
        self.ent_radius = tk.Entry(win_box, width=8)
        self.ent_radius.insert(0, str(self.train.window_radius))
        self.ent_radius.grid(row=1, column=1, sticky="w", padx=5)
        self.ent_radius.bind("<KeyRelease>", lambda e: self.on_config_changed())

        # --- 車体帯（追加長方形）一覧・編集 ---
        band_box = tk.LabelFrame(left_frame, text="車体帯（追加長方形）", padx=10, pady=5)
        band_box.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lst_bands = tk.Listbox(band_box, height=6)
        self.lst_bands.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # 帯追加/編集パラメータ入力フォーム
        input_f = tk.Frame(band_box)
        input_f.pack(fill=tk.X)

        tk.Label(input_f, text="X:").grid(row=0, column=0)
        self.ent_bx = tk.Entry(input_f, width=5)
        self.ent_bx.insert(0, "0")
        self.ent_bx.grid(row=0, column=1)

        tk.Label(input_f, text="Y:").grid(row=0, column=2)
        self.ent_by = tk.Entry(input_f, width=5)
        self.ent_by.insert(0, "-10")
        self.ent_by.grid(row=0, column=3)

        tk.Label(input_f, text="W:").grid(row=0, column=4)
        self.ent_bw = tk.Entry(input_f, width=5)
        self.ent_bw.insert(0, "128")
        self.ent_bw.grid(row=0, column=5)

        tk.Label(input_f, text="H:").grid(row=1, column=0)
        self.ent_bh = tk.Entry(input_f, width=5)
        self.ent_bh.insert(0, "6")
        self.ent_bh.grid(row=1, column=1)

        tk.Label(input_f, text="R:").grid(row=1, column=2)
        self.ent_br = tk.Entry(input_f, width=5)
        self.ent_br.insert(0, "0")
        self.ent_br.grid(row=1, column=3)

        self.band_color = "#0000FF"
        self.lbl_band_color = tk.Label(input_f, width=4, bg=self.band_color, relief="solid", bd=1)
        self.lbl_band_color.grid(row=1, column=4)
        tk.Button(input_f, text="色", command=self.choose_band_color).grid(row=1, column=5)

        btn_band_f = tk.Frame(band_box)
        btn_band_f.pack(fill=tk.X, pady=5)
        tk.Button(btn_band_f, text="帯の追加", command=self.add_band).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_band_f, text="選択項目削除", command=self.delete_band, bg="#ffcccc").pack(side=tk.LEFT, padx=2)

        # --- 保存ボタン ---
        tk.Button(left_frame, text="車両設定を保存", command=self.save_train, bg="#aaffaa", font=("", 11, "bold")).pack(fill=tk.X, pady=5)

        # --- 右側: プレビュー表示設定 ---
        pv_ctrl = tk.Frame(right_frame)
        pv_ctrl.pack(fill=tk.X, pady=(0, 5))

        tk.Label(pv_ctrl, text="表示器用サンプル:").pack(side=tk.LEFT)
        self.pv_mode = tk.StringVar(value="default")
        tk.Radiobutton(pv_ctrl, text="デフォルト(黒)", variable=self.pv_mode, value="default", command=self.update_preview).pack(side=tk.LEFT)
        tk.Radiobutton(pv_ctrl, text=".bmp画像", variable=self.pv_mode, value="bmp", command=self.select_bmp_preview).pack(side=tk.LEFT)
        tk.Radiobutton(pv_ctrl, text=".secファイル", variable=self.pv_mode, value="sec", command=self.select_sec_preview).pack(side=tk.LEFT)

        self.lbl_preview = tk.Label(right_frame, bg="#222222")
        self.lbl_preview.pack(expand=True, fill=tk.BOTH)

    def choose_body_color(self):
        c = colorchooser.askcolor(color=self.train.body_color)
        if c[1]:
            self.train.body_color = c[1]
            self.lbl_color_sample.config(bg=c[1])
            self.update_preview()

    def choose_band_color(self):
        c = colorchooser.askcolor(color=self.band_color)
        if c[1]:
            self.band_color = c[1]
            self.lbl_band_color.config(bg=c[1])

    def add_band(self):
        try:
            x = int(self.ent_bx.get())
            y = int(self.ent_by.get())
            w = int(self.ent_bw.get())
            h = int(self.ent_bh.get())
            r = int(self.ent_br.get())
        except ValueError:
            messagebox.showerror("エラー", "帯設定の数値入力項目を確認してください。")
            return

        band = TrainBand(x=x, y=y, width=w, height=h, radius=r, color=self.band_color)
        self.train.bands.append(band)
        self.reload_bands_list()
        self.update_preview()

    def delete_band(self):
        sel = self.lst_bands.curselection()
        if sel:
            idx = sel[0]
            del self.train.bands[idx]
            self.reload_bands_list()
            self.update_preview()

    def reload_bands_list(self):
        self.lst_bands.delete(0, tk.END)
        for i, b in enumerate(self.train.bands):
            self.lst_bands.insert(tk.END, f"帯{i+1}: POS({b.x},{b.y}) SIZE({b.width}x{b.height}) R:{b.radius} COLOR:{b.color}")

    def on_config_changed(self):
        try:
            self.train.window_gap = int(self.ent_gap.get())
            self.train.window_radius = int(self.ent_radius.get())
            self.update_preview()
        except ValueError:
            pass

    def select_bmp_preview(self):
        path = filedialog.askopenfilename(filetypes=[("Bitmap", "*.bmp")])
        if path:
            img = Image.open(path)
            # 格子倍率に合わせてリサイズ
            self.preview_led_image = img.resize((img.width * self.dot_size, img.height * self.dot_size), Image.NEAREST)
            self.update_preview()
        else:
            self.pv_mode.set("default")

    def select_sec_preview(self):
        path = filedialog.askopenfilename(filetypes=[("Section File", "*.sec")])
        if path:
            sec = Section.load(path)
            if sec.pages:
                raw_img = render_raw_page(sec.prefix, sec.pages[0].items)
                self.preview_led_image = raw_img.resize((raw_img.width * self.dot_size, raw_img.height * self.dot_size), Image.NEAREST)
            self.update_preview()
        else:
            self.pv_mode.set("default")

    def update_preview(self):
        mode = self.pv_mode.get()
        if mode == "default" or self.preview_led_image is None:
            # デフォルトは128x32ドットの黒画面
            w_px, h_px = 128 * self.dot_size, 32 * self.dot_size
            led_img = Image.new("RGB", (w_px, h_px), "#000000")
        else:
            led_img = self.preview_led_image

        full_img = render_train_frame(led_img, self.train, dot_size=self.dot_size)
        self.preview_photo = ImageTk.PhotoImage(full_img)
        self.lbl_preview.config(image=self.preview_photo)

    def save_train(self):
        self.train.prefix = self.ent_prefix.get().strip()
        try:
            self.train.window_gap = int(self.ent_gap.get())
            self.train.window_radius = int(self.ent_radius.get())
        except ValueError:
            messagebox.showerror("エラー", "数値項目を確認してください。")
            return

        self.train.save()
        messagebox.showinfo("完了", f"車両設定 {self.train.filename if hasattr(self.train, 'filename') else self.train.prefix + '.tra'} を保存しました。")
        self.destroy()