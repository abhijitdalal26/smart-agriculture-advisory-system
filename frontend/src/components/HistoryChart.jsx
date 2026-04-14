// HistoryChart — Recharts line/area charts for 24h sensor history
import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  ResponsiveContainer, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const TABS = [
  { key: 'air_temp',      label: 'Air Temp',     color: '#f97316', unit: '°C' },
  { key: 'air_humidity',  label: 'Humidity',     color: '#3b82f6', unit: '%' },
  { key: 'soil_moisture', label: 'Soil Moisture',color: '#22c55e', unit: '%' },
  { key: 'soil_ph',       label: 'Soil pH',      color: '#a78bfa', unit: '' },
  { key: 'light_lux',    label: 'Light',        color: '#fbbf24', unit: ' Lux' },
];

const CustomTooltip = ({ active, payload, label, unit }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#111f36', border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 8, padding: '0.5rem 0.75rem', fontSize: '0.8rem',
    }}>
      <div style={{ color: '#94a3b8', marginBottom: 4 }}>{label}</div>
      <div style={{ color: payload[0]?.color, fontWeight: 600 }}>
        {payload[0]?.value?.toFixed(2)}{unit}
      </div>
    </div>
  );
};

export default function HistoryChart() {
  const [history, setHistory]   = useState([]);
  const [activeTab, setActiveTab] = useState('air_temp');

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get(`${API}/api/sensors/history?limit=48`, { timeout: 5000 });
        const rows = res.data.map(r => ({
          ...r,
          time: new Date(r.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
        }));
        setHistory(rows);
      } catch (_) {}
    };
    fetch();
    const id = setInterval(fetch, 30000);
    return () => clearInterval(id);
  }, []);

  const tab = TABS.find(t => t.key === activeTab) || TABS[0];

  return (
    <div className="card history-card history-row">
      <div className="card-title">📈 Historical Trends (Last 24h)</div>

      <div className="chart-tabs">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`chart-tab ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => setActiveTab(t.key)}
            style={activeTab === t.key ? { background: t.color, borderColor: t.color } : {}}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="chart-wrap">
        {history.length === 0 ? (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100%', color:'var(--text-muted)' }}>
            No historical data yet — readings will appear here after a few minutes.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <defs>
                <linearGradient id={`grad_${tab.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={tab.color} stopOpacity={0.25} />
                  <stop offset="95%" stopColor={tab.color} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748b' }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
              <Tooltip content={<CustomTooltip unit={tab.unit} />} />
              <Area
                type="monotone"
                dataKey={tab.key}
                stroke={tab.color}
                strokeWidth={2}
                fill={`url(#grad_${tab.key})`}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 0 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
