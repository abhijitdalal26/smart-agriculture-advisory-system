# KrishiMitra: Smart Agricultural Advisory System

## Overview
**KrishiMitra** (कृषिमित्र — "Friend of the Farmer") is an end-to-end IoT and AI-driven agricultural system. The primary goal is to provide farmers with real-time field data, machine learning-based crop and irrigation advice, and an intelligent dashboard for monitoring their crops.

The system is designed to run on a **Raspberry Pi 4B** deployed at the edge (on the farm or a greenhouse), acting as the central hub. It collects data from local sensors, runs local machine learning inference using trained XGBoost models, and presents the intelligence via a beautiful web dashboard and a local TFT display.

## Key Features
1. **Real-time Environment Telemetry**: Monitors air temperature, air humidity, soil moisture, soil temperature, soil pH, and light intensity (Lux).
2. **AI Predictive Intelligence**: Uses 4 distinct ML models to provide:
   - Best crop recommendations based on soil health and climate.
   - Yield forecasting based on crop type, area, and season.
   - Irrigation advisories.
   - Fertilizer recommendations.
3. **Natural Language Generation (NLG) Advisories**: Translates raw numerical data and ML predictions into actionable, human-readable advice for farmers.
4. **Local Displays**: Features a 16x2 LCD for quick text cycling and a 1.8-inch ST7735 color TFT display that shows a mini-dashboard directly on the hardware.
5. **Weather Integration**: Uses IP-based geolocation and the Open-Meteo API to integrate local real-time weather and 5-day forecasts.
6. **Alerting System**: Implements a threshold-based alert engine to warn of critical issues (e.g., frost risk, extreme heat, very low moisture).

## Core Philosophy
- **Local First**: While it uses some external APIs for weather, the system is designed to keep core logic and ML inference strictly on the local Raspberry Pi.
- **Farmer-Centric**: Information is translated into actionable insights (e.g., "Irrigate immediately", "Expected yield is 2 tonnes/acre") rather than just showing raw sensor numbers.
- **Robustness**: Provides fallbacks (e.g., IP geolocation if GPS missing, secondary weather APIs if primary fails, manual inputs if sensors fail).
