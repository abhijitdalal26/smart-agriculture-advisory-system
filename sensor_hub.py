"""
KrishiMitra — Sensor Hub Daemon
Reads all physical sensors and:
  1. Writes latest data to sensors.json (shared state for FastAPI)
  2. Posts readings to FastAPI /api/sensors/update every loop
  3. Drives 16×2 LCD in a 5-second two-screen cycle:
       Screen 1 (5s): Air Temp + Humidity | Light Lux
       Screen 2 (5s): Soil Temp + Moisture | pH + status
  4. Persists history to SQLite via the API

Hardware:
  - DHT22 Air Temp/Humidity      → GPIO Pin 17
  - BH1750 Light Sensor (I2C)    → 0x23
  - DS18B20 Soil Temp (1-Wire)   → /sys/bus/w1/devices/28*
  - Arduino Nano (Serial)        → /dev/ttyACM0  (sends "moisture,ph\n")
  - LCD 16×2 (I2C PCF8574)       → 0x27
"""

import json
import os
import glob
import time
import threading
import requests

import smbus
import adafruit_dht
import board
import serial
from RPLCD.i2c import CharLCD

# ── Force Raspberry Pi 4B for Blinka ────────────────────────────────────────
os.environ["BLINKA_FORCEBOARD"] = "RASPBERRY_PI_4B"

# ── Configuration ────────────────────────────────────────────────────────────
API_BASE       = "http://localhost:8000"
SENSOR_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensors.json")
LCD_CYCLE_SEC  = 5       # seconds per LCD screen
LOOP_SLEEP     = 2       # main loop delay (seconds)

# ── LCD Init ─────────────────────────────────────────────────────────────────
time.sleep(2)
lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
lcd.clear()

# ── BH1750 Light Sensor (I2C) ────────────────────────────────────────────────
bus        = smbus.SMBus(1)
light_addr = 0x23

def read_light() -> float:
    try:
        data = bus.read_i2c_block_data(light_addr, 0x20)
        return (data[0] << 8 | data[1]) / 1.2
    except Exception:
        return 0.0

# ── DHT22 (Air Temp + Humidity) ───────────────────────────────────────────────
dht       = adafruit_dht.DHT22(board.D17, use_pulseio=False)
last_temp = 0.0
last_hum  = 0.0

# ── DS18B20 (Soil Temperature, 1-Wire) ───────────────────────────────────────
_base_dir     = '/sys/bus/w1/devices/'

def _get_ds18b20_file():
    folders = glob.glob(_base_dir + '28*')
    if folders:
        return folders[0] + '/w1_slave'
    return None

_device_file = _get_ds18b20_file()

def read_soil_temp() -> float | None:
    global _device_file
    if not _device_file:
        _device_file = _get_ds18b20_file()
        if not _device_file:
            return None
    try:
        with open(_device_file, 'r') as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] != 'YES':
            return None
        pos = lines[1].find('t=')
        if pos != -1:
            return float(lines[1][pos + 2:]) / 1000.0
    except Exception:
        return None

# ── Arduino Serial (Soil Moisture % + pH) ────────────────────────────────────
def connect_serial():
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)
        ser.flushInput()
        print("Arduino Connected ✅")
        return ser
    except Exception as e:
        print("Arduino NOT Connected ❌", e)
        return None

ser      = connect_serial()
moisture = None
ph       = None

# ── LCD display state ─────────────────────────────────────────────────────────
_lcd_screen    = 0   # 0=ambient, 1=soil
_lcd_last_flip = time.time()
_lcd_lock      = threading.Lock()

def _ph_status(ph_val: float) -> str:
    if ph_val < 6.0:   return "Acid"
    if ph_val > 7.5:   return "Alk"
    return "Stbl"

