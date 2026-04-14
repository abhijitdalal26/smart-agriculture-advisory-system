# Hardware & Sensor Setup

KrishiMitra relies on an array of standard IoT sensors connected to a Raspberry Pi 4B, some running directly on GPIO/I2C/SPI buses, and others handled through an analog-to-digital intermediate layer (Arduino).

## Sensors and Connections

| Component | Interface | Description | Purpose |
|---|---|---|---|
| **DHT22** | GPIO 17 | Digital Humidity and Temp Sensor | Measures ambient air temperature (°C) and relative humidity (%). Crucial for crop predictions and frost/heat alerts. |
| **BH1750** | I2C (Address: 0x23) | Light Intensity Sensor | Measures ambient light in Lux. Identifies if overcast conditions are limiting photosynthesis. |
| **DS18B20** | 1-Wire | Digital Thermal Probe | Specifically designed to be buried in the ground to measure precise soil temperature, independent of air temp. |
| **Arduino Nano** | Serial (UART) via USB (`/dev/ttyACM0`) | Microcontroller / ADC | Acts as an Analog-to-Digital converter for sensors that output analog voltages. Measures soil moisture (via a resistive/capacitive probe) and processes soil pH data, passing JSON over Serial to the Pi. |

## Displays

### 1. 16x2 Text LCD (PCF8574)
- **Interface**: I2C (Address: 0x27)
- **Purpose**: Provides a low-cost, high-visibility "glanceable" display of basic sensor readings.
- **Behavior**: Cycles between two screens every 5 seconds (Screen A: Air Temp & Light; Screen B: Soil Temp & pH).

### 2. 1.8" Color TFT Display (ST7735)
- **Interface**: SPI (CS, DC, RST pins mapping directly to Pi GPIO).
- **Purpose**: A rich, visual summary right on the hardware. 
- **Behavior**: Draws a small dashboard including a top status bar (weather/time), the recommended crop, the estimated yield, a color-coded irrigation drop (Blue/Red), and a strip of mini sensor numbers. Driven by the `luma.lcd` Python library.

## Common Interface Issues & Troubleshooting
- **I2C Bus Contention**: Ensure `i2cdetect -y 1` shows both `0x23` and `0x27`.
- **Serial Permission**: Ensure the `ess` user is in the `dialout` group to read `/dev/ttyACM0`.
- **SPI Loading**: Ensure SPI is enabled via `raspi-config` before starting the TFT service.
