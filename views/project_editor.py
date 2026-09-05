import os
import tkinter as tk
from tkinter import messagebox
from config import SECTIONS_DIR
from models import Project, Section
from utils import render_raw_page
from PIL import ImageTk

class ProjectEditorWindow(tk.Toplevel):
    """プロジェクト作成・編集ウィンドウ"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("プロジェクト作成 / 編集")
        self.geometry("600x450")

        self.project = Project()
        self.preview_photo = None
        self.init_ui()

    def init_ui(self):
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top_frame, text="接頭辞 (10桁):").grid(row=0, column=0, sticky="w")
        self.ent_prefix = tk.Entry(top_frame, width=15)
        self.ent_prefix.insert(0, "AAABBBBBBB")
        self.ent_prefix.grid(row=0, column=1, sticky="w")

        tk.Label(top_frame, text="識別名 (任意文字列):").grid(row=1, column=0, sticky="w")
        self.ent_name = tk.Entry(top_frame, width=20)
        self.ent_name.insert(0, "各駅停車")
        self.ent_name.grid(row=1, column=1, sticky="w")

        mid_frame = tk.Frame(self)
        mid_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # 利用可能なセクション一覧
        left_box = tk.Frame(mid_frame)
        left_box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Label(left_box, text="利用可能なセクション:").pack(anchor="w")
        self.lst_avail = tk.Listbox(left_box)
        self.lst_avail.pack(expand=True, fill=tk.BOTH)
        self.refresh_available_sections()

        # 追加・削除ボタン
        btn_box = tk.Frame(mid_frame)
        btn_box.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="追加 ->", command=self.add_section).pack(pady=5)
        tk.Button(btn_box, text="<- 削除", command=self.remove_section).pack(pady=5)

        # 登録済みセクション
        right_box = tk.Frame(mid_frame)
        right_box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Label(right_box, text="登録されたセクション:").pack(anchor="w")
        self.lst_proj = tk.Listbox(right_box)
        self.lst_proj.pack(expand=True, fill=tk.BOTH)
        self.lst_proj.bind("<<ListboxSelect>>", self.on_select_section)

        # プレビュー表示エリア
        prev_frame = tk.Frame(self, bg="#222222", height=80)
        prev_frame.pack(fill=tk.X, padx=10, pady=5)
        self.lbl_preview = tk.Label(prev_frame, bg="black")
        self.lbl_preview.pack(pady=5)

        btn_save = tk.Button(self, text="プロジェクト保存", command=self.save_project, bg="#aaffaa")
        btn_save.pack(pady=10)

    def refresh_available_sections(self):
        self.lst_avail.delete(0, tk.END)
        if os.path.exists(SECTIONS_DIR):
            for f in os.listdir(SECTIONS_DIR):
                if f.endswith(".sec"):
                    self.lst_avail.insert(tk.END, f)

    def add_section(self):
        sel = self.lst_avail.curselection()
        if sel:
            sec_file = self.lst_avail.get(sel[0])
            self.project.section_files.append(sec_file)
            self.lst_proj.insert(tk.END, sec_file)

    def remove_section(self):
        sel = self.lst_proj.curselection()
        if sel:
            idx = sel[0]
            del self.project.section_files[idx]
            self.lst_proj.delete(idx)

    def on_select_section(self, event):
        sel = self.lst_proj.curselection()
        if sel:
            sec_file = self.lst_proj.get(sel[0])
            try:
                sec = Section.load(sec_file)
                items = sec.pages[0].items if sec.pages else []
                img = render_raw_page(sec.prefix, items)
                self.preview_photo = ImageTk.PhotoImage(img)
                self.lbl_preview.config(image=self.preview_photo)
            except Exception:
                pass

    def save_project(self):
        self.project.prefix = self.ent_prefix.get()
        self.project.name = self.ent_name.get()
        if not self.project.section_files:
            messagebox.showerror("エラー", "セクションが選択されていません。")
            return
        self.project.save()
        messagebox.showinfo("完了", f"{self.project.filename} を保存しました。")
        self.destroy()