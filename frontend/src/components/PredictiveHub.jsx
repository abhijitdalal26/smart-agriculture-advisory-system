import { Sprout, BarChart2, CloudRain, Beaker } from 'lucide-react';

export default function PredictiveHub({ data, loading }) {
  const irrClass = (irr) => {
    if (!irr) return 'irr-low';
    const map = { Low: 'irr-low', Medium: 'irr-medium', High: 'irr-high' };
    return map[irr] || 'irr-low';
  };

  const yieldTonAcre = data?.yield_kg_per_ha
    ? (data.yield_kg_per_ha / 1000 * 0.405).toFixed(2)
    : null;

  return (
    <div className="predict-hub predict-panel">
      
      <div className="ph-grid">
        {/* Crop */}
        <div className="ph-item crop">
          <div className="ph-label">
            <div className="ph-label-left">
              <Sprout size={16} /> Best Crop
            </div>
          </div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">{data?.crop?.charAt(0).toUpperCase() + data?.crop?.slice(1) || '---'}</div>
          }
          {data?.inputs?.state && <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>State: {data.inputs.state}</div>}
        </div>

        {/* Yield */}
        <div className="ph-item yield">
          <div className="ph-label">
            <div className="ph-label-left">
              <BarChart2 size={16} /> Expected Yield
            </div>
            <span className="ai-badge">AI</span>
          </div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">{yieldTonAcre ? `${yieldTonAcre} t/acre` : '---'}</div>
          }
          {data?.season && <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>{data.season} Season</div>}
        </div>

        {/* Irrigation */}
        <div className={`ph-item ${irrClass(data?.irrigation_need)}`}>
          <div className="ph-label">
            <div className="ph-label-left">
              <CloudRain size={16} /> Irrigation Need
            </div>
            <span className="ai-badge">AI</span>
          </div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">
                {data?.irrigation_need || '---'}
              </div>
          }
          {data?.rainfall_mm != null && (
            <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>
              Recent rain: {data.rainfall_mm} mm
            </div>
          )}
        </div>

        {/* Fertilizer */}
        <div className="ph-item fert">
          <div className="ph-label">
            <div className="ph-label-left">
              <Beaker size={16} /> Fertilizer
            </div>
            <span className="ai-badge">AI</span>
          </div>
          {loading && !data
            ? <div className="loading-shimmer" />
            : <div className="ph-value">{data?.fertilizer || '---'}</div>
          }
          {data?.inputs && (
            <div style={{fontSize:'0.75rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>
              N:{data.inputs.N} P:{data.inputs.P} K:{data.inputs.K}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
