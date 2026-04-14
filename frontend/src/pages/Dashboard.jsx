import { useState, useEffect } from 'react';
import { useSensorData }  from '../hooks/useSensorData';
import { usePredictions } from '../hooks/usePredictions';
import { 
  Sprout, LayoutDashboard, Cpu, BrainCircuit, CloudSun, 
  LineChart, SlidersHorizontal, Thermometer, Droplets, Droplet, FlaskConical, Sun
} from 'lucide-react';
import SensorCard        from '../components/SensorCard';
import PredictiveHub     from '../components/PredictiveHub';
import WeatherPanel      from '../components/WeatherPanel';
import AlertBanner       from '../components/AlertBanner';
import HistoryChart      from '../components/HistoryChart';
import AdvisoryPane      from '../components/AdvisoryPane';
import ManualInputPanel  from '../components/ManualInputPanel';

export default function Dashboard() {
  const [manualTrigger, setManualTrigger] = useState(0);
  const [time, setTime] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  const { data: sensors, loading: sl }  = useSensorData();
  const { data: preds, loading: pl }    = usePredictions(manualTrigger);

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const onManualSubmit = () => {
    setTimeout(() => setManualTrigger(t => t + 1), 1500);
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'live_sensors', label: 'Live Sensors', icon: Cpu },
    { id: 'ai_predictions', label: 'AI Predictions', icon: BrainCircuit },
    { id: 'weather', label: 'Weather', icon: CloudSun },
    { id: 'history', label: 'History', icon: LineChart },
    { id: 'manual_input', label: 'Manual Input', icon: SlidersHorizontal },
  ];

  return (
    <div className="app-wrapper">
      {/* ── Sidebar ───────────────────────────────────────────────────────── */}
      <aside className="app-sidebar">
        <div className="sidebar-header">
          <div className="header-logo">
            <Sprout size={24} />
            <div>
              <h1>KrishiMitra</h1>
              <span className="tagline">{preds?.inputs?.state || 'Detecting…'}</span>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <div 
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </div>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span style={{color: '#1A1A1A', fontWeight: 500}}>Live System</span>
          </div>
          <div style={{marginTop: '0.25rem'}}>{time}</div>
        </div>
      </aside>

      {/* ── Main Content Area ──────────────────────────────────────────────── */}
      <main className="main-content">
        
        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="tab-overview">
            <h2 className="section-title">Overview</h2>
            <div className="overview-top-row">
              <SensorCard 
                icon={<Thermometer size={20} />} label="Air Temp" 
                value={sensors?.air_temp} unit="°C" 
                colorClass="status-amber" />
              <SensorCard 
                icon={<Droplet size={20} />} label="Soil Moisture" 
                value={sensors?.soil_moisture} unit="%" 
                colorClass="status-green" />
              <div className="sensor-card">
                <div className="sc-header">
                  <Sprout size={20} className="sc-icon" style={{color: 'var(--accent-green)'}} />
                  <span className="sc-label">Top Crop</span>
                </div>
                <div className="sc-value" style={{textTransform: 'capitalize'}}>
                  {preds?.crop || '---'}
                </div>
              </div>
              <div className="sensor-card">
                <div className="sc-header">
                  <Droplet size={20} className="sc-icon" style={{color: 'var(--accent-blue)'}} />
                  <span className="sc-label">Irrigation</span>
                </div>
                <div className="sc-value">
                  {preds?.irrigation_need || '---'}
                </div>
              </div>
            </div>

            <AlertBanner />

            <div className="weather-condensed">
               <CloudSun size={32} style={{color: 'var(--accent-amber)'}} />
               <div>
                 <div style={{fontFamily: 'DM Mono', fontSize: '1.5rem', fontWeight: 600, color: 'var(--text-primary)'}}>
                   Live Local Weather
                 </div>
                 <div style={{fontSize: '0.9rem', color: 'var(--text-secondary)'}}>
                   Switch to the Weather tab for full details and the 5-day forecast.
                 </div>
               </div>
            </div>

            <AdvisoryPane sensors={sensors} predictions={preds} />
          </div>
        )}

        {/* Tab 2: Live Sensors */}
        {activeTab === 'live_sensors' && (
          <div className="tab-live-sensors">
            <h2 className="section-title">Live Sensor Telemetry</h2>
            <div className="sensor-grid">
              <SensorCard icon={<Thermometer size={20} />} label="Air Temp"
                value={sensors?.air_temp} unit="°C" sub="DHT22" colorClass="status-amber" />
              <SensorCard icon={<Droplets size={20} />} label="Humidity"
                value={sensors?.air_humidity} unit="%" sub="DHT22" colorClass="status-blue" />
              <SensorCard icon={<Thermometer size={20} />} label="Soil Temp"
                value={sensors?.soil_temp} unit="°C" sub="DS18B20" colorClass="status-amber" />
              <SensorCard icon={<Droplet size={20} />} label="Soil Moisture"
                value={sensors?.soil_moisture} unit="%" sub="Arduino" colorClass="status-green" />
              <SensorCard icon={<FlaskConical size={20} />} label="Soil pH"
                value={sensors?.soil_ph} unit="" sub="Arduino" colorClass="status-blue" />
              <SensorCard icon={<Sun size={20} />} label="Light"
                value={sensors?.light_lux} unit=" Lux" sub="BH1750" colorClass="status-amber" />
            </div>
          </div>
        )}

        {/* Tab 3: AI Predictions */}
        {activeTab === 'ai_predictions' && (
          <div className="tab-ai-predictions">
             <h2 className="section-title">Predictive Intelligence</h2>
             <PredictiveHub data={preds} loading={pl} />
             <AdvisoryPane sensors={sensors} predictions={preds} />
          </div>
        )}

        {/* Tab 4: Weather */}
        {activeTab === 'weather' && (
          <div className="tab-weather">
             <h2 className="section-title">Weather Conditions</h2>
             <WeatherPanel />
          </div>
        )}

        {/* Tab 5: History */}
        {activeTab === 'history' && (
          <div className="tab-history">
             <h2 className="section-title">Historical Analytics</h2>
             <HistoryChart />
          </div>
        )}

        {/* Tab 6: Manual Input */}
        {activeTab === 'manual_input' && (
          <div className="tab-manual-input">
             <h2 className="section-title">Field Configuration</h2>
             <ManualInputPanel onSubmit={onManualSubmit} />
          </div>
        )}

      </main>
    </div>
  );
}
