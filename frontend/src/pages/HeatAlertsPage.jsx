// Heat Alerts & Emergency Advisories page for active warnings and response protocols
import { useState } from 'react'
import {
  AlertTriangle, Check, Clock, Droplets, Flame,
  HeartPulse, MapPin, ShieldCheck
} from 'lucide-react'
import { formatTemp } from '../utils/tempUtils'

export default function HeatAlertsPage({
  alerts = [],
  zones = [],
  tempUnit = '°C',
  onSelectZone,
  onDismissAlert,
  onNavigate
}) {
  const [filterSeverity, setFilterSeverity] = useState('ALL')
  // Interactive SOP checklist state
  const [completedSops, setCompletedSops] = useState([1])

  const toggleSop = (id) => {
    setCompletedSops((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )
  }

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity === 'ALL') return true
    return a.severity.toLowerCase() === filterSeverity.toLowerCase()
  })

  // Zones under severe watch (>70 risk score)
  const highRiskZones = zones.filter((z) => z.risk >= 70)

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> EARLY WARNING SYSTEM
          </div>
          <h1>Heat alerts & advisories</h1>
          <p className="welcome-subtitle">
            Real-time heatwave warnings, vulnerable community advisories, and municipal SOP protocols.
          </p>
        </div>
        <div className="date-pill">
          <AlertTriangle size={19} style={{ color: '#ef4444' }} />
          <span>Active alert level: {alerts.length > 0 ? 'RED' : 'NORMAL'}</span>
        </div>
      </section>

      {/* Alert level filter pills */}
      <section className="panel" style={{ marginBottom: '18px', padding: '14px 20px' }}>
        <div className="filter-pills">
          <span className="filter-label">Alert Severity:</span>
          {[
            { id: 'ALL', label: `All Alerts (${alerts.length})` },
            { id: 'CRITICAL', label: 'Red (Critical)' },
            { id: 'WARNING', label: 'Orange (Warning)' },
            { id: 'INFO', label: 'Yellow (Advisory)' },
          ].map(({ id, label }) => (
            <button
              key={id}
              type="button"
              className={`filter-pill ${filterSeverity === id ? 'active' : ''}`}
              onClick={() => setFilterSeverity(id)}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      {/* Active alerts stream */}
      <div className="alerts-container">
        {filteredAlerts.length === 0 ? (
          <div className="panel" style={{ padding: '30px', textAlign: 'center', color: '#788994' }}>
            <p style={{ margin: 0, fontSize: '13px' }}>
              No active warnings match this filter. All municipal advisories acknowledged.
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <article key={alert.id} className={`alert-card-detailed ${alert.severity}`}>
              <div className="alert-card-top">
                <div className="alert-badge-group">
                  <span className={`alert-badge ${alert.severity}`}>
                    <AlertTriangle size={13} /> {alert.severity.toUpperCase()}
                  </span>
                  <span className="alert-zone">
                    <MapPin size={13} /> {alert.zone}
                  </span>
                </div>
                <span className="alert-timestamp">
                  <Clock size={13} /> Issued: {alert.issued}
                </span>
              </div>

              <h3 className="alert-card-title">{alert.title}</h3>
              <p className="alert-card-message">{alert.message}</p>

              <div className="alert-action-footer">
                <span className="alert-sop-tag">
                  <ShieldCheck size={14} /> Municipal SOP Level 3 Triggered
                </span>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {onDismissAlert && (
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => onDismissAlert(alert.id)}
                    >
                      Acknowledge
                    </button>
                  )}
                  <button
                    type="button"
                    className="text-button"
                    onClick={() => onNavigate('Intervention planner')}
                  >
                    Deploy Interventions <span>→</span>
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      {/* High-Risk Zones Monitored */}
      {highRiskZones.length > 0 && (
        <section className="panel" style={{ marginTop: '20px' }}>
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <Flame size={18} /> Zones Under Active Heat Surveillance
              </div>
              <p>Click on any high-risk sector to inspect thermal indicators in Heat Explorer</p>
            </div>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {highRiskZones.map((z) => (
              <button
                key={z.id}
                type="button"
                onClick={() => {
                  onSelectZone?.(z)
                  onNavigate?.('Heat explorer')
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: `${z.color}12`,
                  border: `1px solid ${z.color}35`,
                  fontSize: '11px',
                  cursor: 'pointer',
                }}
              >
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: z.color }} />
                <strong>{z.name}</strong>
                <span style={{ color: z.color, fontWeight: 700 }}>
                  {formatTemp(z.temp, tempUnit)} · Risk {z.risk}/100
                </span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Community Resilience SOP Checklist */}
      <section className="panel" style={{ marginTop: '20px' }}>
        <div className="panel-heading">
          <div>
            <div className="panel-title">
              <HeartPulse size={18} /> Standard Operating Procedures (Heatwave Protocol Checklist)
            </div>
            <p>Interactive protocol checklist for civic authorities ({completedSops.length} of 4 completed)</p>
          </div>
        </div>

        <div className="sop-grid">
          {[
            {
              id: 1,
              icon: Droplets,
              color: 'blue',
              title: 'Hydration Stations Activation',
              detail: 'Deploy mobile water tankers and shade tarpaulins at central transit hubs.',
            },
            {
              id: 2,
              icon: ShieldCheck,
              color: 'green',
              title: 'Cooling Shelter Access',
              detail: 'Keep designated community halls open 10 AM – 8 PM with fans and ORS packets.',
            },
            {
              id: 3,
              icon: Clock,
              color: 'orange',
              title: 'Outdoor Labor Curtailment',
              detail: 'Enforce mandatory rest breaks between 12:00 PM and 04:00 PM on job sites.',
            },
            {
              id: 4,
              icon: Flame,
              color: 'red',
              title: 'Hospital Heat Ward Readiness',
              detail: 'Ensure dedicated ice packs, saline fluids, and heatstroke beds are prepped.',
            },
          ].map(({ id, icon: Icon, color, title, detail }) => {
            const isDone = completedSops.includes(id)
            return (
              <div
                key={id}
                className="sop-item"
                style={{
                  cursor: 'pointer',
                  borderColor: isDone ? '#a3d9cb' : undefined,
                  background: isDone ? '#f4faf8' : undefined,
                  transition: 'all 0.2s',
                }}
                onClick={() => toggleSop(id)}
                role="button"
                tabIndex={0}
              >
                <span className={`sop-icon ${color}`}>
                  <Icon size={18} />
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{title}</strong>
                    <span
                      style={{
                        width: '18px',
                        height: '18px',
                        borderRadius: '5px',
                        border: '1px solid #c8d8dc',
                        display: 'grid',
                        placeItems: 'center',
                        background: isDone ? '#087f70' : '#fff',
                        color: '#fff',
                      }}
                    >
                      {isDone && <Check size={12} />}
                    </span>
                  </div>
                  <p>{detail}</p>
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </>
  )
}
