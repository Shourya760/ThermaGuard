import { useEffect, useState } from 'react'
import { Calculator, Check, Save } from 'lucide-react'
import { evaluateScenario, getActionPlans, saveActionPlan } from '../services/api'

export default function BackendScenarioPanel({ zones = [], interventions = [], backendStatus = 'checking' }) {
  const [zoneId, setZoneId] = useState('')
  const [budget, setBudget] = useState(30000)
  const [planName, setPlanName] = useState('Heat resilience plan')
  const [selectedIds, setSelectedIds] = useState([])
  const [quantities, setQuantities] = useState({})
  const [result, setResult] = useState(null)
  const [plans, setPlans] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (backendStatus !== 'online') return undefined
    let active = true
    getActionPlans()
      .then((items) => { if (active) setPlans(items) })
      .catch(() => { if (active) setError('Could not load saved plans from FastAPI.') })
    return () => { active = false }
  }, [backendStatus])

  const targetZoneId = zoneId || zones[0]?.id || ''
  const requestBody = {
    zone_id: targetZoneId,
    budget: Number(budget),
    interventions: selectedIds.map((intervention_id) => ({
      intervention_id,
      quantity: Number(quantities[intervention_id] || 1),
    })),
  }

  const toggleIntervention = (id) => {
    setSelectedIds((current) => current.includes(id)
      ? current.filter((item) => item !== id)
      : [...current, id])
    setResult(null)
  }

  const handleEvaluate = async () => {
    setBusy(true)
    setError('')
    try {
      setResult(await evaluateScenario(requestBody))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  const handleSave = async () => {
    setBusy(true)
    setError('')
    try {
      const savedPlan = await saveActionPlan({ ...requestBody, name: planName })
      setResult(savedPlan)
      setPlans(await getActionPlans())
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel backend-scenario-panel">
      <div className="panel-heading">
        <div>
          <div className="panel-title"><Calculator size={18} /> FastAPI scenario planner</div>
          <p>Uses the backend zone records, intervention catalog, and server-calculated costs. Pilot zones are currently limited to Delhi.</p>
        </div>
      </div>

      {backendStatus !== 'online' ? (
        <p className="scenario-error">{backendStatus === 'offline' ? 'Start FastAPI to use server-backed scenario evaluation and saved plans.' : 'Connecting to FastAPI…'}</p>
      ) : zones.length === 0 || interventions.length === 0 ? (
        <p className="scenario-error">The backend is connected, but its pilot zones or intervention catalog are empty.</p>
      ) : (
        <>
          <div className="scenario-fields">
            <label>Backend pilot zone
              <select value={targetZoneId} onChange={(event) => { setZoneId(event.target.value); setResult(null) }}>
                {zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.name}, {zone.city}</option>)}
              </select>
            </label>
            <label>Budget (₹)
              <input type="number" min="1" value={budget} onChange={(event) => { setBudget(event.target.value); setResult(null) }} />
            </label>
            <label>Plan name
              <input value={planName} onChange={(event) => setPlanName(event.target.value)} />
            </label>
          </div>

          <div className="scenario-options">
            {interventions.map((item) => {
              const selected = selectedIds.includes(item.id)
              return (
                <div className={`scenario-option ${selected ? 'selected' : ''}`} key={item.id}>
                  <label>
                    <input type="checkbox" checked={selected} onChange={() => toggleIntervention(item.id)} />
                    <span><strong>{item.name}</strong><small>₹{item.unit_cost_inr.toLocaleString('en-IN')} / {item.unit}</small></span>
                  </label>
                  {selected && <input aria-label={`Quantity for ${item.name}`} type="number" min="0.1" step="1" value={quantities[item.id] || 1} onChange={(event) => setQuantities((current) => ({ ...current, [item.id]: event.target.value }))} />}
                </div>
              )
            })}
          </div>

          <div className="scenario-actions">
            <button className="secondary-button" type="button" disabled={busy || selectedIds.length === 0 || !targetZoneId} onClick={handleEvaluate}>Evaluate scenario</button>
            <button className="primary-button" type="button" disabled={busy || selectedIds.length === 0 || !targetZoneId || !planName.trim()} onClick={handleSave}><Save size={15} /> Save plan</button>
          </div>

          {error && <p className="scenario-error">{error}</p>}
          {result && (
            <div className="scenario-result">
              <strong>{result.is_feasible ? 'Within budget' : 'Over budget'} · ₹{result.total_estimated_cost.toLocaleString('en-IN')}</strong>
              <span>Budget remaining: ₹{result.remaining_budget.toLocaleString('en-IN')}</span>
              <p>{result.general_limitations?.join(' ') || 'Plan saved to the FastAPI database.'}</p>
            </div>
          )}

          <div className="saved-plans">
            <strong>Saved plans ({plans.length})</strong>
            {plans.slice(0, 3).map((plan) => <span key={plan.id}><Check size={13} /> {plan.name} · {plan.is_feasible ? 'Within budget' : 'Over budget'}</span>)}
          </div>
        </>
      )}
    </section>
  )
}
