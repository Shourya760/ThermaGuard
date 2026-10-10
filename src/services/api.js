const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })

  if (!response.ok) {
    let message = `API request failed (${response.status})`
    try {
      const body = await response.json()
      message = body.detail || message
    } catch {
      // Keep the status-based message when the response isn't JSON.
    }
    throw new Error(message)
  }

  return response.json()
}

export const getApiHealth = () => request('/api/health')
export const getApiZones = () => request('/api/zones')
export const getApiInterventions = () => request('/api/interventions')
export const getZoneWeather = (latitude, longitude) =>
  request(`/api/weather?lat=${encodeURIComponent(latitude)}&lon=${encodeURIComponent(longitude)}`)

export const getZoneRisk = (zoneId) =>
  request(`/api/zones/${encodeURIComponent(zoneId)}/risk`)

export const evaluateScenario = (scenario) =>
  request('/api/scenarios', { method: 'POST', body: JSON.stringify(scenario) })

export const saveActionPlan = (plan) =>
  request('/api/plans', { method: 'POST', body: JSON.stringify(plan) })

export const getActionPlans = () => request('/api/plans')
