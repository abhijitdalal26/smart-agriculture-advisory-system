// PredictiveHub — displays all 4 ML model results
export default function PredictiveHub({ data, loading }) {
  const CROP_ICONS = {
    rice: '🌾', wheat: '🌾', maize: '🌽', corn: '🌽',
    cotton: '🪴', sugarcane: '🌿', potato: '🥔', tomato: '🍅',
    default: '🌱',
  };

  const irrClass = (irr) => {
    if (!irr) return 'irr-low';
    const map = { Low: 'irr-low', Medium: 'irr-medium', High: 'irr-high' };
    return map[irr] || 'irr-low';
  };

  const cropIcon = data?.crop
    ? (CROP_ICONS[data.crop.toLowerCase()] || CROP_ICONS.default)
    : '🌱';

  const yieldTonAcre = data?.yield_kg_per_ha
    ? (data.yield_kg_per_ha / 1000 * 0.405).toFixed(2)
    : null;

  return (
    <div className="card predict-hub predict-panel">
      <div className="ph-header">
        <h2>🧠 Predictive Insights</h2>
        {loading && <span className="refresh-indicator"><span className="refresh-spin">⟳</span> Updating…</span>}
      </div>

      <div className="ph-grid">
        {/* Crop */}
        <div className="ph-item crop">
          <div className="ph-label">🌱 Best Crop</div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">{cropIcon} {data?.crop?.charAt(0).toUpperCase() + data?.crop?.slice(1) || '---'}</div>
          }
          {data?.inputs?.state && <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>State: {data.inputs.state}</div>}
        </div>

        {/* Yield */}
        <div className="ph-item yield">
          <div className="ph-label">📊 Expected Yield</div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">{yieldTonAcre ? `${yieldTonAcre} t/acre` : '---'}</div>
          }
          {data?.season && <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>{data.season} Season</div>}
        </div>

        {/* Irrigation */}
        <div className={`ph-item ${irrClass(data?.irrigation_need)}`}>
          <div className="ph-label">💧 Irrigation Need</div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">
                {data?.irrigation_need === 'High'  ? '🔴 ' : data?.irrigation_need === 'Medium' ? '🟡 ' : '🔵 '}
                {data?.irrigation_need || '---'}
              </div>
          }
          {data?.rainfall_mm != null && (
            <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>
              Recent rain: {data.rainfall_mm} mm
            </div>
          )}
        </div>

        {/* Fertilizer */}
        <div className="ph-item fert">
          <div className="ph-label">🧪 Fertilizer</div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">{data?.fertilizer || '---'}</div>
          }
          {data?.inputs && (
            <div style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>
              N:{data.inputs.N} P:{data.inputs.P} K:{data.inputs.K}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
