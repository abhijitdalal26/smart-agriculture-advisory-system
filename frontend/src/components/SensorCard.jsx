// SensorCard — animated real-time sensor tile
import { useState, useEffect } from 'react';

export default function SensorCard({ icon, label, value, unit, sub, colorClass, nullText = '--' }) {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    if (value != null) {
      setAnimate(true);
      const t = setTimeout(() => setAnimate(false), 400);
      return () => clearTimeout(t);
    }
  }, [value]);

  const isNull = value == null;

  return (
    <div className={`sensor-card ${colorClass} ${isNull ? 'null-state' : ''}`}
         style={{ transition: 'all 0.2s ease', ...(animate ? { transform: 'scale(1.03)' } : {}) }}>
      <span className="sc-icon">{icon}</span>
      <span className="sc-label">{label}</span>
      <div className="sc-value">
        {isNull ? nullText : (
          <>
            {typeof value === 'number' ? value.toFixed(1) : value}
            {unit && <span className="sc-unit">{unit}</span>}
          </>
        )}
      </div>
      {sub && <span className="sc-sub">{sub}</span>}
    </div>
  );
}
