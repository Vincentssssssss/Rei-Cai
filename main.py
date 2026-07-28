#!/usr/bin/env python3
from src.gui.app import App
from src.gui.styles import configure_theme


def main() -> None:
    configure_theme()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
