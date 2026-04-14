"""
KrishiMitra — 1.8" ST7735 TFT Display Driver (128×160 px)
Uses luma.lcd with ST7735 driver over SPI.

Layout (128 wide × 160 tall):
  y  0-22  : Top Bar   — time | Wi-Fi icon | weather icon
  y 23-95  : Crop Area — "Best Crop:" label + crop name
  y 96-118 : Yield     — "Yield:" + value
  y119-148 : Irrigation— drop icon (BLUE=good, RED=required)
  y149-160 : Sensor strip — mini line of key values

Refreshes every 30 seconds from /api/predict/all and /api/weather/current.
Sensor bar refreshes every 5 seconds from sensors.json.
"""

import json
import os
import time
import datetime
import threading
import requests

from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import spi
from luma.lcd.device import st7735

# ── SPI / GPIO config for 1.8" ST7735 on Raspberry Pi ───────────────────────
# Typical wiring: CS=GPIO8(CE0), DC=GPIO24, RST=GPIO25, SPI bus 0, device 0
serial_iface = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=16000000)
device       = st7735(serial_iface, width=160, height=128, h_offset=0, v_offset=0, rotate=1)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
SENSOR_FILE = os.path.join(BASE_DIR, "sensors.json")
API_BASE    = "http://localhost:8000"

# ── Fonts (PIL default — no external font needed on Pi) ───────────────────────
try:
    FONT_SM  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",       8)
    FONT_MD  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",      11)
    FONT_LG  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    FONT_XL  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
except OSError:
    FONT_SM  = ImageFont.load_default()
    FONT_MD  = ImageFont.load_default()
    FONT_LG  = ImageFont.load_default()
    FONT_XL  = ImageFont.load_default()

# ── Colour palette ────────────────────────────────────────────────────────────
C_BG        = (10,  22,  40)    # dark navy
C_BAR       = (16,  63,  45)    # dark green top/bottom bars
C_WHITE     = (255, 255, 255)
C_YELLOW    = (251, 191,  36)
C_GREEN     = (34,  197,  94)
C_RED       = (239,  68,  68)
C_BLUE      = (59,  130, 246)
C_GREY      = (120, 120, 120)
C_ORANGE    = (249, 115,  22)

# ── Weather icon → emoji-like ASCII (for small display) ───────────────────────
WEATHER_ICONS = {
    "sunny":          "*",
    "partly_cloudy":  "~*",
    "cloudy":         "~~",
    "rainy":          "//",
    "showers":        ":/",
    "thunderstorm":   "!!",
    "snowy":          "**",
}

CROP_ICONS = {
    "rice":    "~", "wheat":   "Y", "maize":   "M",
    "cotton":  "c", "sugarcane":"S", "default": "+"
}

# ── Shared state (updated by background threads) ───────────────────────────────
_state = {
    "crop":            "---",
    "yield_kg":        0.0,
    "irrigation":      "---",
    "fertilizer":      "---",
    "weather_icon":    "~~",
    "weather_temp":    "--",
    "sensors":         {},
    "time_str":        "--:--",
}
_lock = threading.Lock()


# ── Data fetch helpers ─────────────────────────────────────────────────────────
def _fetch_predictions():
    try:
        r    = requests.get(f"{API_BASE}/api/predict/all", timeout=8)
        data = r.json()
        with _lock:
            _state["crop"]       = data.get("crop", "---").title()
            _state["yield_kg"]   = data.get("yield_kg_per_ha", 0.0)
            _state["irrigation"] = data.get("irrigation_need", "---")
            _state["fertilizer"] = data.get("fertilizer", "---")
    except Exception:
        pass


def _fetch_weather():
    try:
        r    = requests.get(f"{API_BASE}/api/weather/current", timeout=8)
        data = r.json()
        with _lock:
            _state["weather_icon"] = WEATHER_ICONS.get(data.get("icon", "cloudy"), "~~")
            _state["weather_temp"] = f"{data.get('temperature', '--')}C"
    except Exception:
        pass


def _read_sensors():
    try:
        if os.path.exists(SENSOR_FILE):
            with open(SENSOR_FILE) as f:
                data = json.load(f)
            with _lock:
                _state["sensors"] = data
    except Exception:
        pass


def _background_ml_loop():
    """Refresh ML predictions + weather every 30 seconds."""
    while True:
        _fetch_predictions()
        _fetch_weather()
        time.sleep(30)


