# 6. Database Truncation & Throttling Strategy

**Context**
KrishiMitra connects physical hardware (Raspberry Pi/Arduino) driving a localized edge network. The internal python hardware loop (`sensor_hub.py`) cycles over the physical DHT22/DS18B20/BH1750 and Arduino pins precisely every *2 seconds*.

**The Storage Problem**  
If the FastAPI backend wrote SQL rows for every telemetry ping, it would commit roughly 43,200 rows per day resulting in catastrophic SD card decay and massive database query lockouts.

## State Decoupling Architecture

To preserve a "live dashboard/LCD" experience while properly archiving logical agriculture logs, KrishiMitra decouples State into two boundaries handled by FastAPI:

1. **Live Fast Memory (`backend/sensor_store.py`)**: 
   - Receives the 2-second POST telemetry from `sensor_hub.py` and strictly caches it in isolated RAM / JSON structs.
   - Drives the React `/latest` API endpoint, providing instantaneous edge reflexes.
   - Triggers the 16x2 physical LCD state directly.

2. **Durable Cold History (`krishimitra.db`)**: 
   - Safely rate-limited by a 15-minute chronological barrier (`last_db_write`) injected at the `/api/sensors/update` endpoint.
   - When 15 minutes clear, the SQLite `db.add` pipeline commits a single row capturing the precise momentary environment.
   - Drastically limits the SQLite log footprint to exactly **96 rows per day** (2,880 rows/month), mathematically preserving SD integrity and ensuring zero lookup-lag for the `/api/sensors/history` endpoint when drawing massive multi-day prediction patterns.

For future agentic implementations altering the sensor routing framework, **do not** write directly to SQLite on `POST` hooks without validating the chronological span threshold logic initialized in `routers/sensors.py`.
