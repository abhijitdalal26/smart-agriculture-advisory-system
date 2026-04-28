# KNOWLEDGE_BASE.md — KrishiMitra Agronomic Intelligence

> This file is for OpenClaw's internal use only. It contains deep agronomic insights extracted from data analysis, research notebooks, and the project's trained models. Do NOT share this raw file with the farmer — instead, translate insights into actionable advice.

---

## 1. System Intelligence Summary

| Model | Accuracy/Score | Status | Notes |
|---|---|---|---|
| Crop Recommendation (XGBoost) | **98.86%** | ✅ Production-Ready | Best model. High confidence. |
| Yield Prediction (XGBoost Regression) | **R² = 0.9385** | ✅ Production-Ready | Low MAE (15.9), reliable for all Indian states. |
| Smart Irrigation (XGBoost Classifier) | **73.70%** | ⚠️ Deployed, Improvable | Accuracy can be increased by re-adding Crop_Type, Sunlight_Hours, Field_Area features. Use with caution. |
| Fertilizer Recommendation (XGBoost) | **14.38%** | 🚨 BROKEN — Random Guessing | Near-uniform label distribution; model is no better than random. **Always caveat any fertilizer output with "This recommendation may not be reliable."** |

---

## 2. Crop Recommendation — Deep Insights

**Dataset:** 2,200 rows. 22 Indian crops. Features: N, P, K, temperature, humidity, pH, rainfall.

### Crop-Condition Clusters (from EDA)
These are the environmental fingerprints for each crop group. Use these to cross-verify live sensor readings:

| Crop Cluster | N (ppm) | P (ppm) | K (ppm) | Temp (°C) | Humidity (%) | pH | Rainfall (mm) |
|---|---|---|---|---|---|---|---|
| **Rice** | High (80+) | Medium | Medium | 20–27 | 80–85 | 6.0–7.0 | High (200+) |
| **Maize** | Medium (60–80) | Medium | Medium | 18–27 | 55–75 | 5.5–7.5 | 60–110 |
| **Chickpea / Lentil** | Low (0–40) | High | Medium | 7–22 | 15–65 | 6.5–8.5 | Low (40–100) |
| **Cotton** | High (100+) | Medium | High | 21–30 | 50–70 | 6.0–8.0 | Medium |
| **Banana / Papaya** | High | High | High | 25–35 | 75–90 | 6.0–7.5 | High |
| **Apple / Grapes** | Low–Medium | Low | Medium | 0–24 | 90+ | 5.5–6.5 | High |
| **Muskmelon / Watermelon** | Low–Medium | Low | Medium | 25–38 | 65–90 | 6.0–7.0 | Low |
| **Coffee** | High | Medium | High | 18–28 | 65–90 | 6.0–6.5 | High |
| **Coconut** | Medium | Low | High | 22–36 | 80–95 | 5.0–7.5 | Very High |

### Decision Rule for Crop Verification
Before delivering a crop recommendation, cross-check:
1. Is soil pH in the acceptable range for the recommended crop?
2. Is temperature within the crop's tolerance? (Critical for frost/heat alerts)
3. If soil moisture < 20%, always warn that any crop is at risk regardless of the ML prediction.

### Crops by Season (Indian Calendar)
- **Kharif (July–Oct):** Rice, Maize, Cotton, Jute, Pigeonpeas, Mungbean, Blackgram
- **Rabi (Nov–Mar):** Wheat, Chickpea, Lentil, Mustard
- **Zaid (Apr–Jun):** Muskmelon, Watermelon, Cucumber, Bitter Gourd

---

## 3. Yield Prediction — Deep Insights

**Dataset:** 26,000+ rows. Features: State, Crop, Area (hectares), Season.

### Key Findings from EDA
- **Top yielding crops in India:** Sugarcane, Coconut, Banana (very high kg/ha due to high water use)
- **Most variable states:** Uttar Pradesh and Maharashtra show the highest production variance due to diverse crop types.
- **The model dropped `Production` to avoid target leakage** — yield is derived from production, so including it would be cheating.
- **Outlier crops:** Coconut and Sugarcane are ~10x higher than grain crops; always report units clearly.
- **Dropped columns in training:** `Crop_Year`, `Fertilizer`, `Production` — these caused data leakage.
- Best overall model: **XGBRegressor** (n_estimators=500, depth=8, lr=0.05) — RMSE 221.99, R²=0.9385

