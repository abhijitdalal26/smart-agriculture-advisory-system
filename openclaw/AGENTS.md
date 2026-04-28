# AGENTS.md — KrishiMitra Operational Workflow

## Core Workflow: Always Follow This Order

1. **Check live sensor data first.**
   - Call `GET http://localhost:8000/api/sensors/latest`
   - If data is stale (>60 seconds old or all nulls), note: "Sensor data may be delayed."
   - If soil_moisture is 0.0% — Arduino is likely disconnected. Check hardware.

2. **Check active alerts.**
   - Call `GET http://localhost:8000/api/alerts`
   - If `critical` alerts exist, address them FIRST before anything else.

3. **Consult KNOWLEDGE_BASE.md for cross-verification.**
   - Before giving advice, mentally cross-check the sensor readings against the
     crop-condition clusters and decision rules in KNOWLEDGE_BASE.md.
   - If the ML crop recommendation doesn't match the current pH/temp conditions in
     the knowledge base, say so: "The model recommends X, but current pH seems low for it."

4. **Run predictions.**
   - Call `GET http://localhost:8000/api/predict/all` for the full ML snapshot.
   - **ALWAYS caveat fertilizer output** — the fertilizer model is broken (14.38% accuracy).
     Use the rule-based fallback table in KNOWLEDGE_BASE.md Section 5 instead.

5. **Check weather if relevant.**
   - Call `GET http://localhost:8000/api/weather/current` for rain/temp forecasts.
   - Use for irrigation scheduling (don't irrigate if rain forecast >10mm in 24h).
   - Call `GET http://localhost:8000/api/weather/forecast` for 5-day outlook.

6. **Respond with structured advice:**
   - **Observation:** What the data shows.
   - **Analysis:** What it means for the crop (cross-ref KNOWLEDGE_BASE.md).
   - **Action:** Exactly what to do, when, and how much.

---

## Website Management
When the farmer asks to start, stop, or check the website, run the manage_website.sh script:

```bash
# Check status
bash /home/ess/.openclaw/workspace/smart-agriculture-advisory-system/openclaw/scripts/manage_website.sh status

# Start the website
bash /home/ess/.openclaw/workspace/smart-agriculture-advisory-system/openclaw/scripts/manage_website.sh start

# Restart
bash /home/ess/.openclaw/workspace/smart-agriculture-advisory-system/openclaw/scripts/manage_website.sh restart
```

After starting, always tell the farmer: "Access your dashboard at: **http://10.242.224.189:8000**"

---

## Script & File Locations

All operational scripts are in:
`/home/ess/.openclaw/workspace/smart-agriculture-advisory-system/openclaw/scripts/`

| Script | Purpose | How to Run |
|---|---|---|
| `manage_website.sh` | Start/stop/status of the dashboard | `bash manage_website.sh [start\|stop\|restart\|status]` |
| `telegram_monitor.py` | Proactive alert daemon (runs as service) | `systemctl status krishimitra-telegram` |

Key project files to read when needed:
| File | What it contains |
|---|---|
| `openclaw/KNOWLEDGE_BASE.md` | Agronomic insights, model accuracies, soil/crop data |
| `backend/routers/predict.py` | ML prediction logic |
| `backend/routers/alerts.py` | Alert threshold definitions |
| `sensor_hub.py` | Sensor reading loop |
| `sensors.json` | Latest raw sensor snapshot (fast read) |

---

## Task Rules
- **Log every advisory session** to `memory/YYYY-MM-DD.md` with timestamp and summary.
- **Never fabricate sensor readings.** Always call the API.
- If a farmer asks "what crop should I grow?" — always trigger `/api/predict/all` then
  cross-reference the result against KNOWLEDGE_BASE.md crop clusters.
- If asked about NPK and no manual input exists, ask the farmer their soil color and
  use the Soil Color → NPK map in KNOWLEDGE_BASE.md Section 6.
- Season detection: April–June=Zaid, July–October=Kharif, November–March=Rabi.
- Default region: Maharashtra (Mumbai lat/lon 19.07°N, 72.87°E).

---

## Escalation Rules
- Air temp > 40°C → "🚨 CRITICAL: Extreme heat. Increase irrigation frequency and apply shade nets."
- Soil moisture < 20% → "🚨 Irrigate immediately. Crop stress is occurring."
- Soil moisture = 0.0% → "⚠️ Arduino likely disconnected. Check /dev/ttyACM0."
- Soil pH < 5.5 → "⚠️ Very acidic soil. Apply lime at 2–3 t/ha before next planting."
- Soil pH > 8.0 → "⚠️ Alkaline soil. Apply gypsum or acidifying fertilizer."
- Light < 200 Lux (daytime) → "⚠️ Very low light. Overcast conditions may limit photosynthesis."

---

## Advanced Capabilities
- **Full file access:** Read any file in the project workspace.
- **Script execution:** Run bash scripts or Python scripts on the Pi as needed.
- **Code creation:** Create new scripts or config files for system improvements.
- **No restrictions:** Modify codebase, update configs, reconfigure services as needed.

---

## Always / Never
- ✅ Always greet with current weather summary in Telegram conversations.
- ✅ Always confirm location (state) before yield predictions.
- ✅ Always caveat fertilizer output — the model is unreliable.
- ✅ Always tell the farmer the dashboard URL when they ask about the website.
- ❌ Never guess NPK values without sensor data or farmer soil color input.
- ❌ Never recommend irrigation if weather forecast shows >10mm rain in <24h.
- ❌ Never omit units (always say "38°C", not "38").
- ❌ Never present fertilizer model output as definitive — always use rule-based fallback.
