// Intervention Planner page for allocating municipal cooling budgets and prioritizing heat mitigation actions
import { useState } from 'react'
import {
  Check, Download, MapPin, Plus, RotateCcw,
  ShieldCheck, SlidersHorizontal, Sparkles, X
} from 'lucide-react'
import BackendScenarioPanel from '../components/BackendScenarioPanel'

// Helper function to export plan outside component scope
function exportPlanAsJson(selectedZone, budget, totalCost, totalReduction, chosen) {
  const planData = {
    targetZone: selectedZone?.name || 'All Zones',
    date: new Date().toISOString().split('T')[0],
    budget,
    totalCost,
    budgetRemaining: budget - totalCost,
    estimatedRiskReduction: `${totalReduction}%`,
    selectedInterventionsCount: chosen.length,
    actions: chosen.map((c) => ({
      title: c.title,
      cost: c.cost,
      reduction: `${c.reduction}%`,
      impactTier: c.impact || 'Standard',
    })),
  }

  const blob = new Blob([JSON.stringify(planData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ThermaGuard_Action_Plan_${(selectedZone?.name || 'Urban').replace(/\s+/g, '_')}.json`
  a.click()
  URL.revokeObjectURL(url)
}

export default function InterventionPlannerPage({
  interventions = [],
  onAddIntervention,
  selectedZone,
  zones = [],
  onSelectZone,
  backendZones = [],
  backendInterventions = [],
  backendStatus = 'checking'
}) {
  const [budget, setBudget] = useState(6000)
  const [selectedActions, setSelectedActions] = useState([1, 2])
  const [saved, setSaved] = useState(false)
  const [showCustomModal, setShowCustomModal] = useState(false)

  // Custom intervention form state
  const [newTitle, setNewTitle] = useState('')
  const [newDetail, setNewDetail] = useState('')
  const [newCost, setNewCost] = useState('2000')
  const [newReduction, setNewReduction] = useState('10')

  // Selected interventions calculation
  const chosen = interventions.filter((item) => selectedActions.includes(item.id))
  const totalCost = chosen.reduce((sum, item) => sum + item.cost, 0)
  const totalReduction = chosen.reduce((sum, item) => sum + item.reduction, 0)
  const withinBudget = totalCost <= budget

  // Toggle selection of an action
  const toggleAction = (id) => {
    setSelectedActions((old) =>
      old.includes(id) ? old.filter((item) => item !== id) : [...old, id]
    )
    setSaved(false)
  }

  // Quick action filters
  const handleSelectAll = () => {
    setSelectedActions(interventions.map((i) => i.id))
    setSaved(false)
  }

  const handleClearAll = () => {
    setSelectedActions([])
    setSaved(false)
  }

  const handleResetDefaults = () => {
    setSelectedActions([1, 2])
    setBudget(6000)
    setSaved(false)
  }

  // Handle adding custom intervention
  const handleCreateCustom = (e) => {
    e.preventDefault()
    if (!newTitle.trim()) return

    const newId = interventions.length + 101
    const customItem = {
      id: newId,
      title: newTitle.trim(),
      detail: newDetail.trim() || 'Custom community resilience intervention',
      icon: Sparkles,
      cost: Number(newCost) || 2000,
      reduction: Number(newReduction) || 10,
      impact: 'Custom',
      color: 'green',
    }

    onAddIntervention?.(customItem)
    setSelectedActions((prev) => [...prev, newId])
    setShowCustomModal(false)
    setNewTitle('')
    setNewDetail('')
    setSaved(false)
  }

  // Export plan as JSON
  const handleExportPlan = () => {
    exportPlanAsJson(selectedZone, budget, totalCost, totalReduction, chosen)
  }

  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> ACTION ALLOCATION & BUDGETING
          </div>
          <h1>Intervention planner</h1>
          <p className="welcome-subtitle">
            Turn local heat risks into practical, budget-aware action plans for{' '}
            <strong>{selectedZone?.name || 'urban zones'}</strong>.
          </p>
        </div>

        {/* Target zone switcher directly inside the planner */}
        {zones.length > 0 && onSelectZone && (
          <div className="date-pill" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={16} style={{ color: selectedZone?.color || '#087f70' }} />
            <span>Target:</span>
            <select
              value={selectedZone?.id}
              onChange={(e) => {
                const z = zones.find((item) => item.id === Number(e.target.value))
                if (z) onSelectZone(z)
              }}
              style={{
                border: 'none',
                background: 'transparent',
                fontWeight: 700,
                color: '#1a3a46',
                outline: 'none',
                cursor: 'pointer',
              }}
              aria-label="Target zone"
            >
              {zones.map((z) => (
                <option key={z.id} value={z.id}>
                  {z.name} (Risk: {z.risk})
                </option>
              ))}
            </select>
          </div>
        )}
      </section>

      <section className="planner-layout">
        {/* Intervention action list */}
        <article className="panel planner-panel">
          <div className="panel-heading">
            <div>
              <div className="panel-title">
                <Sparkles size={18} /> Recommended interventions
              </div>
              <p>Select actions to compare your plan</p>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="text-button"
                style={{ fontSize: '10px' }}
                onClick={handleSelectAll}
              >
                Select all
              </button>
              <button
                type="button"
                className="text-button"
                style={{ fontSize: '10px' }}
                onClick={handleClearAll}
              >
                Clear
              </button>
              <button
                type="button"
                className="text-button"
                onClick={() => setShowCustomModal(true)}
                title="Add custom action"
              >
                <Plus size={14} /> Add Action
              </button>
            </div>
          </div>

          <div className="action-list">
            {interventions.map(({ id, title, detail, icon: Icon, cost, reduction, color }) => {
              const isSelected = selectedActions.includes(id)
              return (
                <button
                  key={id}
                  type="button"
                  className={`action-option ${isSelected ? 'action-selected' : ''}`}
                  onClick={() => toggleAction(id)}
                >
                  <span className={`action-icon action-${color}`}>
                    <Icon size={21} />
                  </span>
                  <span className="action-copy">
                    <strong>{title}</strong>
                    <small>{detail}</small>
                    <span className="action-meta">
                      <b>₹{cost.toLocaleString('en-IN')}</b>
                      <span>Est. risk reduction: {reduction}%</span>
                    </span>
                  </span>
                  <span className={`action-check ${isSelected ? 'checked' : ''}`}>
                    {isSelected && <Check size={14} />}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Custom intervention inline creator modal */}
          {showCustomModal && (
            <div className="custom-action-card">
              <div className="custom-action-header">
                <strong>Create custom intervention</strong>
                <button
                  type="button"
                  onClick={() => setShowCustomModal(false)}
                  className="close-nav"
                  style={{ display: 'block' }}
                >
                  <X size={16} />
                </button>
              </div>
              <form onSubmit={handleCreateCustom} className="custom-action-form">
                <input
                  type="text"
                  placeholder="Intervention title (e.g. Misting station canopy)"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
                <input
                  type="text"
                  placeholder="Details (e.g. Install at central bus stands)"
                  value={newDetail}
                  onChange={(e) => setNewDetail(e.target.value)}
                />
                <div className="form-row">
                  <div>
                    <label>Cost (₹)</label>
                    <input
                      type="number"
                      value={newCost}
                      onChange={(e) => setNewCost(e.target.value)}
                      min="500"
                      step="100"
                    />
                  </div>
                  <div>
                    <label>Risk Reduction (%)</label>
                    <input
                      type="number"
                      value={newReduction}
                      onChange={(e) => setNewReduction(e.target.value)}
                      min="1"
                      max="50"
                    />
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                  <button type="submit" className="primary-button" style={{ flex: 1 }}>
                    <Plus size={15} /> Add to Plan
                  </button>
                  <button
                    type="button"
                    className="text-button"
                    onClick={() => setShowCustomModal(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </article>

        {/* Budget calculation & comparison summary */}
        <article className="panel budget-panel">
          <div className="panel-title">
            <SlidersHorizontal size={18} /> Budget & comparison
          </div>
          <p className="panel-description">Adjust your illustrative budget to see which actions fit.</p>

          <div className="budget-amount">
            <span>Total available budget</span>
            <strong>₹{budget.toLocaleString('en-IN')}</strong>
          </div>

          {/* Quick budget tier pills */}
          <div style={{ display: 'flex', gap: '6px', marginTop: '12px' }}>
            {[3000, 6000, 9000, 12000].map((tier) => (
              <button
                key={tier}
                type="button"
                className={`filter-pill ${budget === tier ? 'active' : ''}`}
                style={{ fontSize: '9px', padding: '4px 8px' }}
                onClick={() => {
                  setBudget(tier)
                  setSaved(false)
                }}
              >
                ₹{(tier / 1000)}k
              </button>
            ))}
          </div>

          <input
            className="budget-slider"
            type="range"
            min="1000"
            max="12000"
            step="500"
            value={budget}
            onChange={(event) => {
              setBudget(Number(event.target.value))
              setSaved(false)
            }}
            aria-label="Available budget"
          />
          <div className="slider-labels">
            <span>₹1,000</span>
            <span>₹12,000</span>
          </div>

          <div className="budget-divider" />

          <div className="budget-line">
            <span>Selected actions</span>
            <strong>{chosen.length} of {interventions.length}</strong>
          </div>
          <div className="budget-line">
            <span>Combined risk reduction</span>
            <strong className="positive-value">~{totalReduction}%</strong>
          </div>
          <div className="budget-line">
            <span>Estimated total cost</span>
            <strong>₹{totalCost.toLocaleString('en-IN')}</strong>
          </div>
          <div className="budget-line">
            <span>Budget remaining</span>
            <strong className={withinBudget ? 'positive-value' : 'negative-value'}>
              {withinBudget
                ? `₹${(budget - totalCost).toLocaleString('en-IN')}`
                : `₹${(totalCost - budget).toLocaleString('en-IN')} over`}
            </strong>
          </div>

          <div className={`budget-status ${withinBudget ? '' : 'budget-over'}`}>
            <ShieldCheck size={18} />
            <span>
              {withinBudget ? 'Within budget' : 'Over budget'}
              <small>
                {withinBudget
                  ? 'Selected actions fit your planning budget.'
                  : 'Remove an action or increase the budget.'}
              </small>
            </span>
          </div>

          <button
            type="button"
            className="primary-button full-button"
            disabled={chosen.length === 0 || !withinBudget}
            onClick={() => setSaved(true)}
          >
            <Check size={17} /> Save action plan
          </button>

          {saved && (
            <div style={{ marginTop: '12px' }}>
              <div className="saved-message">
                <Check size={16} /> Plan saved for this session.
              </div>
              <button
                type="button"
                className="text-button"
                style={{ width: '100%', marginTop: '6px', textAlign: 'center', justifyContent: 'center' }}
                onClick={handleExportPlan}
              >
                <Download size={14} /> Download Action Plan JSON
              </button>
            </div>
          )}

          <div style={{ marginTop: '14px', textAlign: 'center' }}>
            <button
              type="button"
              className="text-button"
              style={{ fontSize: '10px', color: '#8898a3' }}
              onClick={handleResetDefaults}
            >
              <RotateCcw size={11} /> Reset planner defaults
            </button>
          </div>

          <p className="estimate-note">
            Costs and impact estimates are illustrative. Actual municipal outcomes require validated local data and cost assumptions.
          </p>
        </article>
      </section>

      <BackendScenarioPanel zones={backendZones} interventions={backendInterventions} backendStatus={backendStatus} />
    </>
  )
}
