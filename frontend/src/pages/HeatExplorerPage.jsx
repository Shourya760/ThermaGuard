// Dedicated Heat Explorer page for inspecting spatial zones, filtering by risk, and reviewing indicator profiles
import { useState } from 'react'
import {
  CloudSun, Filter, MapPinned, Search,
  SlidersHorizontal, Sparkles, Trees, Users, Waves
} from 'lucide-react'
import HeatMap from '../components/map/HeatMap'
import ZoneRiskPanel from '../components/map/ZoneRiskPanel'
import { formatTemp } from '../utils/tempUtils'

export default function HeatExplorerPage({
  zones = [],
  selectedZone,
  selectedCity,
  tempUnit = '°C',
  currentWeather,
  weatherError,
  onSelectZone,
  onNavigate
}) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterLevel, setFilterLevel] = useState('ALL')

  // Filter zones by search text and risk level
  const filteredZones = zones.filter((zone) => {
    const matchesSearch = zone.name.toLowerCase().includes(searchQuery.toLowerCase())
    if (!matchesSearch) return false
    if (filterLevel === 'ALL') return true
    if (filterLevel === 'EXTREME') return zone.risk >= 80
    if (filterLevel === 'HIGH') return zone.risk >= 70 && zone.risk < 80
    if (filterLevel === 'MODERATE') return zone.risk >= 50 && zone.risk < 70
    if (filterLevel === 'LOW') return zone.risk < 50
    return true
  })

  const resetFilters = () => {
    setSearchQuery('')
    setFilterLevel('ALL')
  }

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> SPATIAL THERMAL ANALYSIS
          </div>
          <h1>Heat explorer</h1>
          <p className="welcome-subtitle">
            Explore illustrative heat-risk zones and contributing microclimate indicators for <strong>{selectedCity?.name || 'monitored regions'}</strong>.
          </p>
        </div>
        <div className="date-pill">
          <CloudSun size={19} />
          <span>Interactive spatial view</span>
        </div>
      </section>

      {/* Filter and search bar */}
      <section className="panel explorer-filter-bar" style={{ marginBottom: '18px' }}>
        <div className="search-box">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search zone by name (e.g. City Centre, Transit Hub)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search zones"
          />
          {searchQuery && (
            <button
              type="button"
              className="search-clear"
              onClick={() => setSearchQuery('')}
            >
              Clear
            </button>
          )}
        </div>

        <div className="filter-pills">
          <span className="filter-label">
            <Filter size={13} /> Filter:
          </span>
          {[
            { id: 'ALL', label: `All (${zones.length})` },
            { id: 'EXTREME', label: 'Extreme (>80)' },
            { id: 'HIGH', label: 'High (70-79)' },
            { id: 'MODERATE', label: 'Moderate (50-69)' },
            { id: 'LOW', label: 'Low (<50)' },
          ].map(({ id, label }) => (
            <button
              key={id}
              type="button"
              className={`filter-pill ${filterLevel === id ? 'active' : ''}`}
              onClick={() => setFilterLevel(id)}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      {/* Map and selected zone breakdown */}
      <section className="overview-grid">
        <article className="panel map-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <MapPinned size={18} /> Zone Map ({filteredZones.length} displayed)
              </div>
              <p>Click on any circle or list item to inspect environmental factors</p>
            </div>
          </div>
          <HeatMap
            zones={filteredZones.length > 0 ? filteredZones : zones}
            selectedZoneId={selectedZone?.id}
            onSelect={onSelectZone}
            mapHeight={390}
            tempUnit={tempUnit}
            cityCenter={selectedCity?.center}
          />
        </article>

        <ZoneRiskPanel
          zone={selectedZone}
          tempUnit={tempUnit}
          currentWeather={currentWeather}
          weatherError={weatherError}
          onPlanIntervention={() => onNavigate('Intervention planner')}
        />
      </section>

      {/* Comprehensive zone cards overview */}
      <section className="panel" style={{ marginTop: '18px' }}>
        <div className="panel-heading">
          <div>
            <div className="panel-title">
              <SlidersHorizontal size={18} /> Zone Breakdown Summary
            </div>
            <p>Comparative indicators across monitored urban areas</p>
          </div>
        </div>

        {filteredZones.length === 0 ? (
          <div style={{ padding: '30px', textAlign: 'center', color: '#788994' }}>
            <p style={{ margin: '0 0 10px', fontSize: '13px' }}>No zones match your search query or filter.</p>
            <button type="button" className="primary-button" style={{ margin: '0 auto' }} onClick={resetFilters}>
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="zone-cards-grid">
            {filteredZones.map((zone) => {
              const isSelected = selectedZone?.id === zone.id
              return (
                <div
                  key={zone.id}
                  className={`zone-detail-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectZone(zone)}
                  role="button"
                  tabIndex={0}
                >
                  <div className="zone-card-header">
                    <div>
                      <strong>{zone.name}</strong>
                      <span className="zone-card-level" style={{ color: zone.color }}>
                        {zone.level} Risk
                      </span>
                    </div>
                    <span className="zone-card-score" style={{ color: zone.color }}>
                      {zone.risk}
                      <small>/100</small>
                    </span>
                  </div>

                  <p className="zone-card-desc">{zone.description}</p>

                  <div className="zone-card-metrics">
                    <div className="metric-item">
                      <CloudSun size={14} />
                      <span>Temp: <b>{formatTemp(zone.temp, tempUnit)}</b></span>
                    </div>
                    <div className="metric-item">
                      <Trees size={14} />
                      <span>Canopy: <b>{zone.canopyCover}</b></span>
                    </div>
                    <div className="metric-item">
                      <Users size={14} />
                      <span>Pop: <b>{zone.populationExposure}</b></span>
                    </div>
                    <div className="metric-item">
                      <Waves size={14} />
                      <span>Cooling: <b>{zone.coolingCentres ?? 1} ctrs</b></span>
                    </div>
                  </div>

                  <div className="zone-card-actions">
                    <button
                      type="button"
                      className="text-button"
                      onClick={(e) => {
                        e.stopPropagation()
                        onSelectZone(zone)
                        onNavigate('Intervention planner')
                      }}
                    >
                      Plan Action <Sparkles size={12} />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </>
  )
}
