#!/usr/bin/env python3
import os

import src.http_client  # noqa: F401 - configure SSL before app startup

from src.web.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
