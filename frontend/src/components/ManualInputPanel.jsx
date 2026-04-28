// ManualInputPanel — NPK/soil color + crop/state dropdowns
// Persists values: loads from backend on mount, saves to localStorage as backup
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Palette, Baseline, RefreshCw, CheckCircle2 } from 'lucide-react';

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

const LS_KEY = 'krishimitra_manual_inputs';

function loadFromLocalStorage() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function saveToLocalStorage(data) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(data)); } catch {}
}

export default function ManualInputPanel({ onSubmit }) {
  const [npkMode,    setNpkMode]    = useState('color');
  const [soilColor,  setSoilColor]  = useState(null);
  const [N, setN] = useState(40);
  const [P, setP] = useState(30);
  const [K, setK] = useState(40);
  const [soilType,   setSoilType]   = useState('Loamy');
  const [cropType,   setCropType]   = useState('Wheat');
  const [state,      setState]      = useState('Maharashtra');
  const [area,       setArea]       = useState(1.0);
  const [submitting, setSubmitting] = useState(false);
  const [success,    setSuccess]    = useState(false);
  const [loaded,     setLoaded]     = useState(false);

  // On mount: load saved values from backend first, fallback to localStorage
  useEffect(() => {
    const applyValues = (d) => {
      if (!d) return;
      if (d.manual_nitrogen    != null) { setN(d.manual_nitrogen);    setNpkMode('manual'); }
      if (d.manual_phosphorous != null)   setP(d.manual_phosphorous);
      if (d.manual_potassium   != null)   setK(d.manual_potassium);
      if (d.manual_soil_color  != null) { setSoilColor(d.manual_soil_color); setNpkMode('color'); }
      if (d.manual_soil_type   != null)   setSoilType(d.manual_soil_type);
      if (d.manual_crop_type   != null)   setCropType(d.manual_crop_type);
      if (d.manual_state       != null)   setState(d.manual_state);
      if (d.manual_area        != null)   setArea(d.manual_area);
    };

    // 1. Try backend (source of truth)
    axios.get(`${API}/api/sensors/latest`, { timeout: 5000 })
      .then(r => {
        const d = r.data;
        const hasManual = d.manual_nitrogen != null || d.manual_soil_color != null;
        if (hasManual) {
          applyValues(d);
          saveToLocalStorage(d); // keep localStorage in sync
        } else {
          // 2. Fallback to localStorage if backend has no manual overrides yet
          const ls = loadFromLocalStorage();
          if (ls) applyValues(ls);
          else {
            // 3. Final fallback: auto-detect state from IP
            axios.get(`${API}/api/weather/location`, { timeout: 5000 })
              .then(r2 => { if (r2.data?.state) setState(r2.data.state); })
              .catch(() => {});
          }
        }
        setLoaded(true);
      })
      .catch(() => {
        const ls = loadFromLocalStorage();
        if (ls) applyValues(ls);
        setLoaded(true);
      });
  }, []);

  const selectColor = (sc) => {
    setSoilColor(sc.name);
    if (npkMode === 'color') { setN(sc.npk.N); setP(sc.npk.P); setK(sc.npk.K); }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    const resolvedN = npkMode === 'manual' ? N : (SOIL_COLORS.find(s => s.name === soilColor)?.npk.N ?? N);
    const resolvedP = npkMode === 'manual' ? P : (SOIL_COLORS.find(s => s.name === soilColor)?.npk.P ?? P);
    const resolvedK = npkMode === 'manual' ? K : (SOIL_COLORS.find(s => s.name === soilColor)?.npk.K ?? K);

    const payload = {
      nitrogen:    resolvedN,
      phosphorous: resolvedP,
      potassium:   resolvedK,
      soil_color:  soilColor,
      soil_type:   soilType,
      crop_type:   cropType,
      state,
      area,
    };

    // Save to localStorage immediately so values survive page refresh
    saveToLocalStorage({
      manual_nitrogen:    resolvedN,
      manual_phosphorous: resolvedP,
      manual_potassium:   resolvedK,
      manual_soil_color:  soilColor,
      manual_soil_type:   soilType,
      manual_crop_type:   cropType,
      manual_state:       state,
      manual_area:        area,
    });

    try {
      await axios.post(`${API}/api/sensors/manual`, payload, { timeout: 5000 });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      if (onSubmit) onSubmit();
    } catch (_) {}
    finally { setSubmitting(false); }
  };

  if (!loaded) return (
    <div className="card input-card input-row" style={{ opacity: 0.6 }}>
      <div className="card-title">🧪 Manual Input — Loading saved values…</div>
    </div>
  );

  return (
    <div className="card input-row">

      {/* NPK Mode Toggle */}
      <div className="npk-mode-toggle">
        <button className={`npk-mode-btn ${npkMode === 'color' ? 'active' : ''}`} onClick={() => setNpkMode('color')}>
           Soil Color
        </button>
        <button className={`npk-mode-btn ${npkMode === 'manual' ? 'active' : ''}`} onClick={() => setNpkMode('manual')}>
           Manual NPK
        </button>
      </div>

      {/* Soil Color Picker */}
      {npkMode === 'color' && (
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 500 }}>
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
              />
            ))}
          </div>
          {soilColor && (
            <div style={{ marginTop: '0.75rem', fontSize: '14px', color: 'var(--text-secondary)' }}>
              Selected: <span style={{fontWeight: 600, color: 'var(--text-primary)'}}>{soilColor}</span> → N:{SOIL_COLORS.find(s=>s.name===soilColor)?.npk.N} &nbsp;
              P:{SOIL_COLORS.find(s=>s.name===soilColor)?.npk.P} &nbsp;
              K:{SOIL_COLORS.find(s=>s.name===soilColor)?.npk.K}
            </div>
          )}
        </div>
      )}

      {/* Manual NPK */}
      {npkMode === 'manual' && (
        <div className="input-grid" style={{ marginBottom: '1.5rem' }}>
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
        {submitting ? (
          <span style={{display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center'}}><RefreshCw size={18} className="refresh-spin" /> Updating...</span>
        ) : success ? (
          <span style={{display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center'}}><CheckCircle2 size={18} /> Updated!</span>
        ) : (
          <span style={{display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center'}}>Run Predictions</span>
        )}
      </button>
    </div>
  );
}