### Advice Rule
- Always confirm the farmer's State before running a yield prediction.
- If state = "Maharashtra", default crops are: Cotton, Soybean, Jowar, Sugarcane.
- Yield output is in **kg/hectare**. If the farmer asks in tonnes/acre: divide by 1000, then multiply by 0.4047.

---

## 4. Smart Irrigation — Deep Insights

**Dataset:** 10,000 rows. Features: Soil Type, pH, Moisture, Temperature, Humidity, Rainfall, Wind Speed, Season, Region.

### Why Accuracy is Only 73.70%
The initial model dropped key features: **Crop_Type, Sunlight_Hours, Field_Area**. Re-adding these will significantly improve classification. The trained model is functional but has a bias toward predicting "Medium" irrigation.

### Irrigation Decision Rules (Cross-Check)
Use these to override or reinforce the model output:

| Condition | Action |
|---|---|
| Soil Moisture < 20% | 🚨 ALWAYS: "Irrigate Immediately" — override model if needed |
| Soil Moisture > 70% | "Hold irrigation — risk of waterlogging and root rot" |
| Weather forecast rain > 10mm in 24h | "Skip irrigation — natural rainfall expected" |
| Air Temp > 38°C + Moisture < 30% | "Emergency irrigation needed — heat + drought stress" |
| Soil pH < 5.5 + Moisture high | "Reduce irrigation — acidic waterlogged soil harmful" |

### Soil Type Characteristics (for farmer advice)
| Soil Type | Water Retention | Drainage | Advice |
|---|---|---|---|
| Sandy | Very Low | Very High | Irrigate frequently with small amounts |
| Clay/Clayey | Very High | Very Low | Risk of waterlogging; water less often |
| Loamy | Medium | Medium | Ideal; standard irrigation schedule |
| Red | Low | High | Moderate irrigation; iron-rich, suits legumes |
| Black (Regur) | High | Low | Retains moisture well; reduce irrigation in Kharif |
| Alluvial | High | Good | Ideal for most crops; standard irrigation |

---

## 5. Fertilizer Recommendation — Deep Insights

**Dataset:** 100,000 rows. Features: Temperature, Humidity, Moisture, Soil Type, Crop Type, N, P, K.

### Known Issue: Model is Broken
- **Test Accuracy: 14.38%** — identical to random guessing (1/7 classes = 14.3%)
- **Root Cause:** The Kaggle dataset (irakozekelly) appears to have near-uniform label distribution. The model's validation loss *increased* throughout training (1.946 → 1.979), confirming it learned nothing useful.
- **Impact:** Fertilizer outputs from `/api/predict/fertilizer` are unreliable.
- **Fix Plan:** Replace dataset with one containing stronger crop-soil-NPK correlations, or add target encoding for Crop Type × Soil Type interaction.

### Use Rule-Based Fallback Instead
Until the model is fixed, use these agronomic rules for fertilizer advice:

| Situation | Fertilizer Advice |
|---|---|
| N low (<40), any crop | Apply Urea (46-0-0) — fastest N source |
| N low, P low, young plants | Apply DAP (18-46-0) — promotes root/early growth |
| All NPK deficient | Apply 17-17-17 (general purpose balanced) |
| Fruit/flowering stage | Apply 0-52-34 (MKP) — high P and K for fruiting |
| Established crops, maintenance | Apply 20-20-0 or 28-28-0 |
| Potassium deficient, drought stress | Apply MOP (0-0-60) — potassium for root strength |
| Post-harvest soil restoration | Apply 14-35-14 — restores P and K after heavy cropping |

---

## 6. Soil Color → NPK Approximation Map
Use when the farmer doesn't have soil test reports:

