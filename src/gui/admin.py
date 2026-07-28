import shutil
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.config import KNOWLEDGE_DIR, SUPPORTED_EXTENSIONS
from src.gui.styles import COLORS, FONT_BODY, FONT_SMALL, FONT_SUBTITLE, FONT_TITLE
from src.knowledge.store import KnowledgeStore


class AdminFrame(ctk.CTkFrame):
    def __init__(self, master, store: KnowledgeStore, on_back) -> None:
        super().__init__(master, fg_color=COLORS["bg"])
        self.store = store
        self.on_back = on_back
        self._build()
        self.refresh_list()

    def _build(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 12))

        ctk.CTkButton(header, text="返回", width=72, command=self.on_back).pack(side="left")
        ctk.CTkLabel(header, text="管理入口", font=FONT_TITLE, text_color=COLORS["text"]).pack(side="left", padx=16)

        body = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(top, text="资料管理", font=FONT_SUBTITLE, text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(top, text="上传资料", command=self.upload_files).pack(side="right", padx=(8, 0))
        ctk.CTkButton(top, text="重建索引", command=self.rebuild_index).pack(side="right")

        self.status_label = ctk.CTkLabel(body, text="", font=FONT_SMALL, text_color=COLORS["muted"])
        self.status_label.pack(anchor="w", padx=20, pady=(0, 8))

        self.list_frame = ctk.CTkScrollableFrame(body, fg_color="#f9fafb", corner_radius=12)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        hint = ctk.CTkLabel(
            body,
            text="支持 .txt / .md / .pdf，上传后点击“重建索引”即可供对话使用。",
            font=FONT_SMALL,
            text_color=COLORS["muted"],
        )
        hint.pack(anchor="w", padx=20, pady=(0, 16))

    def refresh_list(self) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()

        sources = self.store.list_sources()
        if not sources:
            ctk.CTkLabel(
                self.list_frame,
                text="暂无资料，请先上传文件。",
                font=FONT_BODY,
                text_color=COLORS["muted"],
            ).pack(pady=24)
            return

        for item in sources:
            row = ctk.CTkFrame(self.list_frame, fg_color=COLORS["card"], corner_radius=10)
            row.pack(fill="x", padx=8, pady=6)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=12, pady=12)
            ctk.CTkLabel(info, text=item["name"], font=FONT_BODY, anchor="w").pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=f"{item['size_kb']} KB · {item['chunks']} 片段",
                font=FONT_SMALL,
                text_color=COLORS["muted"],
            ).pack(anchor="w")

            ctk.CTkButton(
                row,
                text="删除",
                width=72,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda name=item["name"]: self.delete_source(name),
            ).pack(side="right", padx=12, pady=12)

    def upload_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="选择资料文件",
            filetypes=[
                ("Supported", "*.txt *.md *.pdf"),
                ("Text", "*.txt"),
                ("Markdown", "*.md"),
                ("PDF", "*.pdf"),
            ],
        )
        if not paths:
            return

        copied = 0
        for path in paths:
            src = Path(path)
            if src.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            dest = KNOWLEDGE_DIR / src.name
            shutil.copy2(src, dest)
            copied += 1

        self.status_label.configure(text=f"已上传 {copied} 个文件")
        self.refresh_list()

    def rebuild_index(self) -> None:
        self.status_label.configure(text="正在重建索引...")
        self.update_idletasks()

        def task() -> None:
            count = self.store.rebuild()

            def done() -> None:
                self.status_label.configure(text=f"索引完成，共 {count} 个知识片段")
                self.refresh_list()

            self.after(0, done)

        threading.Thread(target=task, daemon=True).start()

    def delete_source(self, filename: str) -> None:
        if not messagebox.askyesno("确认删除", f"确定删除 {filename} 吗？"):
            return
        self.store.delete_source(filename)
        self.status_label.configure(text=f"已删除 {filename}")
        self.refresh_list()
