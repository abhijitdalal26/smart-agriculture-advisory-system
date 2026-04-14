import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "";

const SEV_ORDER = { critical: 0, warning: 1, info: 2 };

export default function AlertBanner() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get(`${API}/api/alerts`, { timeout: 4000 });
        setAlerts(res.data.alerts || []);
      } catch (_) {}
    };
    fetch();
    const id = setInterval(fetch, 10000);
    return () => clearInterval(id);
  }, []);

  if (alerts.length === 0) return null;

  const sorted   = [...alerts].sort((a, b) => SEV_ORDER[a.severity] - SEV_ORDER[b.severity]);
  const topSev   = sorted[0]?.severity || 'info';

  const renderIcon = () => {
    switch(topSev) {
      case 'critical': return <AlertCircle size={24} />;
      case 'warning': return <AlertTriangle size={24} />;
      default: return <Info size={24} />;
    }
  }

  return (
    <div className={`alert-banner ${topSev}`}>
      <span className="alert-icon">{renderIcon()}</span>
      <div className="alert-list">
        {sorted.map(a => (
          <div key={a.id} className="alert-item">
            {a.message}
          </div>
        ))}
      </div>
    </div>
  );
}
