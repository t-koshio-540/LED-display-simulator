import os
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from config import load_led_matrix, IMAGE_DIR
from utils import render_bmp_direct, apply_led_simulation

class QuickPlayerWindow(tk.Toplevel):
    """簡易再生機能ウィンドウ（プロジェクト保存なし）"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("簡易再生機能")
        self.configure(bg="black")

        self.file_paths = []
        self.current_idx = 0
        self.matrix = load_led_matrix()
        self.photo = None
        self.is_first_display = True

        self.init_ui()

    def init_ui(self):
        # コントロールバー
        ctrl_frame = tk.Frame(self, bg="#222222")
        ctrl_frame.pack(fill=tk.X, side=tk.TOP)

        btn_select = tk.Button(ctrl_frame, text="BMPファイルを選択/検索", command=self.select_files)
        btn_select.pack(side=tk.LEFT, padx=10, pady=5)

        self.lbl_info = tk.Label(ctrl_frame, text="ファイルが選択されていません", fg="white", bg="#222222")
        self.lbl_info.pack(side=tk.LEFT, padx=10)

        # 表示エリア
        self.container = tk.Frame(self, bg="black")
        self.container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.container, bg="black", highlightthickness=0)
        self.h_bar = tk.Scrollbar(self.container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_bar = tk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=self.h_bar.set, yscrollcommand=self.v_bar.set)

        self.h_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # キーバインド
        self.bind("<Left>", lambda e: self.navigate(-1))
        self.bind("<Right>", lambda e: self.navigate(1))
        self.focus_set()

    def select_files(self):
        initial_dir = IMAGE_DIR if os.path.exists(IMAGE_DIR) else os.getcwd()
        selected = filedialog.askopenfilenames(
            title="BMPファイルを選択 (複数選択可能)",
            initialdir=initial_dir,
            filetypes=[("BMP Files", "*.bmp"), ("All Files", "*.*")]
        )
        if selected:
            self.file_paths = list(selected)
            self.current_idx = 0
            self.show_current_image()

    def show_current_image(self):
        if not self.file_paths:
            return

        filepath = self.file_paths[self.current_idx]
        filename = os.path.basename(filepath)
        self.lbl_info.config(text=f"[{self.current_idx + 1}/{len(self.file_paths)}] {filename}")

        raw_img = render_bmp_direct(filepath)
        led_img = apply_led_simulation(raw_img, self.matrix)

        self.photo = ImageTk.PhotoImage(led_img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=(0, 0, led_img.width, led_img.height))

        if self.is_first_display:
            self.update_idletasks()
            win_w = min(led_img.width + 40, self.winfo_screenwidth() - 80)
            win_h = min(led_img.height + 80, self.winfo_screenheight() - 80)
            self.geometry(f"{win_w}x{win_h}")
            self.is_first_display = False

    def navigate(self, step):
        if not self.file_paths:
            return
        num_files = len(self.file_paths)
        self.current_idx = (self.current_idx + step) % num_files
        self.show_current_image()