def _background_sensor_loop():
    """Refresh sensor values every 5 seconds."""
    while True:
        _read_sensors()
        _state["time_str"] = datetime.datetime.now().strftime("%H:%M")
        time.sleep(5)


# ── Render frame to device ────────────────────────────────────────────────────
def _render():
    img  = Image.new("RGB", (128, 160), C_BG)
    draw = ImageDraw.Draw(img)

    with _lock:
        crop       = _state["crop"]
        yield_kg   = _state["yield_kg"]
        irrigation = _state["irrigation"]
        w_icon     = _state["weather_icon"]
        w_temp     = _state["weather_temp"]
        time_str   = _state["time_str"]
        sensors    = dict(_state["sensors"])

    # ── TOP BAR (y=0…22) ─────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (128, 22)], fill=C_BAR)
    draw.text((3,  4), time_str,       font=FONT_MD, fill=C_WHITE)
    draw.text((55, 4), w_icon,         font=FONT_MD, fill=C_YELLOW)
    draw.text((80, 4), w_temp,         font=FONT_SM, fill=C_GREY)

    # ── CROP SECTION (y=25…65) ───────────────────────────────────────────────
    draw.text((4, 26), "Best Crop",    font=FONT_SM, fill=C_GREY)
    crop_icon = CROP_ICONS.get(crop.lower(), CROP_ICONS["default"])
    draw.text((4, 37), f"{crop_icon} {crop}", font=FONT_LG, fill=C_GREEN)

    # ── YIELD SECTION (y=66…90) ──────────────────────────────────────────────
    draw.line([(4, 65), (124, 65)], fill=C_BAR, width=1)
    draw.text((4, 67), "Exp. Yield",  font=FONT_SM, fill=C_GREY)
    # Convert kg/ha → t/acre  (1 t/ha ≈ 0.405 t/acre)
    t_per_acre = yield_kg / 1000 * 0.405 if yield_kg else 0.0
    draw.text((4, 77), f"{t_per_acre:.2f} t/acre", font=FONT_MD, fill=C_YELLOW)

    # ── IRRIGATION SECTION (y=95…130) ────────────────────────────────────────
    draw.line([(4, 93), (124, 93)], fill=C_BAR, width=1)
    draw.text((4, 95), "Irrigation",  font=FONT_SM, fill=C_GREY)

    irr_color = C_BLUE if irrigation in ("Low", "---") else (
                C_ORANGE if irrigation == "Medium" else C_RED)
    irr_label = irrigation if irrigation != "---" else "Unknown"
    # Draw a simple drop shape using an ellipse
    draw.ellipse([(10, 108), (30, 128)], fill=irr_color)
    draw.text(  (36, 112), irr_label,  font=FONT_MD, fill=irr_color)

    # ── SENSOR MINI-STRIP (y=134…160) ────────────────────────────────────────
    draw.rectangle([(0, 132), (128, 160)], fill=C_BAR)
    air_t = sensors.get("air_temp");        at = f"{air_t:.0f}C" if air_t else "--"
    air_h = sensors.get("air_humidity");    ah = f"{air_h:.0f}%" if air_h else "--"
    s_moi = sensors.get("soil_moisture");   sm = f"{s_moi:.0f}%M" if s_moi else "--"
    s_ph  = sensors.get("soil_ph");         sp = f"pH{s_ph:.1f}" if s_ph else "--"
    draw.text((2,  135), f"T:{at} H:{ah}", font=FONT_SM, fill=C_WHITE)
    draw.text((2,  148), f"{sm}  {sp}",   font=FONT_SM, fill=C_WHITE)

    device.display(img)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[TFT] Starting KrishiMitra TFT display driver...")

    # Initial data pull before starting
    _fetch_predictions()
    _fetch_weather()
    _read_sensors()

    # Background threads
    t1 = threading.Thread(target=_background_ml_loop,    daemon=True)
    t2 = threading.Thread(target=_background_sensor_loop, daemon=True)
    t1.start(); t2.start()

    try:
        while True:
            _state["time_str"] = datetime.datetime.now().strftime("%H:%M")
            _render()
            time.sleep(5)   # re-render every 5s
    except KeyboardInterrupt:
        print("\n[TFT] Display stopped.")
        device.hide()
