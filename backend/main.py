import os

"""
SatyaShield AI — Real-Time Multimodal Deepfake & Disinformation Defense Platform

FastAPI enterprise application entry point.
Sets up CORS, includes all API routers, provides health checks,
and exposes WebSocket endpoints for real-time alerts.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import time

from backend.api.routes import media, claims, network, dashboard, incident
from backend.api import websocket
from backend.db.database import init_db
from backend.config import CORS_ORIGINS

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR = BASE_DIR.parent / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SatyaShield AI — Real-Time Multimodal Deepfake Defense Platform",
    description=(
        "Autonomous enterprise platform for detecting deepfakes, synthetic media, "
        "and coordinated inauthentic behavior across images, video, audio, and multilingual claims."
    ),
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(media.router, prefix="/api/v1")
app.include_router(claims.router, prefix="/api/v1")
app.include_router(network.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(incident.router, prefix="/api/v1")
app.include_router(websocket.router)

# ── Static Files ──────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# ── Startup ───────────────────────────────────────────────────────────────────

_start_time = time.time()


@app.on_event("startup")
async def startup():
    """Initialize database and pre-load models on startup."""
    init_db()


# ── Web UI & Health checks ────────────────────────────────────────────────────

@app.get("/", tags=["Web UI"])
async def root():
    """Serves the interactive web intelligence dashboard."""
    index_file = STATIC_DIR / "index.html"
    return FileResponse(index_file)


@app.get("/dashboard", tags=["Web UI"])
async def dashboard_ui():
    """Direct route to the Mission Control dashboard."""
    index_file = STATIC_DIR / "index.html"
    return FileResponse(index_file)


@app.get("/guide", tags=["Web UI"])
async def guide_ui():
    """Serves the printable HTML evaluation guide & jury defense dossier."""
    guide_file = STATIC_DIR / "team_guide.html"
    return FileResponse(guide_file)


@app.get("/pdf", tags=["Web UI"])
async def pdf_ui():
    """Direct route to printable guide and PDF exporter."""
    guide_file = STATIC_DIR / "team_guide.html"
    return FileResponse(guide_file)


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _start_time, 2),
    }
