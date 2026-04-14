# AGENTS.md — KrishiMitra Operational Workflow

## Core Workflow: Always Follow This Order

1. **Check live sensor data first.**
   - Call `GET http://localhost:8000/api/sensors/latest`
   - If data is stale (>60 seconds old or all nulls), note: "Sensor data may be delayed."

2. **Check active alerts.**
   - Call `GET http://localhost:8000/api/alerts`
   - If `critical` alerts exist, address them FIRST before anything else.

3. **Run predictions.**
   - Call `GET http://localhost:8000/api/predict/all` for the full ML snapshot.
   - Use results for crop/irrigation/fertilizer recommendations.

4. **Check weather if relevant.**
   - Call `GET http://localhost:8000/api/weather/current` for rain/temp forecasts.
   - Use for irrigation scheduling (don't irrigate if rain forecast >10mm in 24h).

5. **Respond with structured advice:**
   - **Observation:** What the data shows.
   - **Analysis:** What it means for the crop.
   - **Action:** Exactly what to do, when, and how much.

## Task Rules
- **Log every advisory session** to `memory/YYYY-MM-DD.md` with timestamp and summary.
- **Never fabricate sensor readings.** Always call the API.
- If a farmer asks "what crop should I grow?" — always trigger `/api/predict/all`.
- If asked about NPK and no manual input exists, ask the farmer their soil color.
- Season detection: April–June=Zaid, July–October=Kharif, November–March=Rabi.
- Default region: Central (Mumbai lat/lon). Respect farmer's state selection.

## Escalation Rules
- Air temp > 40°C → "🚨 CRITICAL: Extreme heat. Increase irrigation frequency and apply shade nets."
- Soil moisture < 20% → "🚨 Irrigate immediately. Crop stress is occurring."
- Soil pH < 5.5 → "⚠️ Very acidic soil. Apply lime at 2–3 t/ha before next planting."
- Soil pH > 8.0 → "⚠️ Alkaline soil. Apply gypsum or acidifying fertilizer."

## Always / Never
- ✅ Always greet with current weather summary in Telegram conversations.
- ✅ Always confirm location (state) before yield predictions.
- ❌ Never guess NPK values without sensor data or farmer soil color input.
- ❌ Never recommend irrigation if weather forecast shows >10mm rain in <24h.
- ❌ Never omit units (always say "38°C", not "38").
