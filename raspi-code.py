import time
import smbus
import adafruit_dht
import board
import os
import glob
import serial
from RPLCD.i2c import CharLCD

# Force Raspberry Pi 4
os.environ["BLINKA_FORCEBOARD"] = "RASPBERRY_PI_4B"

# ----------- LCD INIT -----------
time.sleep(2)
lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
lcd.clear()

# ----------- BH1750 -----------
bus = smbus.SMBus(1)
light_addr = 0x23

def read_light():
    try:
        data = bus.read_i2c_block_data(light_addr, 0x20)
        return (data[0] << 8 | data[1]) / 1.2
    except:
        return 0.0

# ----------- DHT22 -----------
dht = adafruit_dht.DHT22(board.D17, use_pulseio=False)
last_temp = 0.0
last_hum = 0.0

# ----------- DS18B20 -----------
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')
device_file = device_folder[0] + '/w1_slave' if device_folder else None

def read_soil_temp():
    if not device_file:
        return None
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()

        if lines[0].strip()[-3:] != 'YES':
            return None

        temp_pos = lines[1].find('t=')
        if temp_pos != -1:
            return float(lines[1][temp_pos+2:]) / 1000.0
    except:
        return None

# ----------- ARDUINO SERIAL -----------
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

ser = connect_serial()

moisture = None
ph = None

# ----------- MAIN LOOP -----------
try:
    while True:

        # ----- READ PI SENSORS -----
        light = read_light()
        soil_temp = read_soil_temp()

        try:
            temp = dht.temperature
            hum = dht.humidity

            if temp is not None and hum is not None:
                last_temp = temp
                last_hum = hum
        except:
            pass

        # ----- READ ARDUINO -----
        if ser:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                if line and "," in line:
                    m, p = line.split(",")
                    moisture = float(m)
                    ph = float(p)

            except:
                print("Serial error → reconnecting...")
                try:
                    ser.close()
                except:
                    pass
                time.sleep(2)
                ser = connect_serial()

        # -------- LCD DISPLAY --------
        try:
            lcd.clear()

            # Line 1
            lcd.write_string(
                f"T:{int(last_temp)}{chr(223)}C H:{int(last_hum)}%"
            )

            lcd.crlf()

            # Line 2 (with units)
            if soil_temp is not None:
                lcd.write_string(
                    f"S:{int(soil_temp)}C L:{light:.1f}Lx"
                )
            else:
                lcd.write_string(
                    f"S:Err L:{light:.1f}Lx"
                )

        except Exception as e:
            print("LCD Error:", e)

        # -------- CMD OUTPUT --------
        print(f"T:{last_temp:.1f} °C  H:{last_hum:.1f} %")

        if soil_temp is not None:
            print(f"Soil:{soil_temp:.1f} °C  Light:{light:.1f} Lx")
        else:
            print(f"Soil:Error  Light:{light:.1f} Lx")

        if moisture is not None and ph is not None:
            print(f"Moisture:{moisture:.1f} %  pH:{ph:.2f}")
        else:
            print("Moisture:--  pH:--")

        print("----------------------------")

        time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string("Stopped")
    print("Program stopped safely")