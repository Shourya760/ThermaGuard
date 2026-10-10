// Overview page displaying high-level resilience metrics, interactive map, and diurnal temperature trend
import { CloudSun, Flame, ShieldCheck, Users, MapPinned } from 'lucide-react'
import StatCard from '../components/common/StatCard'
import NoticeBanner from '../components/common/NoticeBanner'
import HeatMap from '../components/map/HeatMap'
import ZoneRiskPanel from '../components/map/ZoneRiskPanel'
import TemperatureTrendChart from '../components/charts/TemperatureTrendChart'
import { convertTemp } from '../utils/tempUtils'

export default function OverviewPage({
  zones = [],
  selectedZone,
  selectedCity,
  onSelectZone,
  temperatureHistory = [],
  tempUnit = '°C',
  currentWeather,
  weatherError,
  onNavigate
}) {
  // Compute dynamic stats based on active city's monitored zones
  const highRiskCount = zones.filter((z) => z.risk >= 70).length
  const peakTemp = zones.length > 0 ? Math.max(...zones.map((z) => z.temp)) : 43.2
  const displayPeak = convertTemp(peakTemp, tempUnit)

  return (
    <>
      {/* Header title and illustrative scenario badge */}
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> HEAT ACTION INTELLIGENCE
          </div>
          <h1>Beat the heat, together.</h1>
          <p className="welcome-subtitle">
            Understand urban heat risk in <strong>{selectedCity?.name || 'monitored regions'}</strong>. Prioritise communities. Plan smarter interventions.
          </p>
        </div>
        <div className="date-pill">
          <CloudSun size={19} />
          <span>{selectedCity?.name ? `${selectedCity.name} · Summer Scenario` : 'Illustrative summer scenario'}</span>
        </div>
      </section>

      {/* Prototype notice banner */}
      <NoticeBanner message={`Real-time simulation for ${selectedCity?.name || 'urban workspace'}. Zone metrics model thermal microclimates.`} />

      {/* Dynamic KPI statistics */}
      <section className="stats-grid">
        <StatCard
          title="Zones at high risk"
          value={highRiskCount}
          unit={`/ ${zones.length}`}
          change="+1"
          icon={Flame}
          tone="tone-red"
          subtitle="Illustrative risk classification"
        />
        <StatCard
          title="Peak zone temperature"
          value={displayPeak}
          unit={tempUnit}
          change="+2.4°"
          icon={CloudSun}
          tone="tone-orange"
          subtitle="Afternoon peak scenario"
        />
        <StatCard
          title="Population to prioritise"
          value="24.8"
          unit="k"
          change="+8%"
          icon={Users}
          tone="tone-purple"
          subtitle="Illustrative planning estimate"
        />
        <StatCard
          title="Intervention coverage"
          value="68"
          unit="%"
          change="-4%"
          icon={ShieldCheck}
          tone="tone-green"
          subtitle="Example planning baseline"
        />
      </section>

      {/* Overview grid: Map on left, Selected zone indicators on right */}
      <section className="overview-grid">
        <article className="panel map-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <MapPinned size={18} /> Heat-risk explorer
              </div>
              <p>Choose a zone to inspect its risk profile</p>
            </div>
            <button
              type="button"
              className="text-button"
              onClick={() => onNavigate('Heat explorer')}
            >
              Explore map <span>→</span>
            </button>
          </div>
          <HeatMap
            zones={zones}
            selectedZoneId={selectedZone?.id}
            onSelect={onSelectZone}
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

      {/* Diurnal temperature profile area chart */}
      <TemperatureTrendChart
        data={temperatureHistory}
        unit={tempUnit}
        title={`Daily temperature profile · ${selectedCity?.name || 'Monitoring zone'}`}
      />
    </>
  )
}
