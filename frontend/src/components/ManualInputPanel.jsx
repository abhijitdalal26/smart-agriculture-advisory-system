// ManualInputPanel — NPK/soil color + crop/state dropdowns
import { useState, useEffect } from 'react';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || "";

const SOIL_COLORS = [
  { name: 'Black Soil', color: '#1a0a00', npk: { N: 80, P: 40, K: 40 } },
  { name: 'Red Soil',   color: '#8b2500', npk: { N: 20, P: 15, K: 35 } },
  { name: 'Alluvial',   color: '#c8a96e', npk: { N: 60, P: 45, K: 80 } },
  { name: 'Sandy Soil', color: '#d4b483', npk: { N: 15, P: 10, K: 20 } },
  { name: 'Clay Soil',  color: '#7a5c3a', npk: { N: 50, P: 35, K: 45 } },
];

const SOIL_TYPES   = ['Loamy', 'Red', 'Sandy', 'Clay', 'Silt', 'Loam'];
const CROP_TYPES   = ['Wheat', 'Rice', 'Maize', 'Cotton', 'Sugarcane', 'Ground Nuts', 'Barley', 'Pulses', 'Millets', 'Oilseeds'];
const INDIAN_STATES = [
  'Maharashtra', 'Punjab', 'Haryana', 'Uttar Pradesh', 'Madhya Pradesh',
  'Rajasthan', 'Gujarat', 'Andhra Pradesh', 'Karnataka', 'Tamil Nadu',
  'West Bengal', 'Bihar', 'Odisha', 'Telangana', 'Chhattisgarh',
  'Jharkhand', 'Himachal Pradesh', 'Uttarakhand', 'Assam', 'Kerala',
];

export default function ManualInputPanel({ onSubmit }) {
  const [npkMode, setNpkMode]     = useState('color');  // 'color' | 'manual'
  const [soilColor, setSoilColor] = useState(null);
  const [N, setN] = useState(40); const [P, setP] = useState(30); const [K, setK] = useState(40);
  const [soilType, setSoilType]   = useState('Loamy');
  const [cropType, setCropType]   = useState('Wheat');
  const [state, setState]         = useState('Maharashtra');
  const [area, setArea]           = useState(1.0);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess]     = useState(false);

  // Auto-detect state via IP geolocation on mount
  useEffect(() => {
    axios.get(`${API}/api/weather/location`, { timeout: 5000 })
      .then(r => { if (r.data?.state) setState(r.data.state); })
      .catch(() => {});
  }, []);

  // When soil color chosen, auto-fill NPK
  const selectColor = (sc) => {
    setSoilColor(sc.name);
    if (npkMode === 'color') { setN(sc.npk.N); setP(sc.npk.P); setK(sc.npk.K); }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    const payload = {
      nitrogen:    npkMode === 'manual' ? N    : (SOIL_COLORS.find(s => s.name === soilColor)?.npk.N ?? N),
      phosphorous: npkMode === 'manual' ? P    : (SOIL_COLORS.find(s => s.name === soilColor)?.npk.P ?? P),
      potassium:   npkMode === 'manual' ? K    : (SOIL_COLORS.find(s => s.name === soilColor)?.npk.K ?? K),
      soil_color:  soilColor,
      soil_type:   soilType,
      crop_type:   cropType,
      state,
      area,
    };
    try {
      await axios.post(`${API}/api/sensors/manual`, payload, { timeout: 5000 });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      if (onSubmit) onSubmit();
    } catch (_) {}
    finally { setSubmitting(false); }
  };

  return (
    <div className="card input-card input-row">
      <div className="card-title">🧪 Manual Input — Field Parameters</div>

      {/* NPK Mode Toggle */}
      <div className="npk-mode-toggle">
        <button className={`npk-mode-btn ${npkMode === 'color' ? 'active' : ''}`} onClick={() => setNpkMode('color')}>
          🎨 Soil Color
        </button>
        <button className={`npk-mode-btn ${npkMode === 'manual' ? 'active' : ''}`} onClick={() => setNpkMode('manual')}>
          🔢 Manual NPK
        </button>
      </div>

      {/* Soil Color Picker */}
      {npkMode === 'color' && (
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600 }}>
            Select your soil color — NPK will be auto-filled
          </div>
          <div className="soil-color-grid">
            {SOIL_COLORS.map(sc => (
              <button
                key={sc.name}
                className={`soil-color-btn ${soilColor === sc.name ? 'selected' : ''}`}
                style={{ background: sc.color }}
                onClick={() => selectColor(sc)}
                title={sc.name}
              >
                {sc.name.split(' ')[0]}
              </button>
            ))}
          </div>
          {soilColor && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              {soilColor} → N:{SOIL_COLORS.find(s=>s.name===soilColor)?.npk.N} &nbsp;
              P:{SOIL_COLORS.find(s=>s.name===soilColor)?.npk.P} &nbsp;
              K:{SOIL_COLORS.find(s=>s.name===soilColor)?.npk.K}
            </div>
          )}
        </div>
      )}

      {/* Manual NPK */}
      {npkMode === 'manual' && (
        <div className="input-grid" style={{ marginBottom: '1rem' }}>
          {[['N (Nitrogen)', N, setN], ['P (Phosphorous)', P, setP], ['K (Potassium)', K, setK]].map(([lbl, val, setter]) => (
            <div className="input-group" key={lbl}>
              <label>{lbl}</label>
              <input type="number" value={val} min={0} max={140}
                onChange={e => setter(+e.target.value)} />
            </div>
          ))}
        </div>
      )}

      {/* Other inputs */}
      <div className="input-grid">
        <div className="input-group">
          <label>Soil Type</label>
          <select value={soilType} onChange={e => setSoilType(e.target.value)}>
            {SOIL_TYPES.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="input-group">
          <label>Crop Type</label>
          <select value={cropType} onChange={e => setCropType(e.target.value)}>
            {CROP_TYPES.map(c => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div className="input-group">
          <label>State (auto-detected)</label>
          <select value={state} onChange={e => setState(e.target.value)}>
            {INDIAN_STATES.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="input-group">
          <label>Farm Area (hectares)</label>
          <input type="number" value={area} min={0.1} step={0.1}
            onChange={e => setArea(+e.target.value)} />
        </div>
      </div>

      <button className="submit-btn" onClick={handleSubmit} disabled={submitting}>
        {submitting ? '⟳ Updating…' : success ? '✅ Updated!' : '🔄 Run Predictions'}
      </button>
    </div>
  );
}
