import threading

import customtkinter as ctk

from src.chat.citations import build_citations
from src.chat.engine import ChatEngine
from src.gui.styles import COLORS, FONT_BODY, FONT_SMALL, FONT_SUBTITLE, FONT_TITLE
from src.knowledge.store import KnowledgeStore


class ChatFrame(ctk.CTkFrame):
    def __init__(self, master, store: KnowledgeStore, on_back) -> None:
        super().__init__(master, fg_color=COLORS["bg"])
        self.store = store
        self.engine = ChatEngine(store)
        self.on_back = on_back
        self._build()
        self._append_bot("你好，我是 Rei-Cai。请基于已上传的资料向我提问。")

    def _build(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 12))

        ctk.CTkButton(header, text="返回", width=72, command=self.on_back).pack(side="left")
        ctk.CTkLabel(header, text="用户入口", font=FONT_TITLE, text_color=COLORS["text"]).pack(side="left", padx=16)

        self.chat_area = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.chat_area.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        input_bar = ctk.CTkFrame(self, fg_color="transparent")
        input_bar.pack(fill="x", padx=24, pady=(0, 24))

        self.input_box = ctk.CTkTextbox(input_bar, height=88, font=FONT_BODY, corner_radius=12)
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.input_box.bind("<Control-Return>", self._on_send)

        self.send_button = ctk.CTkButton(input_bar, text="发送", width=88, height=88, command=self.send_message)
        self.send_button.pack(side="right")

        ctk.CTkLabel(
            self,
            text="Ctrl + Enter 发送",
            font=FONT_SMALL,
            text_color=COLORS["muted"],
        ).pack(anchor="e", padx=24, pady=(0, 8))

    def _append_message(self, role: str, text: str, citations: list[dict] | None = None) -> None:
        bubble_color = COLORS["user_bubble"] if role == "user" else COLORS["bot_bubble"]
        align = "e" if role == "user" else "w"
        anchor = "e" if role == "user" else "w"

        wrapper = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        wrapper.pack(fill="x", padx=12, pady=8)

        label = "你" if role == "user" else "Rei-Cai"
        ctk.CTkLabel(wrapper, text=label, font=FONT_SMALL, text_color=COLORS["muted"]).pack(anchor=anchor)

        bubble = ctk.CTkFrame(wrapper, fg_color=bubble_color, corner_radius=12)
        bubble.pack(anchor=align, fill="x" if role == "bot" else None)

        ctk.CTkLabel(
            bubble,
            text=text,
            font=FONT_BODY,
            text_color=COLORS["text"],
            justify="left",
            wraplength=760,
            anchor="w",
        ).pack(padx=14, pady=12, anchor="w")

        if role == "bot" and citations:
            cite_frame = ctk.CTkFrame(wrapper, fg_color="#f9fafb", corner_radius=12, border_width=1, border_color=COLORS["border"])
            cite_frame.pack(anchor="w", fill="x", pady=(4, 0))
            ctk.CTkLabel(cite_frame, text="引用", font=FONT_SMALL, text_color=COLORS["muted"]).pack(anchor="w", padx=12, pady=(10, 4))
            for index, item in enumerate(citations, start=1):
                excerpt = item["excerpt"]
                if len(excerpt) > 220:
                    excerpt = excerpt[:220].rstrip() + "..."
                cite_text = f"[{index}] {item['source']}\n{excerpt}"
                ctk.CTkLabel(
                    cite_frame,
                    text=cite_text,
                    font=FONT_SMALL,
                    text_color=COLORS["text"],
                    justify="left",
                    wraplength=740,
                    anchor="w",
                ).pack(anchor="w", padx=12, pady=(0, 10))

        self.update_idletasks()
        self.chat_area._parent_canvas.yview_moveto(1.0)

    def _append_bot(self, text: str, citations: list[dict] | None = None) -> None:
        self._append_message("bot", text, citations)

    def _append_user(self, text: str) -> None:
        self._append_message("user", text)

    def _on_send(self, _event=None) -> str:
        self.send_message()
        return "break"

    def send_message(self) -> None:
        question = self.input_box.get("1.0", "end").strip()
        if not question:
            return

        self.input_box.delete("1.0", "end")
        self._append_user(question)
        self.send_button.configure(state="disabled", text="思考中")
        self._append_bot("正在根据资料整理回答...")

        def task() -> None:
            answer, hits = self.engine.answer(question)
            citations = build_citations(hits)

            def done() -> None:
                children = self.chat_area.winfo_children()
                if children:
                    children[-1].destroy()
                self._append_bot(answer, citations)
                self.send_button.configure(state="normal", text="发送")

            self.after(0, done)

        threading.Thread(target=task, daemon=True).start()
