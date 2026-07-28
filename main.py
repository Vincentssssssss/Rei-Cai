#!/usr/bin/env python3
import src.http_client  # noqa: F401 - configure SSL before GUI startup

from src.gui.app import App
from src.gui.styles import configure_theme


def main() -> None:
    configure_theme()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
