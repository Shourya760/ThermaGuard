// Analytics & Reports page providing multi-day projections, vulnerability rankings, and data export
import { useEffect, useState } from 'react'
import { Calendar, CloudSun, Download, QrCode, TrendingUp } from 'lucide-react'
import QRCode from 'qrcode'
import TemperatureTrendChart from '../components/charts/TemperatureTrendChart'
import { convertTemp, formatTemp } from '../utils/tempUtils'

export default function AnalyticsReportsPage({
  zones = [],
  weeklyForecast = [],
  temperatureHistory = [],
  tempUnit = '°C',
  onSelectZone,
  onNavigate
}) {
  const [downloadSuccess, setDownloadSuccess] = useState(false)
  const [showQr, setShowQr] = useState(false)
  const [qrImage, setQrImage] = useState('')

  const rankedZones = [...zones].sort((a, b) => b.risk - a.risk)
  const highestRiskZone = rankedZones[0]
  const averageRisk = Math.round(
    zones.reduce((total, zone) => total + zone.risk, 0) / Math.max(zones.length, 1)
  )

  const reportSummary = `ThermaGuard Urban Heat Report | Average zone risk: ${averageRisk}/100 | Highest risk: ${highestRiskZone?.name || 'N/A'} (${highestRiskZone?.risk ?? 'N/A'}/100) | Zones monitored: ${zones.length}`
  const reportData = {
    title: 'ThermaGuard Urban Heat Report',
    summary: reportSummary,
    zones: rankedZones.map(({ name, risk, temp, canopyCover, populationExposure }) => ({
      name,
      risk,
      temp: formatTemp(temp, tempUnit),
      canopyCover,
      populationExposure,
    })),
    forecast: weeklyForecast.map(({ day, minTemp, maxTemp, riskLevel }) => ({
      day,
      tempRange: `${formatTemp(minTemp, tempUnit)} – ${formatTemp(maxTemp, tempUnit)}`,
      riskLevel,
    })),
  }

  let shareHref = ''
  if (typeof window !== 'undefined') {
    try {
      const u = new URL(window.location.href)
      u.searchParams.set('report', JSON.stringify(reportData))
      shareHref = u.href
    } catch {
      shareHref = ''
    }
  }

  useEffect(() => {
    if (!showQr || !shareHref) return
    QRCode.toDataURL(shareHref, { width: 220, margin: 2, errorCorrectionLevel: 'M' })
      .then(setQrImage)
      .catch(() => setQrImage(''))
  }, [showQr, shareHref])



  let sharedReport = null
  try {
    if (typeof window !== 'undefined') {
      const sharedData = new URLSearchParams(window.location.search).get('report')
      if (sharedData) sharedReport = JSON.parse(sharedData)
    }
  } catch {
    sharedReport = null
  }

  if (sharedReport?.title === 'ThermaGuard Urban Heat Report') {
    return (
      <section className="panel shared-report">
        <div className="eyebrow"><span className="eyebrow-line" /> SHARED REPORT</div>
        <h1>{sharedReport.title}</h1>
        <p className="welcome-subtitle">{sharedReport.summary}</p>
        <h2>Zone vulnerability</h2>
        <div className="table-responsive">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Risk</th>
                <th>Peak temp</th>
                <th>Tree canopy</th>
                <th>Population exposure</th>
              </tr>
            </thead>
            <tbody>
              {sharedReport.zones?.map((zone) => (
                <tr key={zone.name}>
                  <td>{zone.name}</td>
                  <td>{zone.risk}/100</td>
                  <td>{zone.temp}</td>
                  <td>{zone.canopyCover}</td>
                  <td>{zone.populationExposure}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <h2>7-day forecast</h2>
        <div className="table-responsive">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Day</th>
                <th>Temperature range</th>
                <th>Risk level</th>
              </tr>
            </thead>
            <tbody>
              {sharedReport.forecast?.map((day) => (
                <tr key={day.day}>
                  <td>{day.day}</td>
                  <td>{day.tempRange}</td>
                  <td>{day.riskLevel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <button
          className="secondary-button"
          type="button"
          onClick={() => {
            window.history.replaceState({}, '', window.location.pathname)
            window.location.reload()
          }}
        >
          Open dashboard
        </button>
      </section>
    )
  }

  // Generate downloadable HTML report with active temp unit
  const handleDownloadReport = () => {
    const zoneRows = rankedZones
      .map(
        (zone) =>
          `<tr><td>${zone.name}</td><td>${zone.risk}/100</td><td>${formatTemp(zone.temp, tempUnit)}</td><td>${zone.canopyCover}</td><td>${zone.populationExposure}</td></tr>`
      )
      .join('')

    const forecastRows = weeklyForecast
      .map(
        (day) =>
          `<tr><td>${day.day}</td><td>${formatTemp(day.minTemp, tempUnit)} – ${formatTemp(day.maxTemp, tempUnit)}</td><td>${day.riskLevel}</td></tr>`
      )
      .join('')

    const html = `<!doctype html><html><head><meta charset="utf-8"><title>ThermaGuard Heat Report</title><style>body{font:15px Arial,sans-serif;color:#203943;max-width:900px;margin:40px auto;padding:0 24px}h1{color:#087f70}h2{margin-top:32px}p{color:#617581}.summary{padding:18px;background:#eff8f5;border-radius:10px}table{width:100%;border-collapse:collapse;margin:16px 0}th,td{text-align:left;padding:10px;border-bottom:1px solid #dce6e8}th{background:#f4f7f8}@media print{body{margin:0 auto}}</style></head><body><h1>ThermaGuard Urban Heat Report</h1><p>Generated ${new Date().toLocaleString()}</p><div class="summary"><strong>City risk overview</strong><p>Average zone risk: ${averageRisk}/100 · Highest risk: ${highestRiskZone?.name || 'N/A'} (${highestRiskZone?.risk ?? 'N/A'}/100) · Zones monitored: ${zones.length}</p></div><h2>Zone vulnerability</h2><table><thead><tr><th>Zone</th><th>Risk</th><th>Peak temp</th><th>Tree canopy</th><th>Population exposure</th></tr></thead><tbody>${zoneRows}</tbody></table><h2>7-day forecast</h2><table><thead><tr><th>Day</th><th>Temperature range</th><th>Risk level</th></tr></thead><tbody>${forecastRows}</tbody></table><p>Prepared by ThermaGuard · Urban Resilience & Thermal Action Planning</p></body></html>`
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob([html], { type: 'text/html' }))
    link.download = `ThermaGuard_Heat_Report_${new Date().toISOString().slice(0, 10)}.html`
    link.click()
    URL.revokeObjectURL(link.href)
    setDownloadSuccess(true)
    setTimeout(() => setDownloadSuccess(false), 3000)
  }

  // Export full risk report as CSV
  const handleExportCSV = () => {
    const headers = [
      'Zone Name',
      'Risk Score',
      `Temperature (${tempUnit})`,
      'Humidity',
      'Population Exposure',
      'Canopy Cover',
      'Cooling Centres',
    ]
    const rows = zones.map((z) => [
      `"${z.name}"`,
      z.risk,
      convertTemp(z.temp, tempUnit),
      `"${z.humidity}"`,
      `"${z.populationExposure}"`,
      `"${z.canopyCover}"`,
      z.coolingCentres ?? 1,
    ])

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute(
      'download',
      `ThermaGuard_Urban_Heat_Report_${new Date().toISOString().split('T')[0]}.csv`
    )
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    setDownloadSuccess(true)
    setTimeout(() => setDownloadSuccess(false), 3000)
  }

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> CLIMATE ANALYTICS & PROJECTIONS
          </div>
          <h1>Analytics & reports</h1>
          <p className="welcome-subtitle">
            Historical diurnal profiles, 7-day heatwave projections, and zone vulnerability rankings.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="secondary-button"
            onClick={() => setShowQr((visible) => !visible)}
          >
            <QrCode size={15} /> Share summary
          </button>
          <button
            type="button"
            className="primary-button"
            onClick={handleExportCSV}
          >
            <Download size={15} /> Export CSV
          </button>
          <button
            type="button"
            className="primary-button"
            onClick={handleDownloadReport}
          >
            <Download size={15} /> Download HTML Report
          </button>
        </div>
      </section>

      {showQr && (
        <section className="panel report-qr-panel" style={{ marginBottom: '18px' }}>
          <div>
            <div className="panel-title">
              <QrCode size={18} /> Scan to read report summary
            </div>
            <p className="panel-description">
              The QR code contains this snapshot as text and can be scanned from a phone camera.
            </p>
            <p className="report-qr-summary">{reportSummary}</p>
          </div>
          {qrImage ? (
            <img
              className="report-qr-image"
              src={qrImage}
              alt="QR code linking to this full heat report"
            />
          ) : (
            <span className="panel-description">Generating QR code…</span>
          )}
        </section>
      )}

      {downloadSuccess && (
        <div className="saved-message" style={{ marginBottom: '18px' }}>
          Report exported successfully to your downloads!
        </div>
      )}

      {/* 7-Day Forecast Cards */}
      <section className="panel" style={{ marginBottom: '18px' }}>
        <div className="panel-heading">
          <div>
            <div className="panel-title">
              <Calendar size={18} /> 7-Day Summer Heat Forecast
            </div>
            <p>Predicted daily highs and heatwave risk levels</p>
          </div>
          <span className="chart-unit">FORECAST MODEL · WRF-URBAN</span>
        </div>

        <div className="forecast-grid">
          {weeklyForecast.map((item) => (
            <div key={item.day} className={`forecast-card ${item.riskLevel.toLowerCase()}`}>
              <span className="forecast-day">{item.day}</span>
              <CloudSun size={24} className="forecast-icon" />
              <div className="forecast-temp">
                <strong>{convertTemp(item.maxTemp, tempUnit)}°</strong>
                <span>/ {convertTemp(item.minTemp, tempUnit)}°</span>
              </div>
              <span className={`forecast-badge ${item.riskLevel.toLowerCase()}`}>
                {item.riskLevel}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 24-hr temperature trend curve */}
      <TemperatureTrendChart
        data={temperatureHistory}
        unit={tempUnit}
        title="24-Hour Diurnal Temperature Profile vs Heat Index"
        subtitle="Comparing measured ambient dry-bulb temperature against humidity-adjusted heat index"
      />

      {/* Zone Vulnerability Matrix Table */}
      <section className="panel" style={{ marginTop: '18px' }}>
        <div className="panel-heading">
          <div>
            <div className="panel-title">
              <TrendingUp size={18} /> Zone Vulnerability Comparison Matrix
            </div>
            <p>Ranked index of all monitored municipal sectors (click row to explore zone)</p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Risk Score</th>
                <th>Peak Temp</th>
                <th>Tree Canopy</th>
                <th>Population Exposure</th>
                <th>Cooling Centers</th>
              </tr>
            </thead>
            <tbody>
              {rankedZones.map((zone) => (
                <tr
                  key={zone.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => {
                    onSelectZone?.(zone)
                    onNavigate?.('Heat explorer')
                  }}
                  title="Click to view in Heat Explorer"
                >
                  <td>
                    <div className="zone-td-title">
                      <span className="zone-dot" style={{ background: zone.color }} />
                      <strong>{zone.name}</strong>
                    </div>
                  </td>
                  <td>
                    <span
                      className="risk-score-pill"
                      style={{ color: zone.color, background: `${zone.color}15` }}
                    >
                      {zone.risk} / 100
                    </span>
                  </td>
                  <td>
                    <b>{formatTemp(zone.temp, tempUnit)}</b>
                  </td>
                  <td>{zone.canopyCover}</td>
                  <td>{zone.populationExposure}</td>
                  <td>{zone.coolingCentres ?? 1} available</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}
