import os
import tkinter as tk
from tkinter import messagebox
from config import init_directories, DATA_DIR
from views.mask_editor import MaskEditorWindow
from views.section_editor import SectionEditorWindow
from views.project_editor import ProjectEditorWindow
from views.player import PlayerWindow

class MainApp(tk.Tk):
    """メインウィンドウ"""
    def __init__(self):
        super().__init__()
        self.title("LED側面行先表示機 エミュレータ")
        self.geometry("400x350")

        init_directories()
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text="プロジェクト一覧", font=("Helvetica", 12, "bold")).pack(pady=(10, 2))

        # プロジェクトリスト表示
        self.lst_projects = tk.Listbox(self, height=6)
        self.lst_projects.pack(fill=tk.X, padx=20, pady=5)
        self.refresh_project_list()

        # 操作ボタン類
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_play = tk.Button(btn_frame, text="再生", command=self.play_project, width=12, bg="#88ccff")
        btn_play.grid(row=0, column=0, padx=5, pady=5)

        btn_sec_edit = tk.Button(btn_frame, text="セクション作成", command=self.open_sec_editor, width=12)
        btn_sec_edit.grid(row=0, column=1, padx=5, pady=5)

        btn_prj_edit = tk.Button(btn_frame, text="プロジェクト作成", command=self.open_prj_editor, width=12)
        btn_prj_edit.grid(row=1, column=0, padx=5, pady=5)

        btn_mask = tk.Button(btn_frame, text="LED形状設定", command=self.open_mask_editor, width=12)
        btn_mask.grid(row=1, column=1, padx=5, pady=5)

        btn_refresh = tk.Button(self, text="一覧更新", command=self.refresh_project_list)
        btn_refresh.pack(pady=5)

    def refresh_project_list(self):
        self.lst_projects.delete(0, tk.END)
        if os.path.exists(DATA_DIR):
            for f in os.listdir(DATA_DIR):
                if f.endswith(".prj"):
                    self.lst_projects.insert(tk.END, f)

    def play_project(self):
        sel = self.lst_projects.curselection()
        if not sel:
            messagebox.showwarning("注意", "プロジェクトを選択してください。")
            return
        filename = self.lst_projects.get(sel[0])
        PlayerWindow(self, filename)

    def open_sec_editor(self):
        SectionEditorWindow(self)

    def open_prj_editor(self):
        ProjectEditorWindow(self)

    def open_mask_editor(self):
        MaskEditorWindow(self)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()