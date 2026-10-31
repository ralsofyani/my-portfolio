"""FastAPI entry point.

Run locally:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.routers import api, pages

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Rawan · Portfolio",
    version=__version__,
    description="A bilingual single-page portfolio, served with love by FastAPI.",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(pages.router)
app.include_router(api.router)


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"
    return response
