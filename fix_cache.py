import json
with open('/home/ess/.openclaw/workspace/smart-agriculture-advisory-system/sensors.json', 'r+') as f:
    d = json.load(f)
    d['soil_ph'] = None
    d['soil_moisture'] = None
    f.seek(0)
    json.dump(d, f)
    f.truncate()
