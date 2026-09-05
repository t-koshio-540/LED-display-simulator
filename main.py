import os
import tkinter as tk
from tkinter import messagebox
from config import init_directories, DATA_DIR
from views.mask_editor import MaskEditorWindow
from views.section_editor import SectionEditorWindow
from views.project_editor import ProjectEditorWindow
from views.player import PlayerWindow
from views.quick_player import QuickPlayerWindow

class MainApp(tk.Tk):
    """メインウィンドウ"""
    def __init__(self):
        super().__init__()
        self.title("LED側面行先表示機 エミュレータ")
        self.geometry("480x480")

        init_directories()
        self.init_ui()

    def init_ui(self):
        tk.Label(self, text="プロジェクト一覧・管理", font=("Helvetica", 12, "bold")).pack(pady=(10, 2))

        # 検索エリア
        search_frame = tk.LabelFrame(self, text="プロジェクト検索", padx=5, pady=5)
        search_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(search_frame, text="接頭辞 (10桁):").grid(row=0, column=0, sticky="w")
        self.ent_search_prefix = tk.Entry(search_frame, width=12)
        self.ent_search_prefix.grid(row=0, column=1, padx=5, sticky="w")
        self.ent_search_prefix.bind("<KeyRelease>", lambda e: self.refresh_project_list())

        tk.Label(search_frame, text="識別名/キーワード:").grid(row=1, column=0, sticky="w")
        self.ent_search_keyword = tk.Entry(search_frame, width=15)
        self.ent_search_keyword.grid(row=1, column=1, padx=5, sticky="w")
        self.ent_search_keyword.bind("<KeyRelease>", lambda e: self.refresh_project_list())

        # プロジェクトリスト表示
        self.lst_projects = tk.Listbox(self, height=6)
        self.lst_projects.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.refresh_project_list()

        # 操作ボタン群
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_play = tk.Button(btn_frame, text="再生", command=self.play_project, width=13, bg="#88ccff")
        btn_play.grid(row=0, column=0, padx=5, pady=5)

        btn_quick_play = tk.Button(btn_frame, text="簡易再生", command=self.open_quick_player, width=13, bg="#ffaa88")
        btn_quick_play.grid(row=0, column=1, padx=5, pady=5)

        btn_sec_edit = tk.Button(btn_frame, text="セクション作成", command=self.open_sec_editor, width=13)
        btn_sec_edit.grid(row=1, column=0, padx=5, pady=5)

        btn_prj_edit = tk.Button(btn_frame, text="プロジェクト作成", command=self.open_prj_editor, width=13)
        btn_prj_edit.grid(row=1, column=1, padx=5, pady=5)

        btn_mask = tk.Button(btn_frame, text="LED形状設定", command=self.open_mask_editor, width=13)
        btn_mask.grid(row=2, column=0, padx=5, pady=5)

        btn_refresh = tk.Button(btn_frame, text="一覧更新", command=self.refresh_project_list, width=13)
        btn_refresh.grid(row=2, column=1, padx=5, pady=5)

    def refresh_project_list(self):
        self.lst_projects.delete(0, tk.END)
        prefix_query = self.ent_search_prefix.get().strip().lower()
        keyword_query = self.ent_search_keyword.get().strip().lower()

        if os.path.exists(DATA_DIR):
            for f in os.listdir(DATA_DIR):
                if f.endswith(".prj"):
                    name_body = f[:-4]
                    prefix_part = name_body[:10] if len(name_body) >= 10 else name_body
                    rest_part = name_body[10:] if len(name_body) >= 10 else ""

                    match_prefix = (not prefix_query) or (prefix_query in prefix_part.lower())
                    match_keyword = (not keyword_query) or (keyword_query in rest_part.lower())

                    if match_prefix and match_keyword:
                        self.lst_projects.insert(tk.END, f)

    def play_project(self):
        sel = self.lst_projects.curselection()
        if not sel:
            messagebox.showwarning("注意", "プロジェクトを選択してください。")
            return
        filename = self.lst_projects.get(sel[0])
        PlayerWindow(self, filename)

    def open_quick_player(self):
        QuickPlayerWindow(self)

    def open_sec_editor(self):
        SectionEditorWindow(self)

    def open_prj_editor(self):
        ProjectEditorWindow(self)

    def open_mask_editor(self):
        MaskEditorWindow(self)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()