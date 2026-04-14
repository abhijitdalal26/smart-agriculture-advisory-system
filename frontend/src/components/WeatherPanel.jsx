import { useState, useEffect } from 'react';
import axios from 'axios';
import { Sun, CloudSun, Cloud, CloudRain, CloudLightning, Snowflake, Wind, Droplet, MapPin } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || "";

const getWeatherIcon = (iconName, size = 24, className = '') => {
  const props = { size, className };
  switch(iconName) {
    case 'sunny': return <Sun {...props} style={{color: 'var(--accent-amber)'}} />;
    case 'partly_cloudy': return <CloudSun {...props} style={{color: 'var(--accent-amber)'}} />;
    case 'cloudy': return <Cloud {...props} style={{color: 'var(--text-secondary)'}} />;
    case 'rainy': 
    case 'showers': return <CloudRain {...props} style={{color: 'var(--accent-blue)'}} />;
    case 'thunderstorm': return <CloudLightning {...props} style={{color: '#7C3AED'}} />;
    case 'snowy': return <Snowflake {...props} style={{color: '#93C5FD'}} />;
    default: return <CloudSun {...props} style={{color: 'var(--accent-amber)'}} />;
  }
};

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function WeatherPanel() {
  const [current,  setCurrent]  = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [curRes, fcRes] = await Promise.all([
          axios.get(`${API}/api/weather/current`,  { timeout: 8000 }),
          axios.get(`${API}/api/weather/forecast`, { timeout: 8000 }),
        ]);
        setCurrent(curRes.data);
        setForecast(fcRes.data.forecast || []);
      } catch (_) {} finally {
        setLoading(false);
      }
    };
    fetchAll();
    const id = setInterval(fetchAll, 300000); // refresh every 5 min
    return () => clearInterval(id);
  }, []);

  const dayLabel = (dateStr) => {
    const d = new Date(dateStr);
    return DAYS[d.getDay()];
  };

  return (
    <div className="card weather-panel">
      {loading ? (
        <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
          Loading weather…
        </div>
      ) : (
        <div className="weather-split">
          {current && (
            <div className="weather-current">
              <div className="weather-icon-lg">
                {getWeatherIcon(current.icon, 52)}
              </div>
              <div className="weather-info">
                <div className="wi-temp">
                  {current.temperature != null ? `${current.temperature.toFixed(1)}°` : '--°'}
                </div>
                <div className="wi-desc">
                  {current.icon.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </div>
                <div className="wi-extras">
                  <Wind size={14} /> {current.wind_speed?.toFixed(1) ?? '--'} km/h
                  <span style={{color: 'var(--border-color)'}}>|</span>
                  <Droplet size={14} /> {current.humidity ?? '--'}%
                </div>
                {current.location && (
                  <div className="wi-extras">
                    <MapPin size={14} /> {current.location.city}, {current.location.state}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="forecast-strip">
            {forecast.slice(0, 5).map((day, i) => (
              <div key={i} className="forecast-day">
                <div className="fd-date">{dayLabel(day.date)}</div>
                <div className="fd-icon">{getWeatherIcon(day.icon, 24)}</div>
                <div className="fd-temp">{day.temp_max?.toFixed(0)}°<span style={{color:'var(--text-muted)', fontWeight:400, marginLeft:2}}>/{day.temp_min?.toFixed(0)}°</span></div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
