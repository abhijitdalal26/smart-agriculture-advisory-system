# USER.md — Farmer / Operator Profile

## Primary User
- **Name:** Abhijit (operator / student researcher)
- **Location:** Near Mumbai, Maharashtra, India
  - Latitude: 19.07°N | Longitude: 72.87°E
- **Language:** English
- **Experience:** Tech-savvy — comfortable with SSH, Python, and dashboards.

## Farm Details
- **Controller:** Raspberry Pi 4B (hostname: `ess`, username: `ess`)
- **Pi IP:** 10.186.162.189 (may change if DHCP lease changes)
- **Workspace:** `/home/ess/.openclaw/workspace/krishimitra/`
- **Default State:** Maharashtra (overridable from dashboard)
- **Default Season:** Auto-detected from calendar month.

## Communication Preferences
- Telegram bot already connected — prefer short messages (2–3 paragraphs max).
- Use bullet points for multi-step actions.
- Provide both headline and detail: headline in 1 line, details below.
- No marketing language — practical facts only.

## Hardware Reference (Do Not Fabricate Data From These)
| Sensor     | Interface | What it measures              |
|------------|-----------|-------------------------------|
| DHT22      | GPIO 17   | Air temperature, humidity     |
| BH1750     | I2C 0x23  | Light intensity (Lux)         |
| DS18B20    | 1-Wire    | Soil temperature              |
| Arduino Nano | Serial /dev/ttyACM0 | Soil moisture (%), pH |
| LCD 16×2   | I2C 0x27  | Display (PCF8574)             |
| 1.8" TFT   | SPI       | ST7735 display (128×160 px)   |

## Telegram Integration
- Already configured via OpenClaw.
- Bot handle: (user knows — already working)
- Use Telegram for: alerts, quick status checks, crop advice on-the-go.
- Use Web Dashboard for: charts, history, detailed predictions.
