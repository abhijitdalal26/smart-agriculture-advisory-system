"""
KrishiMitra — FastAPI Backend Entry Point
Starts the server, loads all ML models on startup, registers all routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.database import init_db
from backend.models.crop_recommender   import recommender
from backend.models.yield_predictor    import predictor
from backend.models.irrigation_advisor import advisor as irr_advisor
from backend.models.fertilizer_advisor import advisor as fert_advisor

from backend.routers import sensors, predict, weather, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup: init DB + load all ML models ────────────────────────────────
    print("[KrishiMitra] Initialising database...")
    init_db()

    print("[KrishiMitra] Loading ML models...")
    recommender.load()
    predictor.load()
    irr_advisor.load()
    fert_advisor.load()
    print("[KrishiMitra] All models ready ✅")

    yield

    # ── Shutdown (clean-up if needed) ────────────────────────────────────────
    print("[KrishiMitra] Shutting down...")


app = FastAPI(
    title       = "KrishiMitra API",
    description = "Smart Agricultural Advisory System — IoT + ML Backend",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── CORS (allow React dev server + Pi dashboard) ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # restrict to Pi IP in production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(sensors.router)
app.include_router(predict.router)
app.include_router(weather.router)
app.include_router(alerts.router)


@app.get("/")
def root():
    return {
        "name":    "KrishiMitra API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}

# ── Frontend Hosting (Single-Port Pi Mount) ──────────────────────────────────
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

# Mount assets natively
if os.path.exists(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        return {"error": "API Route Not Found"}
    
    file_path = os.path.join(frontend_dist, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
        
    fallback = os.path.join(frontend_dist, "index.html")
    if os.path.isfile(fallback):
        return FileResponse(fallback)
    return {"error": "Frontend build (dist) not found. Run npm run build."}
