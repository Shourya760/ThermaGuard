// Application topbar with breadcrumb navigation, alert trigger, and status pill
import { useState } from 'react'
import { Bell, Menu } from 'lucide-react'
import NotificationModal from './NotificationModal'

export default function Topbar({
  currentPage,
  onOpenMobileNav,
  alerts = [],
  onNavigateAlerts,
  onDismissAlert,
  onClearAllAlerts,
  onNavigate,
  backendStatus = 'checking',
  backendZoneCount = 0
}) {
  const [showNotifications, setShowNotifications] = useState(false)

  return (
    <header className="topbar">
      <button
        type="button"
        className="mobile-menu"
        onClick={onOpenMobileNav}
        aria-label="Open navigation menu"
      >
        <Menu size={22} />
      </button>

      <div className="breadcrumb">
        <button
          type="button"
          onClick={() => onNavigate?.('Overview')}
          style={{ background: 'transparent', padding: 0, color: 'inherit', font: 'inherit', cursor: 'pointer' }}
        >
          Workspace
        </button>
        <span>/</span>
        <strong>{currentPage}</strong>
      </div>

      <div className="topbar-right" style={{ position: 'relative' }}>
        <span className={`status-pill ${backendStatus === 'offline' ? 'status-offline' : ''}`} title={backendStatus === 'online' ? `FastAPI is connected with ${backendZoneCount} pilot zones. Alert lists, forecasts and heat-risk scores remain illustrative frontend data.` : 'Start the FastAPI backend to load live weather'}>
          <span /> {backendStatus === 'online' ? 'FastAPI online · Live weather' : backendStatus === 'offline' ? 'API offline · Demo data' : 'Connecting to API…'}
        </span>

        <button
          type="button"
          className="icon-button"
          onClick={() => setShowNotifications(!showNotifications)}
          aria-label="Toggle notifications"
          title="Heat advisories"
        >
          <Bell size={19} />
          {alerts.length > 0 && <i />}
        </button>

        <div
          className="top-avatar"
          title="Urban Resilience Planning Team - Click for Settings"
          style={{ cursor: 'pointer' }}
          onClick={() => onNavigate?.('Settings')}
        >
          UR
        </div>

        <NotificationModal
          isOpen={showNotifications}
          onClose={() => setShowNotifications(false)}
          alerts={alerts}
          onNavigateAlerts={onNavigateAlerts}
          onDismissAlert={onDismissAlert}
          onClearAllAlerts={onClearAllAlerts}
        />
      </div>
    </header>
  )
}
