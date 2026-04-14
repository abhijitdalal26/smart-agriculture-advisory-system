"""
Alerts API router — /api/alerts
Computes threshold-based alerts from live sensor data + ML predictions.
Returns a list of active alert objects for the dashboard banner.
"""

from datetime import datetime
from fastapi import APIRouter
from backend import sensor_store

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# ─────────────────────── Threshold config ────────────────────────────────────
THRESHOLDS = {
    "air_temp_high":     40.0,    # °C — extreme heat
    "air_temp_low":      5.0,     # °C — frost risk
    "air_humidity_low":  20.0,    # % — crop stress
    "soil_moisture_low": 20.0,    # % — irrigation required
    "soil_moisture_high": 85.0,   # % — waterlogging risk
    "soil_ph_low":       5.5,     # — acidic
    "soil_ph_high":      8.0,     # — alkaline
    "light_low":         200.0,   # Lux — insufficient light
}

SEVERITY = {
    "extreme_heat":    "critical",
    "frost_risk":      "critical",
    "crop_stress":     "warning",
    "irrigation_req":  "warning",
    "waterlogging":    "warning",
    "acidic_soil":     "info",
    "alkaline_soil":   "info",
    "low_light":       "info",
}


def _check_alerts(sensors: dict) -> list:
    alerts = []
    now = datetime.utcnow().isoformat()

    def add(key: str, message: str, value=None):
        alerts.append({
            "id":       key,
            "severity": SEVERITY.get(key, "info"),
            "message":  message,
            "value":    value,
            "time":     now,
        })

    temp = sensors.get("air_temp")
    hum  = sensors.get("air_humidity")
    mois = sensors.get("soil_moisture")
    ph   = sensors.get("soil_ph")
    lux  = sensors.get("light_lux")

    if temp is not None:
        if temp > THRESHOLDS["air_temp_high"]:
            add("extreme_heat", f"Extreme heat detected: {temp:.1f}°C — protect crops!", temp)
        if temp < THRESHOLDS["air_temp_low"]:
            add("frost_risk", f"Frost risk: {temp:.1f}°C — cover sensitive crops", temp)

    if hum is not None and hum < THRESHOLDS["air_humidity_low"]:
        add("crop_stress", f"Low humidity ({hum:.1f}%) — potential crop stress", hum)

    if mois is not None:
        if mois < THRESHOLDS["soil_moisture_low"]:
            add("irrigation_req", f"Soil moisture is low ({mois:.1f}%) — irrigation required", mois)
        if mois > THRESHOLDS["soil_moisture_high"]:
            add("waterlogging", f"Soil moisture very high ({mois:.1f}%) — waterlogging risk", mois)

    if ph is not None:
        if ph < THRESHOLDS["soil_ph_low"]:
            add("acidic_soil", f"Soil pH is acidic ({ph:.1f}) — consider applying lime", ph)
        if ph > THRESHOLDS["soil_ph_high"]:
            add("alkaline_soil", f"Soil pH is alkaline ({ph:.1f}) — consider sulfur treatment", ph)

    if lux is not None and lux < THRESHOLDS["light_low"]:
        add("low_light", f"Low light intensity ({lux:.0f} Lux) — check for cloud cover", lux)

    return alerts


@router.get("")
@router.get("/")
def get_alerts():
    """Return list of currently active alerts based on latest sensor data."""
    sensors = sensor_store.get_latest()
    alerts  = _check_alerts(sensors)
    return {
        "count":  len(alerts),
        "alerts": alerts,
    }
