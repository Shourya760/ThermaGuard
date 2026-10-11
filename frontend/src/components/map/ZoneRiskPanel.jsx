// Detailed indicator breakdown and risk assessment panel for a selected zone
import { CloudSun, Droplets, HeartPulse, Trees, Users, Waves } from 'lucide-react'
import { formatTemp } from '../../utils/tempUtils'

export default function ZoneRiskPanel({ zone, onPlanIntervention, tempUnit = '°C', currentWeather, weatherError }) {
  if (!zone) return null

  // Risk categorization helper
  const getRiskLabel = (score) => {
    if (score >= 80) return 'Extreme risk'
    if (score >= 70) return 'High risk'
    if (score >= 50) return 'Moderate risk'
    return 'Low risk'
  }
  const displayedTemperature = currentWeather?.temperature_celsius ?? zone.temp
  const displayedHumidity = currentWeather?.relative_humidity_percent ?? Number.parseFloat(zone.humidity)
  const temperatureLabel = currentWeather?.temperature_celsius != null ? 'Live observation · Open-Meteo' : weatherError ? 'Live unavailable · sample shown' : 'Loading live weather…'
  const humidityLabel = currentWeather?.relative_humidity_percent != null ? 'Live observation · Open-Meteo' : weatherError ? 'Live unavailable · sample shown' : 'Loading live weather…'

  return (
    <article className="panel risk-panel">
      <div className="panel-heading">
        <div>
          <div className="panel-title">
            <HeartPulse size={18} /> Selected zone
          </div>
          <p>Illustrative risk profile · live weather when available</p>
        </div>
        <span
          className="risk-badge"
          style={{
            backgroundColor: `${zone.color}15`,
            color: zone.color,
          }}
        >
          {getRiskLabel(zone.risk)}
        </span>
      </div>

      <div className="selected-zone-title">
        <div>
          <h3>{zone.name}</h3>
          <p>Selected monitoring area</p>
        </div>
        <div className="risk-number" style={{ color: zone.color }}>
          {zone.risk}
          <small>/100</small>
        </div>
      </div>

      <div className="risk-meter">
        <span style={{ width: `${zone.risk}%`, background: zone.color }} />
      </div>
      <div className="risk-meter-label">
        <span>Lower risk</span>
        <span>Higher risk</span>
      </div>

      <div className="indicator-list">
        <div className="indicator-row">
          <span className="indicator-icon temp-icon">
            <CloudSun size={17} />
          </span>
          <span className="indicator-name">
            Air temperature
            <small>{temperatureLabel}</small>
          </span>
            <strong>{formatTemp(displayedTemperature, tempUnit)}</strong>
        </div>

        <div className="indicator-row">
          <span className="indicator-icon humidity-icon">
            <Droplets size={17} />
          </span>
          <span className="indicator-name">
            Humidity
            <small>{humidityLabel}</small>
          </span>
            <strong>{Number.isFinite(displayedHumidity) ? `${Math.round(displayedHumidity)}%` : '—'}</strong>
        </div>

        <div className="indicator-row">
          <span className="indicator-icon people-icon">
            <Users size={17} />
          </span>
          <span className="indicator-name">
            Population exposure
            <small>Planning estimate</small>
          </span>
          <strong>{zone.populationExposure || 'High'}</strong>
        </div>

        <div className="indicator-row">
          <span className="indicator-icon shade-icon">
            <Trees size={17} />
          </span>
          <span className="indicator-name">
            Green shade cover
            <small>Tree canopy</small>
          </span>
          <strong>{zone.canopyCover || 'Low'}</strong>
        </div>

        <div className="indicator-row">
          <span className="indicator-icon" style={{ background: '#e0f2fe', color: '#0284c7' }}>
            <Waves size={17} />
          </span>
          <span className="indicator-name">
            Cooling shelters
            <small>Public facilities</small>
          </span>
          <strong>{zone.coolingCentres ?? 1} available</strong>
        </div>
      </div>

      {onPlanIntervention && (
        <button
          type="button"
          className="primary-button full-button"
          onClick={() => onPlanIntervention(zone)}
        >
          Plan an intervention <span>→</span>
        </button>
      )}
    </article>
  )
}
