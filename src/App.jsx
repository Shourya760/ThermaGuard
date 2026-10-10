// Main application shell managing routing, global state, and layout orchestration
import { useEffect, useState } from 'react'
import Sidebar from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'
import Footer from './components/layout/Footer'
import OverviewPage from './pages/OverviewPage'
import HeatExplorerPage from './pages/HeatExplorerPage'
import InterventionPlannerPage from './pages/InterventionPlannerPage'
import HeatAlertsPage from './pages/HeatAlertsPage'
import AnalyticsReportsPage from './pages/AnalyticsReportsPage'
import SettingsPage from './pages/SettingsPage'
import { getApiHealth, getApiInterventions, getApiZones, getZoneWeather } from './services/api'
import {
  cities, cityAlerts, cityHourlyHistory, cityZones,
  defaultInterventions, weeklyForecast
} from './data/mockData'
import './App.css'

export default function App() {
  const [page, setPage] = useState(() => {
    if (typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('report')) {
      return 'Analytics & reports'
    }
    return 'Overview'
  })
  const [mobileNav, setMobileNav] = useState(false)

  const [selectedCity, setSelectedCity] = useState(cities[0])
  const currentZones = cityZones[selectedCity.id] || cityZones.delhi
  const [selectedZone, setSelectedZone] = useState(currentZones[0])
  const [tempUnit, setTempUnit] = useState('°C')
  const [alertThreshold, setAlertThreshold] = useState(42)
  const [interventions, setInterventions] = useState(defaultInterventions)
  const [activeAlerts, setActiveAlerts] = useState(cityAlerts[selectedCity.id] || cityAlerts.delhi)
  const [backendStatus, setBackendStatus] = useState('checking')
  const [backendZoneCount, setBackendZoneCount] = useState(0)
  const [backendZones, setBackendZones] = useState([])
  const [backendInterventions, setBackendInterventions] = useState([])
  const [weatherResult, setWeatherResult] = useState(null)
  const [weatherFailure, setWeatherFailure] = useState(null)

  useEffect(() => {
    let active = true
    Promise.all([getApiHealth(), getApiZones(), getApiInterventions()])
      .then(([, apiZones, apiInterventions]) => {
        if (!active) return
        setBackendZoneCount(apiZones.length)
        setBackendZones(apiZones)
        setBackendInterventions(apiInterventions)
        setBackendStatus('online')
      })
      .catch(() => {
        if (active) setBackendStatus('offline')
      })
    return () => { active = false }
  }, [])

  const selectedLatitude = selectedZone?.position?.[0]
  const selectedLongitude = selectedZone?.position?.[1]

  useEffect(() => {
    if (selectedLatitude == null || selectedLongitude == null) return undefined
    let active = true
    const key = `${selectedLatitude},${selectedLongitude}`
    getZoneWeather(selectedLatitude, selectedLongitude)
      .then((weather) => { if (active) setWeatherResult({ key, weather }) })
      .catch((error) => { if (active) setWeatherFailure({ key, message: error.message }) })
    return () => { active = false }
  }, [selectedLatitude, selectedLongitude])

  const selectedWeatherKey = `${selectedLatitude},${selectedLongitude}`
  const currentWeather = weatherResult?.key === selectedWeatherKey ? weatherResult.weather : null
  const weatherError = weatherFailure?.key === selectedWeatherKey ? weatherFailure.message : ''

  const currentHistory = cityHourlyHistory[selectedCity.id] || cityHourlyHistory.delhi

  const handleSelectCity = (city) => {
    setSelectedCity(city)
    const newZones = cityZones[city.id] || cityZones.delhi
    setSelectedZone(newZones[0])
    setActiveAlerts(cityAlerts[city.id] || cityAlerts.delhi)
  }

  const handleNavigate = (pageName) => {
    setPage(pageName)
    setMobileNav(false)
  }

  const handleAddIntervention = (newItem) => {
    setInterventions((prev) => [newItem, ...prev])
  }

  const handleDismissAlert = (alertId) => {
    setActiveAlerts((prev) => prev.filter((a) => a.id !== alertId))
  }

  const handleClearAllAlerts = () => {
    setActiveAlerts([])
  }

  return (
    <div className="app-shell">
      <Sidebar
        currentPage={page}
        onNavigate={handleNavigate}
        mobileOpen={mobileNav}
        onCloseMobile={() => setMobileNav(false)}
        selectedCity={selectedCity}
        onSelectCity={handleSelectCity}
        zonesCount={currentZones.length}
        alertsCount={activeAlerts.length}
      />

      <main className="main-content">
        <Topbar
          currentPage={page}
          onOpenMobileNav={() => setMobileNav(true)}
          alerts={activeAlerts}
          onNavigateAlerts={() => handleNavigate('Heat alerts')}
          onDismissAlert={handleDismissAlert}
          onClearAllAlerts={handleClearAllAlerts}
          onNavigate={handleNavigate}
          backendStatus={backendStatus}
          backendZoneCount={backendZoneCount}
        />

        <div className="page-content">
          {page === 'Overview' && (
            <OverviewPage
              zones={currentZones}
              selectedZone={selectedZone}
              selectedCity={selectedCity}
              onSelectZone={setSelectedZone}
              temperatureHistory={currentHistory}
              tempUnit={tempUnit}
              currentWeather={currentWeather}
              weatherError={weatherError}
              onNavigate={handleNavigate}
            />
          )}

          {page === 'Heat explorer' && (
            <HeatExplorerPage
              zones={currentZones}
              selectedZone={selectedZone}
              selectedCity={selectedCity}
              tempUnit={tempUnit}
              currentWeather={currentWeather}
              weatherError={weatherError}
              onSelectZone={setSelectedZone}
              onNavigate={handleNavigate}
            />
          )}

          {page === 'Intervention planner' && (
            <InterventionPlannerPage
              interventions={interventions}
              backendZones={backendZones}
              backendInterventions={backendInterventions}
              backendStatus={backendStatus}
              onAddIntervention={handleAddIntervention}
              selectedZone={selectedZone}
              zones={currentZones}
              onSelectZone={setSelectedZone}
            />
          )}

          {page === 'Heat alerts' && (
            <HeatAlertsPage
              alerts={activeAlerts}
              zones={currentZones}
              tempUnit={tempUnit}
              onSelectZone={setSelectedZone}
              onDismissAlert={handleDismissAlert}
              onNavigate={handleNavigate}
            />
          )}

          {page === 'Analytics & reports' && (
            <AnalyticsReportsPage
              zones={currentZones}
              weeklyForecast={weeklyForecast}
              temperatureHistory={currentHistory}
              tempUnit={tempUnit}
              onSelectZone={setSelectedZone}
              onNavigate={handleNavigate}
            />
          )}

          {page === 'Settings' && (
            <SettingsPage
              selectedCity={selectedCity}
              onSelectCity={handleSelectCity}
              tempUnit={tempUnit}
              onToggleTempUnit={setTempUnit}
              alertThreshold={alertThreshold}
              onUpdateAlertThreshold={setAlertThreshold}
            />
          )}

          <Footer />
        </div>
      </main>
    </div>
  )
}
