import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk
from models import Section, Page
from utils import render_raw_page

class SectionEditorWindow(tk.Toplevel):
    """ページ・セクション作成・編集ウィンドウ"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("セクション作成 / 編集")
        self.geometry("850x600")

        self.section = Section()
        self.current_page_items = []  # 現在編集中のページの画像要素リスト
        self.preview_photo = None
        
        self.init_ui()

    def init_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- 上部: セクション全体設定 ---
        sec_frame = tk.LabelFrame(main_frame, text="セクション設定", padx=10, pady=5)
        sec_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sec_frame, text="接頭辞 (10桁):").grid(row=0, column=0, sticky="w")
        self.ent_prefix = tk.Entry(sec_frame, width=12)
        self.ent_prefix.insert(0, "AAABBBBBBB")
        self.ent_prefix.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(sec_frame, text="セクションID (8桁):").grid(row=0, column=2, sticky="w")
        self.ent_sec_id = tk.Entry(sec_frame, width=10)
        self.ent_sec_id.insert(0, "00000001")
        self.ent_sec_id.grid(row=0, column=3, sticky="w", padx=5)

        tk.Label(sec_frame, text="遷移条件:").grid(row=0, column=4, sticky="w")
        self.cmb_cond = ttk.Combobox(sec_frame, values=["REPEAT", "SPACE"], state="readonly", width=8)
        self.cmb_cond.set("REPEAT")
        self.cmb_cond.grid(row=0, column=5, sticky="w", padx=5)

        tk.Label(sec_frame, text="繰返回数:").grid(row=0, column=6, sticky="w")
        self.ent_cond_val = tk.Entry(sec_frame, width=5)
        self.ent_cond_val.insert(0, "1")
        self.ent_cond_val.grid(row=0, column=7, sticky="w", padx=5)

        # --- 中部レイアウト ---
        mid_frame = tk.Frame(main_frame)
        mid_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(mid_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 1. 登録済みページ一覧
        pages_box = tk.LabelFrame(left_frame, text="登録ページ一覧", padx=5, pady=5)
        pages_box.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.lst_pages = tk.Listbox(pages_box, height=4)
        self.lst_pages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.lst_pages.bind("<<ListboxSelect>>", self.on_select_page)

        btn_page_box = tk.Frame(pages_box)
        btn_page_box.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        tk.Button(btn_page_box, text="新規ページ追加", command=self.add_page, width=12).pack(pady=2)
        tk.Button(btn_page_box, text="選択ページ更新", command=self.update_page, width=12).pack(pady=2)
        tk.Button(btn_page_box, text="選択ページ削除", command=self.delete_page, width=12).pack(pady=2)

        # 2. ページ詳細編集
        page_edit_box = tk.LabelFrame(left_frame, text="ページの編集", padx=5, pady=5)
        page_edit_box.pack(fill=tk.BOTH, expand=True)

        dur_frame = tk.Frame(page_edit_box)
        dur_frame.pack(fill=tk.X, pady=2)
        tk.Label(dur_frame, text="持続時間 (ms):").pack(side=tk.LEFT)
        self.ent_duration = tk.Entry(dur_frame, width=8)
        self.ent_duration.insert(0, "1000")
        self.ent_duration.pack(side=tk.LEFT, padx=5)

        tk.Label(page_edit_box, text="配置画像リスト:").pack(anchor="w", pady=(5, 0))
        img_list_frame = tk.Frame(page_edit_box)
        img_list_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        self.lst_items = tk.Listbox(img_list_frame, height=5)
        self.lst_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_img_box = tk.Frame(img_list_frame)
        btn_img_box.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        tk.Button(btn_img_box, text="画像取り消し", command=self.remove_image_item, width=12, bg="#ffcccc").pack(pady=2)

        # 画像追加入力フォーム
        add_img_frame = tk.Frame(page_edit_box)
        add_img_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(add_img_frame, text="コード(4桁):").pack(side=tk.LEFT)
        self.ent_code = tk.Entry(add_img_frame, width=6)
        self.ent_code.insert(0, "0001")
        self.ent_code.pack(side=tk.LEFT, padx=2)

        tk.Label(add_img_frame, text="X:").pack(side=tk.LEFT)
        self.ent_x = tk.Entry(add_img_frame, width=4)
        self.ent_x.insert(0, "0")
        self.ent_x.pack(side=tk.LEFT, padx=2)

        tk.Label(add_img_frame, text="Y:").pack(side=tk.LEFT)
        self.ent_y = tk.Entry(add_img_frame, width=4)
        self.ent_y.insert(0, "0")
        self.ent_y.pack(side=tk.LEFT, padx=2)

        tk.Button(add_img_frame, text="画像追加", command=self.add_image_item).pack(side=tk.LEFT, padx=5)

        # --- 右側: プレビューエリア ---
        right_frame = tk.LabelFrame(mid_frame, text="プレビュー (等倍・LED加工なし)", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.lbl_preview = tk.Label(right_frame, bg="black")
        self.lbl_preview.pack(expand=True)

        # --- 下部: 保存ボタン ---
        btn_save = tk.Button(main_frame, text="セクション全体を保存", command=self.save_section, bg="#aaffaa", font=("", 11, "bold"))
        btn_save.pack(fill=tk.X, pady=(10, 0))

        self.update_preview()

    # 画像要素操作
    def add_image_item(self):
        code = self.ent_code.get()
        try:
            x = int(self.ent_x.get())
            y = int(self.ent_y.get())
        except ValueError:
            messagebox.showerror("エラー", "座標には整数を入力してください。")
            return

        self.current_page_items.append({"code": code, "x": x, "y": y})
        self.refresh_item_listbox()
        self.update_preview()

    def remove_image_item(self):
        """追加した画像を取り消す（選択要素の削除）"""
        sel = self.lst_items.curselection()
        if sel:
            idx = sel[0]
            del self.current_page_items[idx]
            self.refresh_item_listbox()
            self.update_preview()

    def refresh_item_listbox(self):
        self.lst_items.delete(0, tk.END)
        for item in self.current_page_items:
            self.lst_items.insert(tk.END, f"Code:{item['code']} (X:{item['x']}, Y:{item['y']})")

    # ページ操作
    def add_page(self):
        try:
            dur = int(self.ent_duration.get())
        except ValueError:
            messagebox.showerror("エラー", "持続時間には整数(ms)を入力してください。")
            return

        page = Page(duration=dur, items=list(self.current_page_items))
        self.section.pages.append(page)
        self.refresh_page_listbox()
        self.lst_pages.select_set(len(self.section.pages) - 1)

    def update_page(self):
        sel = self.lst_pages.curselection()
        if not sel:
            messagebox.showwarning("注意", "更新するページを一覧から選択してください。")
            return
        try:
            dur = int(self.ent_duration.get())
        except ValueError:
            messagebox.showerror("エラー", "持続時間には整数(ms)を入力してください。")
            return

        idx = sel[0]
        self.section.pages[idx] = Page(duration=dur, items=list(self.current_page_items))
        self.refresh_page_listbox()

    def delete_page(self):
        sel = self.lst_pages.curselection()
        if sel:
            idx = sel[0]
            del self.section.pages[idx]
            self.refresh_page_listbox()
            self.current_page_items = []
            self.refresh_item_listbox()
            self.update_preview()

    def on_select_page(self, event):
        sel = self.lst_pages.curselection()
        if sel:
            idx = sel[0]
            page = self.section.pages[idx]
            self.ent_duration.delete(0, tk.END)
            self.ent_duration.insert(0, str(page.duration))
            self.current_page_items = list(page.items)
            self.refresh_item_listbox()
            self.update_preview()

    def refresh_page_listbox(self):
        self.lst_pages.delete(0, tk.END)
        for i, page in enumerate(self.section.pages):
            self.lst_pages.insert(tk.END, f"ページ {i+1} [{page.duration}ms, 画像{len(page.items)}件]")

    def update_preview(self):
        prefix = self.ent_prefix.get()
        img = render_raw_page(prefix, self.current_page_items)
        self.preview_photo = ImageTk.PhotoImage(img)
        self.lbl_preview.config(image=self.preview_photo)

    def save_section(self):
        self.section.prefix = self.ent_prefix.get()
        self.section.section_id = self.ent_sec_id.get()
        try:
            self.section.condition_val = int(self.ent_cond_val.get())
        except ValueError:
            messagebox.showerror("エラー", "繰返回数には整数を入力してください。")
            return
        self.section.condition_type = self.cmb_cond.get()

        if not self.section.pages:
            messagebox.showerror("エラー", "ページが1つも作成されていません。")
            return

        self.section.save()
        messagebox.showinfo("完了", f"{self.section.filename} を保存しました。")
        self.destroy()