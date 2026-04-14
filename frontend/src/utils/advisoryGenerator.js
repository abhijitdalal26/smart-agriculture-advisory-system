// NLG Advisory Generator
// Converts sensor data + ML prediction results into human-readable sentences

const PH_STATUS = (ph) => {
  if (ph < 5.5) return { label: 'very acidic', action: 'Apply lime (2–3 t/ha) before the next planting season.' };
  if (ph < 6.0) return { label: 'slightly acidic', action: 'Consider applying lime before the next rain.' };
  if (ph > 8.0) return { label: 'alkaline', action: 'Add sulfur or acidifying fertilizers to lower pH.' };
  if (ph > 7.5) return { label: 'mildly alkaline', action: 'Monitor pH trend and consider acidifying irrigation.' };
  return { label: 'optimal', action: 'Maintain current soil management practices.' };
};

const MOISTURE_STATUS = (m) => {
  if (m < 20) return { level: 'critically low', action: 'Irrigate immediately to prevent crop stress.', severity: 'critical' };
  if (m < 35) return { level: 'low', action: 'Schedule irrigation within 24 hours.', severity: 'warning' };
  if (m > 85) return { level: 'excessive', action: 'Hold irrigation — risk of root rot and nutrient leaching.', severity: 'warning' };
  return { level: 'adequate', action: 'No immediate irrigation needed.', severity: 'ok' };
};

const CROP_ICONS = {
  rice: '🌾', wheat: '🌾', maize: '🌽', corn: '🌽', cotton: '🪴',
  sugarcane: '🌿', potato: '🥔', tomato: '🍅', onion: '🧅',
  default: '🌱',
};

export function generateAdvisory(sensors, predictions) {
  if (!sensors && !predictions) return [];
  const messages = [];

  // ── Crop recommendation ───────────────────────────────────────────────────
  if (predictions?.crop) {
    const icon = CROP_ICONS[predictions.crop.toLowerCase()] || CROP_ICONS.default;
    messages.push({
      icon, severity: 'ok',
      text: `Based on current soil and weather conditions, ${icon} ${predictions.crop} is the recommended crop for this season.`,
    });
  }

  // ── Yield forecast ────────────────────────────────────────────────────────
  if (predictions?.yield_kg_per_ha) {
    const tPerAcre = (predictions.yield_kg_per_ha / 1000 * 0.405).toFixed(2);
    messages.push({
      icon: '📊', severity: 'ok',
      text: `Expected yield forecast is ${tPerAcre} tonnes/acre for ${predictions.season || 'this'} season.`,
    });
  }

  // ── Irrigation ───────────────────────────────────────────────────────────
  if (predictions?.irrigation_need) {
    const irr = predictions.irrigation_need;
    const map = {
      Low:    { icon: '💧', text: 'Irrigation need is LOW — soil moisture is adequate. No action required.', severity: 'ok' },
      Medium: { icon: '🚿', text: 'Irrigation need is MEDIUM — consider irrigating within the next 1–2 days.', severity: 'warning' },
      High:   { icon: '🔴', text: 'Irrigation need is HIGH — irrigate promptly to prevent yield loss.', severity: 'critical' },
    };
    if (map[irr]) messages.push(map[irr]);
  }

  // ── Fertilizer ────────────────────────────────────────────────────────────
  if (predictions?.fertilizer) {
    messages.push({
      icon: '🧪', severity: 'ok',
      text: `Recommended fertilizer: ${predictions.fertilizer}. Apply as per standard dosage for your selected crop.`,
    });
  }

  // ── Soil pH ───────────────────────────────────────────────────────────────
  if (sensors?.soil_ph != null) {
    const ph = sensors.soil_ph;
    const { label, action } = PH_STATUS(ph);
    const sev = (ph < 5.5 || ph > 8.0) ? 'warning' : 'ok';
    messages.push({
      icon: '⚗️', severity: sev,
      text: `Soil pH is ${ph.toFixed(1)} (${label}). ${action}`,
    });
  }

  // ── Soil moisture ─────────────────────────────────────────────────────────
  if (sensors?.soil_moisture != null) {
    const { level, action, severity } = MOISTURE_STATUS(sensors.soil_moisture);
    messages.push({
      icon: severity === 'critical' ? '🚨' : severity === 'warning' ? '⚠️' : '✅',
      severity,
      text: `Soil moisture is ${level} at ${sensors.soil_moisture.toFixed(1)}%. ${action}`,
    });
  }

  // ── Temperature warnings ──────────────────────────────────────────────────
  if (sensors?.air_temp != null) {
    if (sensors.air_temp > 40) {
      messages.push({
        icon: '🌡️', severity: 'critical',
        text: `Air temperature is extremely high at ${sensors.air_temp.toFixed(1)}°C. Provide shade netting and increase irrigation frequency.`,
      });
    } else if (sensors.air_temp < 10) {
      messages.push({
        icon: '❄️', severity: 'critical',
        text: `Temperature is critically low at ${sensors.air_temp.toFixed(1)}°C. Protect frost-sensitive crops immediately.`,
      });
    }
  }

  // ── Light check ───────────────────────────────────────────────────────────
  if (sensors?.light_lux != null && sensors.light_lux < 200) {
    messages.push({
      icon: '☁️', severity: 'warning',
      text: `Light intensity is low (${sensors.light_lux.toFixed(0)} Lux). Extended overcast conditions may reduce photosynthesis and crop growth.`,
    });
  }

  return messages.length > 0 ? messages : [{
    icon: '✅', severity: 'ok',
    text: 'All systems normal. Crop conditions are healthy — no immediate action required.',
  }];
}
