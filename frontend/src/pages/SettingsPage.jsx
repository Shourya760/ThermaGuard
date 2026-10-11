// Settings & Workspace Configuration page for adjusting units, alert thresholds, and cities
import { useState } from 'react'
import {
  Bell, Check, Compass, Info, Thermometer
} from 'lucide-react'
import { cities } from '../data/mockData'
import { formatTemp } from '../utils/tempUtils'

export default function SettingsPage({
  selectedCity,
  onSelectCity,
  tempUnit = '°C',
  onToggleTempUnit,
  alertThreshold = 42,
  onUpdateAlertThreshold
}) {
  const [localThreshold, setLocalThreshold] = useState(String(alertThreshold))
  const [emailAlerts, setEmailAlerts] = useState(true)
  const [smsAlerts, setSmsAlerts] = useState(false)
  const [savedSettings, setSavedSettings] = useState(false)

  const handleSave = () => {
    onUpdateAlertThreshold?.(Number(localThreshold))
    setSavedSettings(true)
    setTimeout(() => setSavedSettings(false), 2500)
  }

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> CONFIGURATION & PREFERENCES
          </div>
          <h1>Settings</h1>
          <p className="welcome-subtitle">
            Configure your urban monitoring workspace, thresholds, and resilience alert preferences.
          </p>
        </div>
      </section>

      {savedSettings && (
        <div className="saved-message" style={{ marginBottom: '18px' }}>
          <Check size={16} /> Preferences saved successfully.
        </div>
      )}

      <div className="settings-grid">
        {/* Workspace selection */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <Compass size={18} /> Active City Monitoring Workspace
              </div>
              <p>Select which urban boundary data model to load</p>
            </div>
          </div>

          <div className="city-options-grid">
            {cities.map((city) => (
              <button
                key={city.id}
                type="button"
                className={`city-card-btn ${selectedCity?.id === city.id ? 'active' : ''}`}
                onClick={() => onSelectCity?.(city)}
              >
                <strong>{city.name}</strong>
                <small>{city.label}</small>
                {selectedCity?.id === city.id && (
                  <span className="city-card-active-tag">Active</span>
                )}
              </button>
            ))}
          </div>
        </section>

        {/* Units & Display preferences */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <Thermometer size={18} /> Temperature Units & Display
              </div>
              <p>Choose your preferred measurement scale (updates all dashboards & maps)</p>
            </div>
          </div>

          <div className="settings-field-row">
            <div>
              <strong>Display Units</strong>
              <small>Choose between Celsius and Fahrenheit</small>
            </div>
            <div className="unit-toggle-group">
              <button
                type="button"
                className={`unit-toggle-btn ${tempUnit === '°C' ? 'active' : ''}`}
                onClick={() => onToggleTempUnit?.('°C')}
              >
                °C (Celsius)
              </button>
              <button
                type="button"
                className={`unit-toggle-btn ${tempUnit === '°F' ? 'active' : ''}`}
                onClick={() => onToggleTempUnit?.('°F')}
              >
                °F (Fahrenheit)
              </button>
            </div>
          </div>
        </section>

        {/* Heatwave Alert Thresholds */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <Bell size={18} /> Early Warning Sensitivity
              </div>
              <p>Set trigger threshold for automatic Red Alert notifications</p>
            </div>
          </div>

          <div className="settings-field-row">
            <div>
              <strong>Red Alert Temperature Threshold</strong>
              <small>Alert triggers when predicted afternoon peak crosses this value</small>
            </div>
            <select
              className="settings-select"
              value={localThreshold}
              onChange={(e) => setLocalThreshold(e.target.value)}
              aria-label="Red alert temperature threshold"
            >
              <option value="40">
                {formatTemp(40, tempUnit)} (Standard Heatwave)
              </option>
              <option value="42">
                {formatTemp(42, tempUnit)} (Severe Heatwave)
              </option>
              <option value="44">
                {formatTemp(44, tempUnit)} (Extreme Emergency)
              </option>
            </select>
          </div>

          <div className="settings-field-row" style={{ marginTop: '14px' }}>
            <div>
              <strong>Dispatch Notifications</strong>
              <small>Automated notification channels for municipal coordinators</small>
            </div>
            <div style={{ display: 'flex', gap: '15px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                <input
                  type="checkbox"
                  checked={emailAlerts}
                  onChange={(e) => setEmailAlerts(e.target.checked)}
                />
                Email Reports
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                <input
                  type="checkbox"
                  checked={smsAlerts}
                  onChange={(e) => setSmsAlerts(e.target.checked)}
                />
                SMS Broadcast
              </label>
            </div>
          </div>

          <button
            type="button"
            className="primary-button"
            style={{ marginTop: '20px' }}
            onClick={handleSave}
          >
            Save Alert Preferences
          </button>
        </section>

        {/* About ThermaGuard */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <Info size={18} /> About ThermaGuard Platform
              </div>
              <p>Urban Resilience & Thermal Action Planning</p>
            </div>
          </div>

          <div className="about-content">
            <p>
              ThermaGuard combines spatial heat island mapping with evidence-based municipal intervention planning.
              By pinpointing microclimates where surface heat overlaps with high population vulnerability, civic authorities can deploy cooling centers, shaded transit corridors, and hydration stations with maximum return on investment.
            </p>
            <div className="about-meta">
              <span><b>Version:</b> 2.4.0-resilience</span>
              <span><b>Data Provider:</b> Municipal Satellite & Sensor Network (Demo)</span>
            </div>
          </div>
        </section>
      </div>
    </>
  )
}
