"""
Weather API router — /api/weather
Primary  : Open-Meteo (free, no key needed)
Fallback : OpenWeatherMap (key from env)
Endpoints:
  GET /api/weather/current   → now conditions + icon key
  GET /api/weather/forecast  → 5-day daily forecast
  GET /api/weather/location  → IP-based geolocation (lat/lon/state/city)
"""

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/weather", tags=["weather"])

OWM_API_KEY  = "606fda0c5bc4a0fc1477de659f256b12"
DEFAULT_LAT  = 19.07
DEFAULT_LON  = 72.87

# ─────────────────────── Icon mapping ────────────────────────────────────────
def _weather_icon(wmo_code: int) -> str:
    """Map WMO weather code → simple icon key for the frontend."""
    if wmo_code == 0:                        return "sunny"
    if wmo_code in (1, 2):                  return "partly_cloudy"
    if wmo_code == 3:                        return "cloudy"
    if wmo_code in range(51, 68):            return "rainy"
    if wmo_code in range(71, 78):            return "snowy"
    if wmo_code in range(80, 83):            return "showers"
    if wmo_code in range(95, 100):           return "thunderstorm"
    return "cloudy"

# ──────────────────────── Open-Meteo helpers ─────────────────────────────────

async def _open_meteo_current(lat: float, lon: float) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"weather_code,wind_speed_10m,precipitation"
        f"&timezone=auto"
    )
    async with httpx.AsyncClient(timeout=6) as c:
        r    = await c.get(url)
        data = r.json()
    cur = data.get("current", {})
    return {
        "source":       "open-meteo",
        "temperature":  cur.get("temperature_2m"),
        "feels_like":   cur.get("apparent_temperature"),
        "humidity":     cur.get("relative_humidity_2m"),
        "wind_speed":   cur.get("wind_speed_10m"),
        "precipitation":cur.get("precipitation"),
        "wmo_code":     cur.get("weather_code"),
        "icon":         _weather_icon(cur.get("weather_code", 3)),
    }


async def _open_meteo_forecast(lat: float, lon: float) -> list:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,weather_code,"
        f"precipitation_sum,wind_speed_10m_max"
        f"&forecast_days=5&timezone=auto"
    )
    async with httpx.AsyncClient(timeout=6) as c:
        r    = await c.get(url)
        data = r.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    return [
        {
            "date":        dates[i],
            "temp_max":    daily["temperature_2m_max"][i],
            "temp_min":    daily["temperature_2m_min"][i],
            "precipitation": daily["precipitation_sum"][i],
            "wind_speed":  daily["wind_speed_10m_max"][i],
            "wmo_code":    daily["weather_code"][i],
            "icon":        _weather_icon(daily["weather_code"][i]),
        }
        for i in range(len(dates))
    ]


# ──────────────────── OpenWeatherMap fallback ─────────────────────────────────

async def _owm_current(lat: float, lon: float) -> dict:
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
    )
    async with httpx.AsyncClient(timeout=6) as c:
        r    = await c.get(url)
        data = r.json()
    return {
        "source":       "openweathermap",
        "temperature":  data.get("main", {}).get("temp"),
        "feels_like":   data.get("main", {}).get("feels_like"),
        "humidity":     data.get("main", {}).get("humidity"),
        "wind_speed":   data.get("wind", {}).get("speed"),
        "precipitation": data.get("rain", {}).get("1h", 0),
        "icon":         "cloudy",
        "description":  data.get("weather", [{}])[0].get("description", ""),
    }


# ─────────────────────── IP Geolocation helper ───────────────────────────────

async def _ip_geolocation() -> dict:
    """Use ip-api.com (free) to auto-detect lat/lon/state from Pi's public IP."""
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r    = await c.get("http://ip-api.com/json/?fields=lat,lon,regionName,city,country")
            data = r.json()
        return {
            "lat":    data.get("lat", DEFAULT_LAT),
            "lon":    data.get("lon", DEFAULT_LON),
            "state":  data.get("regionName", "Maharashtra"),
            "city":   data.get("city", "Mumbai"),
            "country":data.get("country", "India"),
        }
    except Exception:
        return {"lat": DEFAULT_LAT, "lon": DEFAULT_LON,
                "state": "Maharashtra", "city": "Mumbai", "country": "India"}


# ──────────────────────────── Endpoints ──────────────────────────────────────

@router.get("/location")
async def get_location():
    """Return IP-based location (lat, lon, state, city) for dashboard auto-fill."""
    return await _ip_geolocation()


@router.get("/current")
async def get_current_weather():
    loc = await _ip_geolocation()
    lat, lon = loc["lat"], loc["lon"]
    try:
        weather = await _open_meteo_current(lat, lon)
        weather["location"] = loc
        return weather
    except Exception:
        # Fallback to OpenWeatherMap
        weather = await _owm_current(lat, lon)
        weather["location"] = loc
        return weather


@router.get("/forecast")
async def get_forecast():
    loc = await _ip_geolocation()
    forecast = await _open_meteo_forecast(loc["lat"], loc["lon"])
    return {"location": loc, "forecast": forecast}
