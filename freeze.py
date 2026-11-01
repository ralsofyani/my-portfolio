"""Build a static copy of the site into dist/ (used for Render's Static Site).

    python freeze.py

It asks the FastAPI app for the page and the learning ideas once, then writes:
    dist/index.html                    the page (English by default, Arabic via the toggle or ?lang=ar)
    dist/static/...                    CSS, JS, images, CV
    dist/api/learning-ideas.json       the 30 ideas for the ideas card
    dist/favicon.ico                   the site icon
Locally you can keep running the live FastAPI version with uvicorn as usual.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
STATIC = ROOT / "app" / "static"
BASE = "http://testserver"  # TestClient's host; stripped so every link is relative to the site


def main() -> None:
    client = TestClient(app)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # 1. The page
    res = client.get("/")
    res.raise_for_status()
    html = res.text.replace(BASE, "")
    # The static site has no API, so point the ideas card at the JSON file written below.
    html = html.replace("<html ", '<html data-ideas-url="/api/learning-ideas.json" ', 1)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    # 2. Static files
    shutil.copytree(STATIC, DIST / "static")
    shutil.copyfile(STATIC / "images" / "favicon-32.png", DIST / "favicon.ico")

    # 3. The learning ideas
    ideas = client.get("/api/learning-ideas")
    ideas.raise_for_status()
    (DIST / "api").mkdir()
    (DIST / "api" / "learning-ideas.json").write_text(
        json.dumps(ideas.json(), ensure_ascii=False), encoding="utf-8"
    )

    count = sum(1 for p in DIST.rglob("*") if p.is_file())
    print(f"Static site written to {DIST} ({count} files)")


if __name__ == "__main__":
    main()
