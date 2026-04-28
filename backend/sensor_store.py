"""
Thread-safe shared sensor state store.
sensor_hub.py writes to sensors.json; FastAPI reads from it.
Also exposes an in-memory cache so rapid API calls don't hit disk.
"""

import json
import os
import threading
from datetime import datetime
from typing import Optional

_lock      = threading.Lock()
_cache: dict = {}

# Resolve path relative to project root (one level above backend/)
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SENSOR_FILE  = os.path.join(BASE_DIR, "..", "sensors.json")

DEFAULT_SENSORS = {
    "air_temp":      None,
    "air_humidity":  None,
    "soil_temp":     None,
    "soil_moisture": None,
    "soil_ph":       None,
    "light_lux":     None,
    "updated_at":    None,
    "manual_nitrogen": None,
    "manual_phosphorous": None,
    "manual_potassium": None,
    "manual_soil_color": None,
    "manual_crop_type": None,
    "manual_soil_type": None,
    "manual_state": None,
    "manual_area": None,
}


def _load_from_file() -> dict:
    """Read sensors.json from disk; return defaults on any error."""
    try:
        if os.path.exists(SENSOR_FILE):
            with open(SENSOR_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_SENSORS.copy()


def get_latest() -> dict:
    """Return most-recent sensor readings (memory-first, file fallback)."""
    with _lock:
        if _cache:
            return dict(_cache)
        data = _load_from_file()
        _cache.update(data)
        return dict(_cache)


def update(data: dict) -> None:
    """
    Called by sensor_hub.py (via HTTP POST or direct import).
    Merges new values into cache and writes sensors.json.
    """
    payload = {k: v for k, v in data.items() if k in DEFAULT_SENSORS}
    payload["updated_at"] = datetime.utcnow().isoformat()

    with _lock:
        _cache.update(payload)
        try:
            with open(SENSOR_FILE, "w") as f:
                json.dump(_cache, f, indent=2, default=str)
        except Exception as e:
            print(f"[sensor_store] Failed to write sensors.json: {e}")
