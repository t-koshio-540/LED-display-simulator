import os
import tkinter as tk
from PIL import ImageTk
from models import Project, Section
from config import load_led_matrix
from utils import render_raw_page, apply_led_simulation

class PlayerWindow(tk.Toplevel):
    """LED表示シミュレーション再生ウィンドウ"""
    def __init__(self, parent, project_filename):
        super().__init__(parent)
        self.title("LED 側面行先表示機 シミュレータ")
        self.configure(bg="black")

        self.project = Project.load(project_filename)
        self.matrix = load_led_matrix()

        self.current_sec_idx = 0
        self.current_page_idx = 0
        self.repeat_counter = 0
        self.timer_id = None
        self.photo = None
        self.is_first_display = True  # ウィンドウサイズ自動調整を初回のみ限定にするフラグ

        # スクロール対応キャンバス
        self.container = tk.Frame(self, bg="black")
        self.container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.container, bg="black", highlightthickness=0)
        self.h_bar = tk.Scrollbar(self.container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_bar = tk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=self.h_bar.set, yscrollcommand=self.v_bar.set)

        self.h_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # キーバインドの設定
        self.bind("<Left>", lambda e: self.navigate_section(-1))
        self.bind("<Right>", lambda e: self.navigate_section(1))
        self.bind("<space>", lambda e: self.on_space_pressed())

        self.focus_set()
        self.load_current_section()

    def load_current_section(self):
        """セクション切り替え時の初期化"""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        if not self.project.section_files:
            return

        sec_filename = self.project.section_files[self.current_sec_idx]
        self.current_sec = Section.load(sec_filename)
        self.current_page_idx = 0
        self.repeat_counter = 0

        self.show_current_page()

    def show_current_page(self):
        """現在のページの描画とタイマー設定"""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        if not self.current_sec.pages:
            return

        current_page = self.current_sec.pages[self.current_page_idx]

        # 原寸合成画像の生成
        raw_img = render_raw_page(self.current_sec.prefix, current_page.items)
        # LED変換（格子サイズ拡大＋ドットマスク適用）
        led_img = apply_led_simulation(raw_img, self.matrix)

        self.photo = ImageTk.PhotoImage(led_img)

        # 描画更新
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.config(scrollregion=(0, 0, led_img.width, led_img.height))

        # 初回起動時のみウィンドウサイズを自動設定（ユーザー手動変更後は保持）
        if self.is_first_display:
            self.update_idletasks()
            win_w = min(led_img.width + 20, self.winfo_screenwidth() - 80)
            win_h = min(led_img.height + 20, self.winfo_screenheight() - 80)
            self.geometry(f"{win_w}x{win_h}")
            self.is_first_display = False

        # ページの持続時間(ms)経過後に次の処理を実行
        self.timer_id = self.after(current_page.duration, self.on_page_timeout)

    def on_page_timeout(self):
        """ページの持続時間が経過したときの処理"""
        num_pages = len(self.current_sec.pages)
        self.current_page_idx += 1

        if self.current_page_idx < num_pages:
            self.show_current_page()
        else:
            self.current_page_idx = 0
            
            if self.current_sec.condition_type == "REPEAT":
                self.repeat_counter += 1
                if self.repeat_counter >= self.current_sec.condition_val:
                    self.navigate_section(1)
                else:
                    self.show_current_page()
            elif self.current_sec.condition_type == "SPACE":
                self.show_current_page()

    def on_space_pressed(self):
        """スペースキー入力時"""
        if self.current_sec.condition_type == "SPACE":
            self.navigate_section(1)

    def navigate_section(self, step):
        """左右キーによる前後強制切替、または進行"""
        if not self.project.section_files:
            return
        num_sections = len(self.project.section_files)
        self.current_sec_idx = (self.current_sec_idx + step) % num_sections
        self.load_current_section()