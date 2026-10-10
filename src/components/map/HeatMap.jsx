// Interactive Leaflet heatmap displaying thermal risk zones with radius circles
import { useEffect } from 'react'
import { Circle, MapContainer, TileLayer, Tooltip, useMap } from 'react-leaflet'
import { formatTemp } from '../../utils/tempUtils'

// Helper component to smoothly center, zoom, and invalidate map size on zone/city changes
function MapFocus({ zone }) {
  const map = useMap()

  useEffect(() => {
    map.invalidateSize()
    if (zone?.position) {
      map.flyTo(zone.position, 13, { duration: 0.7 })
    }
  }, [zone, map])

  return null
}

export default function HeatMap({
  zones = [],
  selectedZoneId,
  onSelect,
  mapHeight,
  tempUnit = '°C',
  cityCenter
}) {
  const activeZone = zones.find((z) => z.id === selectedZoneId) || zones[0]
  const defaultCenter = activeZone?.position || cityCenter || [28.6139, 77.209]

  return (
    <div className="map-layout">
      <div className="map-canvas" style={mapHeight ? { height: mapHeight } : undefined}>
        <MapContainer
          key={`map-${defaultCenter[0]}-${defaultCenter[1]}`}
          center={defaultCenter}
          zoom={12}
          scrollWheelZoom
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapFocus zone={activeZone} />
          {zones.map((zone) => {
            const isSelected = activeZone?.id === zone.id
            return (
              <Circle
                key={zone.id}
                center={zone.position}
                radius={isSelected ? 900 : 650}
                pathOptions={{
                  color: zone.color,
                  fillColor: zone.color,
                  fillOpacity: isSelected ? 0.48 : 0.27,
                  weight: isSelected ? 3 : 1,
                }}
                eventHandlers={{
                  click: () => onSelect?.(zone),
                }}
              >
                <Tooltip>
                  <strong>{zone.name}</strong><br />
                  Risk score: {zone.risk}/100<br />
                  Temperature: {formatTemp(zone.temp, tempUnit)}
                </Tooltip>
              </Circle>
            )
          })}
        </MapContainer>
        <div className="map-label">
          <span className="live-dot" /> Illustrative zone data
        </div>
      </div>

      <aside className="zone-list">
        <div className="zone-list-heading">
          <div>
            <strong>Risk zones</strong>
            <p>Select a zone to explore</p>
          </div>
          <span className="zone-count">{zones.length}</span>
        </div>

        {zones.map((zone) => {
          const isSelected = activeZone?.id === zone.id
          return (
            <button
              key={zone.id}
              type="button"
              className={`zone-row ${isSelected ? 'zone-active' : ''}`}
              onClick={() => onSelect?.(zone)}
            >
              <span className="zone-dot" style={{ background: zone.color }} />
              <span className="zone-info">
                <strong>{zone.name}</strong>
                <small>{formatTemp(zone.temp, tempUnit)} · Risk {zone.risk}/100</small>
              </span>
              <span className="zone-score" style={{ color: zone.color }}>
                {zone.risk}
              </span>
            </button>
          )
        })}

        <div className="map-legend">
          <strong>Heat-risk legend</strong>
          <div>
            <i style={{ background: '#22c55e' }} /> Low
            <i style={{ background: '#eab308' }} /> Moderate
          </div>
          <div>
            <i style={{ background: '#f97316' }} /> High
            <i style={{ background: '#ef4444' }} /> Extreme
          </div>
        </div>
      </aside>
    </div>
  )
}
