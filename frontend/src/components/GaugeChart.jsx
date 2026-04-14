// GaugeChart — Radial gauge using Recharts RadialBarChart
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts';

export default function GaugeChart({ label, value, min = 0, max = 100, color = '#22c55e', unit = '%', icon }) {
  const pct    = value != null ? Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100)) : 0;
  const data   = [{ value: pct, fill: color }];

  return (
    <div className="card gauge-card">
      <div className="card-title gauge-title">{icon && `${icon} `}{label}</div>
      <div className="gauge-wrap">
        {value == null ? (
          <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100%',color:'var(--text-muted)'}}>
            --
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%" cy="70%"
              innerRadius="60%" outerRadius="90%"
              startAngle={180} endAngle={0}
              data={data}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
              <RadialBar
                dataKey="value" cornerRadius={6}
                background={{ fill: 'rgba(255,255,255,0.05)' }}
              />
              {/* Center label */}
              <text x="50%" y="65%" textAnchor="middle"
                    style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>
                <tspan style={{ fontSize: '1.4rem', fill: color }}>
                  {typeof value === 'number' ? value.toFixed(1) : value}
                </tspan>
                <tspan style={{ fontSize: '0.8rem', fill: '#94a3b8' }}>{unit}</tspan>
              </text>
              <text x="50%" y="80%" textAnchor="middle"
                    fill="#4a5568" style={{ fontSize: '0.65rem' }}>
                {min}{unit} — {max}{unit}
              </text>
            </RadialBarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
