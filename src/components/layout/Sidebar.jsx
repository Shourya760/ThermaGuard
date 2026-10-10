// Navigation sidebar with workspace selector, navigation links, and resilience prompt
import { useEffect, useRef, useState } from 'react'
import {
  ChevronDown, Compass, Flame, SlidersHorizontal, Sparkles, X
} from 'lucide-react'
import { cities, navigationItems } from '../../data/mockData'

export default function Sidebar({
  currentPage,
  onNavigate,
  mobileOpen,
  onCloseMobile,
  selectedCity,
  onSelectCity,
  zonesCount = 6,
  alertsCount = 0
}) {
  const [cityDropdownOpen, setCityDropdownOpen] = useState(false)
  const citySelectRef = useRef(null)

  // Close city dropdown when clicking outside
  useEffect(() => {
    if (!cityDropdownOpen) return
    function handleClickOutside(e) {
      if (citySelectRef.current && !citySelectRef.current.contains(e.target)) {
        setCityDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [cityDropdownOpen])

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          className="mobile-overlay"
          onClick={onCloseMobile}
          aria-label="Close navigation overlay"
        />
      )}

      <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
        <div
          className="brand"
          style={{ cursor: 'pointer' }}
          onClick={() => {
            onNavigate('Overview')
            onCloseMobile()
          }}
          role="button"
          tabIndex={0}
        >
          <div className="brand-mark">
            <Flame size={24} fill="currentColor" />
          </div>
          <div>
            <strong>Therma<span>Guard</span></strong>
            <small>URBAN RESILIENCE</small>
          </div>
          <button
            type="button"
            className="close-nav"
            onClick={(e) => {
              e.stopPropagation()
              onCloseMobile()
            }}
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <div
          ref={citySelectRef}
          className="city-select"
          style={{ cursor: 'pointer', position: 'relative' }}
          onClick={() => setCityDropdownOpen(!cityDropdownOpen)}
          role="button"
          tabIndex={0}
        >
          <span className="city-symbol">
            <Compass size={18} />
          </span>
          <span>
            <strong>{selectedCity?.name || 'New Delhi, India'}</strong>
            <small>{selectedCity?.label || 'City monitoring'}</small>
          </span>
          <ChevronDown
            size={15}
            style={{
              transform: cityDropdownOpen ? 'rotate(180deg)' : 'none',
              transition: 'transform 0.2s'
            }}
          />

          {cityDropdownOpen && (
            <div
              className="city-dropdown-menu"
              onClick={(e) => e.stopPropagation()}
            >
              {cities.map((city) => (
                <button
                  key={city.id}
                  type="button"
                  className={`city-dropdown-item ${selectedCity?.id === city.id ? 'active' : ''}`}
                  onClick={() => {
                    onSelectCity?.(city)
                    setCityDropdownOpen(false)
                  }}
                >
                  <strong>{city.name}</strong>
                  <small>{city.label}</small>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="nav-label">MAIN MENU</div>
        <nav className="nav-list">
          {navigationItems.map(({ id, label, icon: Icon }) => {
            const isActive = currentPage === id
            const badgeCount =
              id === 'Heat explorer'
                ? zonesCount
                : id === 'Heat alerts'
                  ? alertsCount
                  : undefined

            return (
              <button
                key={id}
                type="button"
                onClick={() => {
                  onNavigate(id)
                  onCloseMobile()
                }}
                className={`nav-item ${isActive ? 'nav-active' : ''}`}
              >
                <Icon size={19} />
                <span>{label}</span>
                {badgeCount !== undefined && badgeCount > 0 && (
                  <span className="nav-count">{badgeCount}</span>
                )}
              </button>
            )
          })}
        </nav>

        <div className="sidebar-note">
          <div className="note-icon">
            <Sparkles size={19} />
          </div>
          <strong>Make every action count.</strong>
          <p>Explore risk zones and plan targeted heat interventions.</p>
          <button
            type="button"
            onClick={() => {
              onNavigate('Intervention planner')
              onCloseMobile()
            }}
          >
            Build an action plan <span>→</span>
          </button>
        </div>

        <div
          className="sidebar-bottom"
          style={{ cursor: 'pointer' }}
          onClick={() => {
            onNavigate('Settings')
            onCloseMobile()
          }}
          title="Open Settings"
        >
          <div className="profile-avatar">UR</div>
          <div className="profile-info">
            <strong>Urban Resilience Team</strong>
            <small>Planning workspace</small>
          </div>
          <SlidersHorizontal size={18} />
        </div>
      </aside>
    </>
  )
}
