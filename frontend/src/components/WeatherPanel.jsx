// WeatherPanel — current conditions + 5-day forecast
import { useState, useEffect } from 'react';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

const WEATHER_ICONS = {
  sunny: '☀️', partly_cloudy: '⛅', cloudy: '☁️',
  rainy: '🌧️', showers: '🌦️', thunderstorm: '⛈️', snowy: '❄️',
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
      <div className="card-title">☁️ Weather Intelligence</div>

      {loading ? (
        <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
          Loading weather…
        </div>
      ) : (
        <>
          {current && (
            <div className="weather-current">
              <div className="weather-icon-lg">
                {WEATHER_ICONS[current.icon] || '🌤️'}
              </div>
              <div className="weather-info">
                <div className="wi-temp">
                  {current.temperature != null ? `${current.temperature.toFixed(1)}°C` : '--°C'}
                </div>
                <div className="wi-desc">
                  Feels like {current.feels_like?.toFixed(1) ?? '--'}°C
                </div>
                <div className="wi-extras">
                  💧 {current.humidity ?? '--'}% &nbsp;|&nbsp;
                  💨 {current.wind_speed?.toFixed(1) ?? '--'} km/h &nbsp;|&nbsp;
                  🌧 {current.precipitation ?? 0} mm
                </div>
                {current.location && (
                  <div className="wi-extras" style={{marginTop:'0.3rem'}}>
                    📍 {current.location.city}, {current.location.state}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="forecast-row">
            {forecast.slice(0, 5).map((day, i) => (
              <div key={i} className="forecast-day">
                <div className="fd-date">{dayLabel(day.date)}</div>
                <div className="fd-icon">{WEATHER_ICONS[day.icon] || '🌤️'}</div>
                <div className="fd-temp">{day.temp_max?.toFixed(0)}°/{day.temp_min?.toFixed(0)}°</div>
                <div className="fd-rain">🌧 {day.precipitation?.toFixed(1)}mm</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
