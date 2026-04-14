"""
API routers — /api/sensors
Endpoints:
  GET  /api/sensors/latest    → current readings
  GET  /api/sensors/history   → last N readings from SQLite
  POST /api/sensors/update    → called by sensor_hub.py to push new readings
  POST /api/sensors/manual    → accept manual NPK / soil-color input from dashboard
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import SensorReading, get_db
from backend import sensor_store

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


# ──────────────────────────── Pydantic models ────────────────────────────────

class SensorUpdatePayload(BaseModel):
    air_temp:      Optional[float] = None
    air_humidity:  Optional[float] = None
    soil_temp:     Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_ph:       Optional[float] = None
    light_lux:     Optional[float] = None


class ManualInputPayload(BaseModel):
    nitrogen:    Optional[float] = None
    phosphorous: Optional[float] = None
    potassium:   Optional[float] = None
    soil_color:  Optional[str]   = None   # e.g. "Black Soil"
    crop_type:   Optional[str]   = None
    soil_type:   Optional[str]   = None   # for fertilizer model
    state:       Optional[str]   = None
    area:        Optional[float] = None


# ──────────────────────────── Endpoints ──────────────────────────────────────

@router.get("/latest")
def get_latest_sensors():
    """Return the most recent sensor reading from memory cache / sensors.json."""
    return sensor_store.get_latest()


@router.get("/history")
def get_sensor_history(
    limit: int = Query(default=48, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Return the last `limit` sensor readings from SQLite."""
    rows = (
        db.query(SensorReading)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp":     r.timestamp.isoformat() if r.timestamp else None,
            "air_temp":      r.air_temp,
            "air_humidity":  r.air_humidity,
            "soil_temp":     r.soil_temp,
            "soil_moisture": r.soil_moisture,
            "soil_ph":       r.soil_ph,
            "light_lux":     r.light_lux,
        }
        for r in reversed(rows)   # chronological order
    ]


@router.post("/update")
def update_sensors(payload: SensorUpdatePayload, db: Session = Depends(get_db)):
    """
    Called by sensor_hub.py every ~2 seconds.
    Updates in-memory cache and persists to SQLite.
    """
    data = payload.model_dump(exclude_none=True)
    sensor_store.update(data)

    # Persist to SQLite (write every call; sensor_hub manages frequency)
    row = SensorReading(
        timestamp     = datetime.utcnow(),
        air_temp      = payload.air_temp,
        air_humidity  = payload.air_humidity,
        soil_temp     = payload.soil_temp,
        soil_moisture = payload.soil_moisture,
        soil_ph       = payload.soil_ph,
        light_lux     = payload.light_lux,
    )
    db.add(row)
    db.commit()
    return {"status": "ok"}


@router.post("/manual")
def set_manual_inputs(payload: ManualInputPayload):
    """
    Store manual farmer inputs (NPK / soil color / crop / state / area).
    These are used by /api/predict/all for the ML models.
    """
    # Store in sensor_store under a "manual" namespace
    data = {f"manual_{k}": v for k, v in payload.model_dump().items() if v is not None}
    sensor_store.update(data)
    return {"status": "ok", "stored": data}
