# System Architecture

KrishiMitra follows a decoupled, service-oriented architecture designed to run on edge hardware (Raspberry Pi). 

## High-Level Diagram

```mermaid
graph TD
    %% Hardware / IoT Layer
    subgraph IoT Edge [Raspberry Pi Hardware]
        Sensors[Physical Sensors: DHT22, BH1750, DS18B20] --> SensorDaemon(sensor_hub.py)
        Arduino[Arduino Nano: Soil Moisture & pH] --> SensorDaemon
        SensorDaemon --> |Updates State| JSONState(sensors.json)
        SensorDaemon --> |Cycles Text| LCD16x2[16x2 I2C Display]
        SensorDaemon --> |POST| API_Sensors(/api/sensors/manual)
    end

    %% Backend Layer
    subgraph Backend [FastAPI Application]
        JSONState -.-> |Reads| SensorStore(sensor_store.py)
        API_Sensors --> SQLiteDB[(krishimitra.db)]
        
        Router_Sensors(routers/sensors.py) -.-> SensorStore
        Router_Predict(routers/predict.py) --> ML_Models[XGBoost Models]
        Router_Predict -.-> SensorStore
        Router_Weather(routers/weather.py) --> ExtWeather((Open-Meteo API))
        Router_Alerts(routers/alerts.py) -.-> SensorStore
    end

    %% External Interfaces
    subgraph Interfaces [Displays & Integrations]
        TFTDaemon(display_tft.py) --> |Reads /predict/all| Backend
        ReactDash(React JS Frontend) <--> |REST API| Backend
        OpenClaw(OpenClaw Telegram GenAI) <--> |API Calls| Backend
    end
```

## Layers of the System

### 1. The Sensor Hub (`sensor_hub.py`)
A continuous daemon that loops to read hardware pins. It formats the data, saves the immediate state to `sensors.json` (for extremely fast cross-process reads) and loops the basic field numbers onto the 16x2 character LCD display. It occasionally sends POST requests to the backend to log historical data into the database.

### 2. The FastAPI Backend (`backend/`)
The brain of the system.
- Retrieves data from `sensors.json` thread-safely.
- Exposes RESTful JSON APIs for the React dashboard.
- Hosts 4 Singletons for the Machine Learning models (loaded into RAM memory once at application startup).
- Coordinates third-party weather API connections.
- Has a threshold-trigger alerting engine.

### 3. Display Subsystems
- **TFT Driver (`display_tft.py`)**: Uses `luma.lcd` over SPI to draw a mini dashboard directly on the device enclosure.
- **Web Dashboard (`frontend/`)**: React application running on Vite. Communicates with the FastAPI backend to visualize gauges, history charts, weather, predictive hubs, and natural language alerts.

### 4. Integration
- **OpenClaw**: Connects directly via REST API to power a Telegram Bot using natural language generation (NLG) workflows, dictated by its markdown files (`SOUL.md`, `AGENTS.md`, etc.).
