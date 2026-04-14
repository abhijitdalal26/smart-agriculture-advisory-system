# MEMORY.md — KrishiMitra Curated Long-Term Knowledge

## Project Identity
- System name: KrishiMitra (Smart Agricultural Advisory System)
- Hardware: Raspberry Pi 4B running FastAPI backend + React frontend + Telegram bot via OpenClaw
- GitHub: https://github.com/abhijitdalal26/smart-agriculture-advisory-system
- Pi SSH: `ssh ess@ess.local` (password: 2026) | IP: 10.186.162.189

## 4 ML Models (All XGBoost, trained on Indian agricultural datasets)

### 1. Crop Recommendation
- File: `model/crop_recommandation.json` + `model/crop_recommandation.pkl` (LabelEncoder)
- Input: N, P, K, temperature (°C), humidity (%), pH, rainfall (mm)
- Output: Crop name string (e.g., "rice", "maize", "wheat")

### 2. Yield Prediction
- File: `model/crop_yield.json` + `model/crop_yield.pkl` (feature columns metadata)
- Input: State (Indian state name), Crop, Area (hectares), Season
- Output: Yield (float, kg/hectare)
- Note: Convert to t/acre for display → value / 1000 * 0.405

### 3. Irrigation Need
- File: `model/irrigation_need.json` + `model/irrigation_need.pkl`
- Input: Soil_Type, Soil_pH, Soil_Moisture, Temperature, Humidity, Rainfall, Wind_Speed, Season, Region
- Output: "Low" | "Medium" | "High"
- Season auto-detected: Apr–Jun=Zaid, Jul–Oct=Kharif, Nov–Mar=Rabi
- Region default: "Central"

### 4. Fertilizer Advisory
- File: `model/fertilizer_recommendation.json` + `model/fertilizer_recommendation.pkl`
- Input: Temperature, Humidity, Moisture, Soil Type (categorical), Crop Type (categorical), N, K, P
- Output: Fertilizer name (e.g., "Urea", "DAP", "10-26-26")

## Critical Thresholds (memorise these)
- Soil moisture < 20% → IRRIGATE IMMEDIATELY
- Air temp > 40°C → EXTREME HEAT ALERT
- Soil pH < 5.5 → Apply lime
- Soil pH > 8.0 → Apply sulfur/gypsum
- Light < 200 Lux → Extended overcast — monitor

## Season Calendar (India)
- Kharif: June–October (rice, cotton, maize, soybean)
- Rabi:   November–March (wheat, barley, mustard, peas)
- Zaid:   April–June (watermelon, cucumber, bitter gourd)

## Key Decisions Made
- TFT: 1.8" ST7735 (128×160 px) — using luma.lcd via SPI
- Weather: Open-Meteo (primary, free) + OpenWeather (fallback, key: 606fda0c5bc4a0fc1477de659f256b12)
- Rainfall for crop model: fetched from Open-Meteo last 24h precipitation
- NPK input: both soil-color picker AND manual sliders available on dashboard
- State/location: auto-detected via IP geolocation (ip-api.com), changeable in dashboard
- SIM800L GSM: disabled (not working) — skeleton function retained for future
