"""
API routers — /api/predict
Endpoints:
  POST /api/predict/crop          → crop name
  POST /api/predict/yield         → yield kg/hectare
  POST /api/predict/irrigation    → Low/Medium/High
  POST /api/predict/fertilizer    → fertilizer name
  GET  /api/predict/all           → all 4 models using live sensors + stored manual inputs
"""

import calendar
from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import MLPrediction, get_db
from backend import sensor_store
from backend.models.crop_recommender  import recommender
from backend.models.yield_predictor   import predictor
from backend.models.irrigation_advisor import advisor as irr_advisor
from backend.models.fertilizer_advisor import advisor as fert_advisor, SOIL_COLOR_NPK

router = APIRouter(prefix="/api/predict", tags=["predict"])

# ─────────────────────── Season auto-detection ───────────────────────────────
def _detect_season() -> str:
    month = datetime.now().month
    if month in (6, 7, 8, 9, 10):
        return "Kharif"
    elif month in (11, 12, 1, 2, 3):
        return "Rabi"
    else:
        return "Zaid"  # April, May

# ──────────────────────── Pydantic request models ────────────────────────────

class CropRequest(BaseModel):
    N: float; P: float; K: float
    temperature: float; humidity: float
    ph: float; rainfall: float

class YieldRequest(BaseModel):
    state: str; crop: str
    area: float = 1.0
    season: Optional[str] = None

class IrrigationRequest(BaseModel):
    soil_type:    str   = "Loamy"
    soil_ph:      float = 6.5
    soil_moisture: float = 40.0
    temperature:  float = 28.0
    humidity:     float = 65.0
    rainfall:     float = 0.0
    wind_speed:   float = 10.0
    season:       Optional[str] = None
    region:       str   = "Central"

class FertilizerRequest(BaseModel):
    temperature:  float
    humidity:     float
    moisture:     float
    soil_type:    str   = "Loamy"
    crop_type:    str   = "Wheat"
    nitrogen:     Optional[float] = None
    potassium:    Optional[float] = None
    phosphorous:  Optional[float] = None
    soil_color:   Optional[str]   = None   # if NPK not known

# ─────────────────────────── Helpers ─────────────────────────────────────────

async def _get_rainfall_from_open_meteo(lat: float = 19.07, lon: float = 72.87) -> float:
    """Fetch last-24h precipitation from Open-Meteo (free, no key)."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=precipitation&forecast_days=1&timezone=auto"
    )
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(url)
            data = r.json()
            hours = data.get("hourly", {}).get("precipitation", [])
            return float(sum(hours))
    except Exception:
        return 0.0

# ──────────────────────────── Endpoints ──────────────────────────────────────

@router.post("/crop")
async def predict_crop(req: CropRequest):
    crop = recommender.predict(req.N, req.P, req.K,
                               req.temperature, req.humidity,
                               req.ph, req.rainfall)
    return {"crop": crop}


@router.post("/yield")
def predict_yield(req: YieldRequest):
    season = req.season or _detect_season()
    val = predictor.predict(req.state, req.crop, req.area, season)
    return {"yield_kg_per_hectare": val, "season": season}


@router.post("/irrigation")
def predict_irrigation(req: IrrigationRequest):
    season = req.season or _detect_season()
    result = irr_advisor.predict(
        soil_type     = req.soil_type,
        soil_ph       = req.soil_ph,
        soil_moisture = req.soil_moisture,
        temperature   = req.temperature,
        humidity      = req.humidity,
        rainfall      = req.rainfall,
        wind_speed    = req.wind_speed,
        season        = season,
        region        = req.region,
    )
    return {"irrigation_need": result, "season": season}


@router.post("/fertilizer")
def predict_fertilizer(req: FertilizerRequest):
    # Resolve NPK: manual entry takes priority; soil color is fallback
    if req.nitrogen is not None and req.phosphorous is not None and req.potassium is not None:
        N, P, K = req.nitrogen, req.phosphorous, req.potassium
    elif req.soil_color:
        npk = SOIL_COLOR_NPK.get(req.soil_color, {"N": 40, "P": 30, "K": 40})
        N, P, K = npk["N"], npk["P"], npk["K"]
    else:
        N, P, K = 40.0, 30.0, 40.0

    result = fert_advisor.predict(
        temperature  = req.temperature,
        humidity     = req.humidity,
        moisture     = req.moisture,
        soil_type    = req.soil_type,
        crop_type    = req.crop_type,
        nitrogen     = N,
        potassium    = K,
        phosphorous  = P,
    )
    return {"fertilizer": result, "npk_used": {"N": N, "P": P, "K": K}}


@router.get("/all")
async def predict_all(db: Session = Depends(get_db)):
    """
    Master endpoint: combines live sensor data + manual inputs stored in
    sensor_store, runs all 4 models, returns consolidated JSON.
    Used by React dashboard (polls every 30s) and TFT display.
    """
    sensors = sensor_store.get_latest()

    # ── Gather values (sensor > manual fallback > default) ───────────────────
    air_temp      = sensors.get("air_temp")      or 28.0
    air_humidity  = sensors.get("air_humidity")  or 65.0
    soil_moisture = sensors.get("soil_moisture") or 40.0
    soil_ph       = sensors.get("soil_ph")       or 6.5
    soil_temp     = sensors.get("soil_temp")     or 26.0

    # Manual overrides from dashboard
    N     = sensors.get("manual_nitrogen")    or 40.0
    P     = sensors.get("manual_phosphorous") or 30.0
    K     = sensors.get("manual_potassium")   or 40.0
    color = sensors.get("manual_soil_color")
    if color and (sensors.get("manual_nitrogen") is None):
        npk = SOIL_COLOR_NPK.get(color, {"N": 40, "P": 30, "K": 40})
        N, P, K = npk["N"], npk["P"], npk["K"]

    soil_type  = sensors.get("manual_soil_type") or "Loamy"
    crop_type  = sensors.get("manual_crop_type") or "Wheat"
    state      = sensors.get("manual_state")     or "Maharashtra"
    area       = sensors.get("manual_area")      or 1.0
    season     = _detect_season()
    rainfall   = await _get_rainfall_from_open_meteo()

    # ── Run all 4 models ─────────────────────────────────────────────────────
    crop  = recommender.predict(N, P, K, air_temp, air_humidity, soil_ph, rainfall)
    yield_val = predictor.predict(state, crop, area, season)
    irr   = irr_advisor.predict(soil_type, soil_ph, soil_moisture,
                                air_temp, air_humidity, rainfall, 10.0, season, "Central")
    fert  = fert_advisor.predict(air_temp, air_humidity, soil_moisture,
                                 soil_type, crop_type, N, K, P)

    result = {
        "crop":             crop,
        "yield_kg_per_ha":  yield_val,
        "irrigation_need":  irr,
        "fertilizer":       fert,
        "season":           season,
        "rainfall_mm":      round(rainfall, 2),
        "inputs": {
            "N": N, "P": P, "K": K,
            "air_temp": air_temp, "air_humidity": air_humidity,
            "soil_moisture": soil_moisture, "soil_ph": soil_ph,
            "state": state, "area": area,
        }
    }

    # ── Persist to SQLite ─────────────────────────────────────────────────────
    row = MLPrediction(
        timestamp       = datetime.utcnow(),
        crop            = crop,
        yield_value     = yield_val,
        irrigation_need = irr,
        fertilizer      = fert,
        n_value         = N, p_value = P, k_value = K,
        state           = state,
    )
    db.add(row); db.commit()

    return result
