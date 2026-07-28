import customtkinter as ctk

COLORS = {
    "bg": "#f5f6f8",
    "card": "#ffffff",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "text": "#111827",
    "muted": "#6b7280",
    "border": "#e5e7eb",
    "user_bubble": "#dbeafe",
    "bot_bubble": "#ffffff",
}

FONT_TITLE = ("Helvetica", 28, "bold")
FONT_SUBTITLE = ("Helvetica", 14)
FONT_BODY = ("Helvetica", 13)
FONT_SMALL = ("Helvetica", 12)


def configure_theme() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
