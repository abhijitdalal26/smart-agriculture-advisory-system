// KrishiMitra — Main Dashboard Page
import { useState, useEffect } from 'react';
import { useSensorData }  from '../hooks/useSensorData';
import { usePredictions } from '../hooks/usePredictions';
import SensorCard        from '../components/SensorCard';
import GaugeChart        from '../components/GaugeChart';
import PredictiveHub     from '../components/PredictiveHub';
import WeatherPanel      from '../components/WeatherPanel';
import AlertBanner       from '../components/AlertBanner';
import HistoryChart      from '../components/HistoryChart';
import AdvisoryPane      from '../components/AdvisoryPane';
import ManualInputPanel  from '../components/ManualInputPanel';

export default function Dashboard() {
  const [manualTrigger, setManualTrigger] = useState(0);
  const [time, setTime] = useState('');

  const { data: sensors, loading: sl }  = useSensorData();
  const { data: preds, loading: pl }    = usePredictions(manualTrigger);

  // Live clock
  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const onManualSubmit = () => {
    // Give the API a moment to process then re-fetch predictions
    setTimeout(() => setManualTrigger(t => t + 1), 1500);
  };

  return (
    <div className="app-wrapper">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="header-logo">
          <span className="logo-icon">🌿</span>
          <div>
            <h1>KrishiMitra</h1>
            <span className="tagline">Smart Agricultural Advisory System</span>
          </div>
        </div>
        <div className="header-right">
          <span className="location-badge">📍 {preds?.inputs?.state || 'Detecting…'}</span>
          <span className="header-time">{time}</span>
          <span className="status-dot">Live</span>
        </div>
      </header>

      <main className="main-content">
        {/* ── Alerts ─────────────────────────────────────────────────────── */}
        <AlertBanner />

        {/* ── Sensor Cards Row ───────────────────────────────────────────── */}
        <div className="section-label">📡 Live Sensor Telemetry</div>
        <div className="sensor-row">
          <SensorCard icon="🌡️" label="Air Temp"      colorClass="sc-air-temp"
            value={sensors?.air_temp}     unit="°C" sub="DHT22" />
          <SensorCard icon="💧" label="Humidity"       colorClass="sc-humidity"
            value={sensors?.air_humidity} unit="%" sub="DHT22" />
          <SensorCard icon="🌱" label="Soil Temp"      colorClass="sc-soil-temp"
            value={sensors?.soil_temp}    unit="°C" sub="DS18B20" />
          <SensorCard icon="💦" label="Soil Moisture"  colorClass="sc-soil-moist"
            value={sensors?.soil_moisture} unit="%" sub="Arduino" />
          <SensorCard icon="⚗️" label="Soil pH"        colorClass="sc-ph"
            value={sensors?.soil_ph}       unit="" sub="Arduino" />
          <SensorCard icon="☀️" label="Light"          colorClass="sc-light"
            value={sensors?.light_lux}    unit=" Lux" sub="BH1750" />
        </div>

        {/* ── Gauges Row ─────────────────────────────────────────────────── */}
        <div className="section-label">📊 Field Health Gauges</div>
        <div className="gauge-row">
          <GaugeChart icon="💦" label="Soil Moisture"
            value={sensors?.soil_moisture} min={0} max={100}
            color="#22c55e" unit="%" />
          <GaugeChart icon="⚗️" label="Soil pH"
            value={sensors?.soil_ph} min={0} max={14}
            color="#a78bfa" unit="" />
          <GaugeChart icon="💧" label="Air Humidity"
            value={sensors?.air_humidity} min={0} max={100}
            color="#3b82f6" unit="%" />
        </div>

        {/* ── Main Panels ────────────────────────────────────────────────── */}
        <div className="section-label">🧠 Intelligence Hub</div>
        <div className="dashboard-grid">
          <PredictiveHub data={preds} loading={pl} />
          <WeatherPanel />
        </div>

        {/* ── History ────────────────────────────────────────────────────── */}
        <div className="section-label">📈 Historical Analytics</div>
        <HistoryChart />

        {/* ── Advisory ───────────────────────────────────────────────────── */}
        <div className="section-label">💬 AI Advisory</div>
        <AdvisoryPane sensors={sensors} predictions={preds} />

        {/* ── Manual Input ───────────────────────────────────────────────── */}
        <div className="section-label">🧪 Field Configuration</div>
        <ManualInputPanel onSubmit={onManualSubmit} />
      </main>
    </div>
  );
}
