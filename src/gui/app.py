import customtkinter as ctk

from src.gui.admin import AdminFrame
from src.gui.chat import ChatFrame
from src.gui.styles import COLORS, FONT_BODY, FONT_SMALL, FONT_SUBTITLE, FONT_TITLE
from src.config import get_llm_status
from src.knowledge.store import KnowledgeStore


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, store: KnowledgeStore, on_navigate) -> None:
        super().__init__(master, fg_color=COLORS["bg"])
        self.store = store
        self.on_navigate = on_navigate
        self._build()

    def _build(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text="Rei-Cai", font=FONT_TITLE, text_color=COLORS["text"]).pack(pady=(0, 8))
        ctk.CTkLabel(
            container,
            text="基于资料学习的智能对话机器人",
            font=FONT_SUBTITLE,
            text_color=COLORS["muted"],
        ).pack(pady=(0, 36))

        card = ctk.CTkFrame(container, fg_color=COLORS["card"], corner_radius=16, border_width=1, border_color=COLORS["border"])
        card.pack(padx=24, pady=8)

        ctk.CTkButton(
            card,
            text="用户入口",
            width=280,
            height=52,
            font=FONT_BODY,
            command=lambda: self.on_navigate("user"),
        ).pack(padx=32, pady=(28, 12))

        ctk.CTkButton(
            card,
            text="管理入口",
            width=280,
            height=52,
            font=FONT_BODY,
            fg_color="#4b5563",
            hover_color="#374151",
            command=lambda: self.on_navigate("admin"),
        ).pack(padx=32, pady=(0, 28))

        stats = self.store.list_sources()
        llm = get_llm_status()
        ctk.CTkLabel(
            container,
            text=f"当前资料：{len(stats)} 个文件，{len(self.store.documents)} 个知识片段",
            font=("Helvetica", 12),
            text_color=COLORS["muted"],
        ).pack(pady=(24, 0))

        if llm["configured"]:
            llm_text = f"大模型：已配置 · {llm['model']} · {llm['base_url']}"
        else:
            llm_text = "大模型：未配置（请设置 OPENAI_API_KEY 等环境变量）"
        ctk.CTkLabel(
            container,
            text=llm_text,
            font=FONT_SMALL,
            text_color=COLORS["muted"],
        ).pack(pady=(8, 0))


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Rei-Cai")
        self.geometry("960x680")
        self.minsize(860, 600)
        self.configure(fg_color=COLORS["bg"])

        self.store = KnowledgeStore()
        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.container.pack(fill="both", expand=True)
        self.current_frame = None
        self.show_home()

    def clear_container(self) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_home(self) -> None:
        self.clear_container()
        self.current_frame = HomeFrame(self.container, self.store, self.navigate)
        self.current_frame.pack(fill="both", expand=True)

    def show_admin(self) -> None:
        self.clear_container()
        self.current_frame = AdminFrame(self.container, self.store, self.show_home)
        self.current_frame.pack(fill="both", expand=True)

    def show_user(self) -> None:
        self.clear_container()
        self.current_frame = ChatFrame(self.container, self.store, self.show_home)
        self.current_frame.pack(fill="both", expand=True)

    def navigate(self, target: str) -> None:
        if target == "admin":
            self.show_admin()
        elif target == "user":
            self.show_user()
        else:
            self.show_home()