def _update_lcd(air_t, air_h, light, soil_t, soil_m, soil_p):
    """Update 16×2 LCD — cycles between two screens every LCD_CYCLE_SEC."""
    global _lcd_screen, _lcd_last_flip

    now = time.time()
    if now - _lcd_last_flip >= LCD_CYCLE_SEC:
        _lcd_screen    = 1 - _lcd_screen
        _lcd_last_flip = now

    try:
        with _lcd_lock:
            lcd.clear()
            if _lcd_screen == 0:
                # Screen 1 — Ambient Environment
                # Line 1: "Air: 25°C 60%H"   (max 16 chars)
                line1 = f"Air:{int(air_t)}\xdfC {int(air_h)}%H"
                # Line 2: "Light: 1200 Lux"
                lux_str = f"{int(light)}"
                line2 = f"Light:{lux_str} Lux"
            else:
                # Screen 2 — Soil Health
                # Line 1: "Soil: 22°C 45%M"
                st_str = f"{int(soil_t)}\xdfC" if soil_t is not None else "Err"
                sm_str = f"{int(soil_m)}%" if soil_m is not None else "--"
                line1  = f"Soil:{st_str} {sm_str}M"
                # Line 2: "pH: 6.5 [Stable]"
                if soil_p is not None:
                    line2 = f"pH:{soil_p:.1f} [{_ph_status(soil_p)}]"
                else:
                    line2 = "pH: ---"

            lcd.write_string(line1[:16])
            lcd.crlf()
            lcd.write_string(line2[:16])
    except Exception as e:
        print(f"[LCD] Error: {e}")


# ── Shared state writer ───────────────────────────────────────────────────────
def _write_sensors_json(data: dict):
    try:
        with open(SENSOR_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"[sensor_hub] sensors.json write error: {e}")


def _post_to_api(data: dict):
    """Non-blocking POST to FastAPI; silently ignores connection errors."""
    payload = {k: v for k, v in data.items()
               if k in ("air_temp","air_humidity","soil_temp","soil_moisture","soil_ph","light_lux")}
    try:
        requests.post(f"{API_BASE}/api/sensors/update", json=payload, timeout=2)
    except Exception:
        pass   # API not up yet — write to file, sensor_store will pick it up


# ── Main Loop ─────────────────────────────────────────────────────────────────
print("[KrishiMitra] Sensor Hub starting...")

try:
    while True:
        # ── Read PI sensors ──────────────────────────────────────────────────
        light     = read_light()
        soil_temp = read_soil_temp()

        try:
            t = dht.temperature
            h = dht.humidity
            if t is not None and h is not None:
                last_temp = t
                last_hum  = h
        except Exception:
            pass

        # ── Read Arduino serial ──────────────────────────────────────────────
        if ser:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line and "," in line:
                    parts = line.split(",")
                    if len(parts) >= 2:
                        moisture = float(parts[0])
                        ph       = float(parts[1])
            except Exception:
                print("[sensor_hub] Serial error → reconnecting...")
                try:   ser.close()
                except Exception: pass
                time.sleep(2)
                ser = connect_serial()
        else:
            # Try to connect if it wasn't available at startup
            ser = connect_serial()

        # ── Build payload ────────────────────────────────────────────────────
        sensor_data = {
            "air_temp":      round(last_temp, 1),
            "air_humidity":  round(last_hum, 1),
            "soil_temp":     round(soil_temp, 1) if soil_temp is not None else None,
            "soil_moisture": round(moisture, 1)  if moisture  is not None else None,
            "soil_ph":       round(ph, 2)        if ph        is not None else None,
            "light_lux":     round(light, 1),
        }

        # ── Write / push ─────────────────────────────────────────────────────
        _write_sensors_json(sensor_data)
        _post_to_api(sensor_data)

        # ── Update LCD ───────────────────────────────────────────────────────
        _update_lcd(
            air_t  = last_temp,
            air_h  = last_hum,
            light  = light,
            soil_t = soil_temp,
            soil_m = moisture,
            soil_p = ph,
        )

        # ── Console log ──────────────────────────────────────────────────────
        print(
            f"Air:{last_temp:.1f}°C {last_hum:.1f}%  "
            f"Soil:{soil_temp:.1f}°C  Light:{light:.0f}Lx  "
            f"Mois:{moisture:.1f}%  pH:{ph:.2f}"
            if (soil_temp and moisture and ph)
            else f"Air:{last_temp:.1f}°C  Light:{light:.0f}Lx  (waiting for sensors...)"
        )

        time.sleep(LOOP_SLEEP)

except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string("KrishiMitra")
    lcd.crlf()
    lcd.write_string("Halted safely")
    print("\n[sensor_hub] Stopped safely.")
