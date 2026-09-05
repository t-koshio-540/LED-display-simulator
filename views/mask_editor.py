import tkinter as tk
from tkinter import messagebox
from config import load_led_matrix, save_led_matrix

class MaskEditorWindow(tk.Toplevel):
    """LEDドット形状および格子サイズ設定ウィンドウ"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("LEDドット形状・格子サイズ設定")
        self.matrix = load_led_matrix()
        self.buttons = []
        self.grid_frame = None
        self.init_ui()

    def init_ui(self):
        # 格子サイズ変更エリア
        top_frame = tk.Frame(self)
        top_frame.pack(padx=10, pady=10)

        tk.Label(top_frame, text="格子サイズ (N x N):").pack(side=tk.LEFT)
        self.spn_size = tk.Spinbox(top_frame, from_=2, to=30, width=5)
        current_size = len(self.matrix) if self.matrix else 10
        self.spn_size.delete(0, tk.END)
        self.spn_size.insert(0, str(current_size))
        self.spn_size.pack(side=tk.LEFT, padx=5)

        btn_change_size = tk.Button(top_frame, text="サイズ変更", command=self.change_grid_size)
        btn_change_size.pack(side=tk.LEFT, padx=5)

        # マトリクスボタンエリア
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(padx=10, pady=10)

        self.render_matrix_grid()

        save_btn = tk.Button(self, text="保存", command=self.save, bg="#aaffaa")
        save_btn.pack(pady=10)

    def render_matrix_grid(self):
        """現在の行列データに基づいてグリッドボタンを描画"""
        for row in self.buttons:
            for btn in row:
                btn.destroy()
        self.buttons = []

        size = len(self.matrix)
        for y in range(size):
            row_btns = []
            for x in range(size):
                val = self.matrix[y][x]
                color = "#ff9900" if val == 1 else "#333333"
                btn = tk.Button(self.grid_frame, width=2, height=1, bg=color,
                                command=lambda r=y, c=x: self.toggle_cell(r, c))
                btn.grid(row=y, column=x, padx=1, pady=1)
                row_btns.append(btn)
            self.buttons.append(row_btns)

    def change_grid_size(self):
        """入力された格子サイズで行列を再構成（既存パターンは可能な限り維持）"""
        try:
            new_size = int(self.spn_size.get())
            if new_size < 2 or new_size > 30:
                raise ValueError()
        except ValueError:
            messagebox.showerror("エラー", "格子サイズは2〜30の範囲で指定してください。")
            return

        old_size = len(self.matrix)
        new_matrix = [[0 for _ in range(new_size)] for _ in range(new_size)]
        
        for y in range(min(old_size, new_size)):
            for x in range(min(old_size, new_size)):
                new_matrix[y][x] = self.matrix[y][x]

        self.matrix = new_matrix
        self.render_matrix_grid()

    def toggle_cell(self, r, c):
        self.matrix[r][c] = 1 if self.matrix[r][c] == 0 else 0
        color = "#ff9900" if self.matrix[r][c] == 1 else "#333333"
        self.buttons[r][c].config(bg=color)

    def save(self):
        save_led_matrix(self.matrix)
        messagebox.showinfo("完了", "LEDドット形状と格子サイズを保存しました。")
        self.destroy()