// Interactive notifications dropdown for active heat advisories & system events
import { useEffect, useRef } from 'react'
import { AlertTriangle, Check, X } from 'lucide-react'

export default function NotificationModal({
  isOpen,
  onClose,
  alerts = [],
  onNavigateAlerts,
  onDismissAlert,
  onClearAllAlerts
}) {
  const dropdownRef = useRef(null)

  // Close when clicking outside
  useEffect(() => {
    if (!isOpen) return
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="notification-dropdown" ref={dropdownRef}>
      <div className="notification-header">
        <div className="notification-title">
          <AlertTriangle size={16} />
          <strong>Heat Advisories ({alerts.length})</strong>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {alerts.length > 0 && onClearAllAlerts && (
            <button
              type="button"
              className="text-button"
              style={{ fontSize: '10px', padding: 0 }}
              onClick={onClearAllAlerts}
            >
              Clear all
            </button>
          )}
          <button
            type="button"
            className="notification-close"
            onClick={onClose}
            aria-label="Close alerts"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      <div className="notification-body">
        {alerts.length === 0 ? (
          <p className="notification-empty">All alerts acknowledged. No active warnings.</p>
        ) : (
          alerts.map((item) => (
            <div key={item.id} className={`notification-item ${item.severity}`}>
              <div className="notification-item-top">
                <span className="notification-badge">{item.severity.toUpperCase()}</span>
                <span className="notification-time">{item.issued}</span>
              </div>
              <strong className="notification-item-title">{item.title}</strong>
              <p className="notification-item-desc">{item.message}</p>
              {onDismissAlert && (
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '6px' }}>
                  <button
                    type="button"
                    className="text-button"
                    style={{ fontSize: '10px', display: 'flex', alignItems: 'center', gap: '3px' }}
                    onClick={() => onDismissAlert(item.id)}
                  >
                    <Check size={12} /> Acknowledge
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="notification-footer">
        <button
          type="button"
          className="text-button"
          onClick={() => {
            onClose()
            onNavigateAlerts?.()
          }}
        >
          View all heat advisories <span>→</span>
        </button>
      </div>
    </div>
  )
}
