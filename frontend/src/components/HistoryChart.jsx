import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  ResponsiveContainer, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts';

const API = import.meta.env.VITE_API_URL || "";

const TABS = [
  { key: 'air_temp',      label: 'Air Temp',     color: '#F4A261', unit: '°C' },
  { key: 'air_humidity',  label: 'Humidity',     color: '#3B82F6', unit: '%' },
  { key: 'soil_moisture', label: 'Soil Moisture',color: '#52B788', unit: '%' },
  { key: 'soil_ph',       label: 'Soil pH',      color: '#8B5E3C', unit: '' },
  { key: 'light_lux',     label: 'Light',        color: '#fbbf24', unit: ' Lux' },
];

const CustomTooltip = ({ active, payload, label, unit }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#FFFFFF', border: '1px solid #E5E7EB',
      borderRadius: 8, padding: '0.75rem 1rem', fontSize: '0.85rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{ color: '#6B7280', marginBottom: 4 }}>{label}</div>
      <div style={{ color: payload[0]?.color, fontWeight: 600, fontSize: '1.1rem', fontFamily: 'DM Mono, monospace' }}>
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
    <div className="card history-card history-row" style={{padding: '24px'}}>
      <div className="chart-tabs">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`chart-tab ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => setActiveTab(t.key)}
            style={activeTab === t.key ? { background: t.color } : {}}
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
            <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
              <defs>
                <linearGradient id={`grad_${tab.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={tab.color} stopOpacity={0.15} />
                  <stop offset="95%" stopColor={tab.color} stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} interval="preserveStartEnd" minTickGap={30} />
              <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip unit={tab.unit} />} cursor={{stroke: '#E5E7EB', strokeWidth: 1}} />
              <Area
                type="monotone"
                dataKey={tab.key}
                stroke={tab.color}
                strokeWidth={3}
                fill={`url(#grad_${tab.key})`}
                dot={false}
                activeDot={{ r: 5, strokeWidth: 0, fill: tab.color }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
