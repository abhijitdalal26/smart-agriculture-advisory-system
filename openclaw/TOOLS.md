# TOOLS.md — KrishiMitra API Reference

## Base URL
All API calls use: `http://localhost:8000`

## Sensor Data
```
GET /api/sensors/latest           → current readings (JSON)
GET /api/sensors/history?limit=48 → last 48 readings from SQLite
POST /api/sensors/manual          → set manual inputs (NPK, soil color, state, crop)
```

### Example: Latest Sensors Response
```json
{
  "air_temp": 28.4,
  "air_humidity": 67.0,
  "soil_temp": 24.1,
  "soil_moisture": 42.5,
  "soil_ph": 6.8,
  "light_lux": 1450.0,
  "updated_at": "2026-04-14T15:30:00"
}
```

## ML Predictions
```
GET  /api/predict/all              → run all 4 models with live data
POST /api/predict/crop             → { N, P, K, temperature, humidity, ph, rainfall }
POST /api/predict/yield            → { state, crop, area, season }
POST /api/predict/irrigation       → { soil_type, soil_ph, soil_moisture, ... }
POST /api/predict/fertilizer       → { temperature, humidity, moisture, soil_type, crop_type, N, K, P }
```

### Example: /api/predict/all Response
```json
{
  "crop": "rice",
  "yield_kg_per_ha": 2987.4,
  "irrigation_need": "Medium",
  "fertilizer": "Urea",
  "season": "Kharif",
  "rainfall_mm": 2.4
}
```

## Weather
```
GET /api/weather/current    → temp, humidity, wind, precipitation, icon, location
GET /api/weather/forecast   → 5-day daily forecast array
GET /api/weather/location   → IP-based lat/lon/state/city
```

## Alerts
```
GET /api/alerts             → list of active threshold alerts with severity
```

### Alert Severity Levels
| Level    | Meaning                              |
|----------|--------------------------------------|
| critical | Immediate action required            |
| warning  | Action needed within 24h             |
| info     | Informational, monitor situation     |

## Soil Color → NPK Mapping
| Color       | N  | P  | K  |
|-------------|----|----|-----|
| Black Soil  | 80 | 40 | 40  |
| Red Soil    | 20 | 15 | 35  |
| Alluvial    | 60 | 45 | 80  |
| Sandy Soil  | 15 | 10 | 20  |
| Clay Soil   | 50 | 35 | 45  |

## Alert Thresholds
| Parameter     | Low    | High  |
|---------------|--------|-------|
| Air Temp (°C) | < 5    | > 40  |
| Humidity (%)  | < 20   | -     |
| Soil Moisture | < 20   | > 85  |
| Soil pH       | < 5.5  | > 8.0 |
| Light (Lux)   | < 200  | -     |