| Soil Color / Type | N (approx) | P (approx) | K (approx) | Common Regions |
|---|---|---|---|---|
| Black Soil (Regur) | 80 | 40 | 40 | Maharashtra, MP, Gujarat |
| Red Soil | 20 | 15 | 35 | AP, Karnataka, Tamil Nadu |
| Alluvial Soil | 60 | 45 | 80 | UP, Punjab, West Bengal |
| Sandy Soil | 15 | 10 | 20 | Rajasthan, Coastal areas |
| Clay Soil | 50 | 35 | 45 | Delta regions |
| Loamy Soil | 55 | 40 | 60 | General farming regions |

---

## 7. Indian Agriculture — Seasonal Patterns & Insights

### Critical Periods by Month
| Month | Risk | Advisory Focus |
|---|---|---|
| Apr–May | Heat stress (>40°C common), Zaid crops | Monitor air temp; suggest heat-tolerant crops |
| Jun–Jul | Monsoon onset; Kharif sowing window | Check soil moisture; guide Kharif planting |
| Aug–Sep | Peak Kharif growth | Monitor diseases; nitrogen application window |
| Oct–Nov | Kharif harvest; Rabi sowing | Yield tracking; guide Rabi planning |
| Dec–Feb | Frost risk in North India | Alert if temp < 5°C; cold-stress crops |
| Mar | Rabi harvest | Yield assessment; soil recovery advice |

### Maharashtra-Specific Notes (Primary User Region)
- **Dominant crops:** Soybean, Cotton, Sugarcane, Jowar, Wheat
- **Soils:** Primarily Black Cotton Soil (Regur) — apply NPK: N=80, P=40, K=40 as default
- **Average rainfall:** 1,000–2,500mm (varies from Konkan to Marathwada significantly)
- **Marathwada region:** Drought-prone; soil moisture alerts are CRITICAL here
- **Konkan region:** High humidity and rainfall; focus on fungal disease prevention

---

## 8. File System Map for OpenClaw
```
/home/ess/.openclaw/workspace/
├── smart-agriculture-advisory-system/     ← Git repo (the full project)
│   ├── backend/main.py                    ← FastAPI app
│   ├── backend/routers/predict.py         ← ML prediction endpoints
│   ├── backend/routers/sensors.py         ← Sensor data endpoints
│   ├── backend/routers/weather.py         ← Weather API endpoints
│   ├── backend/routers/alerts.py          ← Alert engine
│   ├── sensor_hub.py                      ← DHT22/BH1750/DS18B20/Arduino loop
│   ├── display_tft.py                     ← ST7735 TFT display driver
│   ├── deployment/quick_deploy.sh         ← Full setup script
│   ├── openclaw/SOUL.md                   ← Identity file
│   ├── openclaw/AGENTS.md                 ← Workflow rules
│   ├── openclaw/TOOLS.md                  ← API reference
│   ├── openclaw/USER.md                   ← User/farm profile
│   ├── openclaw/KNOWLEDGE_BASE.md         ← This file (agronomic intelligence)
│   └── openclaw/scripts/                  ← Executable operational scripts
│       ├── manage_website.sh              ← Start/stop/status of the website
│       └── telegram_monitor.py            ← Proactive alert sender
├── SOUL.md                                ← Live copy (synced by deploy script)
├── AGENTS.md                              ← Live copy
├── TOOLS.md                               ← Live copy
├── USER.md                                ← Live copy
└── KNOWLEDGE_BASE.md                      ← Live copy
```

---

## 9. Known Hardware Issues & Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Arduino NOT Connected (ttyACM0) | USB cable loose or Arduino not powered | Re-plug USB; check `ls /dev/ttyACM*`; restart sensors service |
| DHT22 read failure | GPIO noise or sensor timeout | Check GPIO 17 connection; retry (sensor_hub auto-retries) |
| BH1750 returning 0 Lux | I2C address conflict or dark room | Run `i2cdetect -y 1`; verify 0x23 is shown |
| TFT blank screen | SPI not enabled or luma.lcd error | Check `raspi-config` > Interfaces > SPI; restart TFT service |
| Soil moisture always 0% | Arduino not connected | Fix Arduino connection; soil data flows through Arduino serial |
| Backend not responding | uvicorn crashed | Run `systemctl restart krishimitra-backend` |
