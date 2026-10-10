// Reusable metric card displaying KPIs, directional trends, and semantic icons
import { ArrowDownRight, ArrowUpRight } from 'lucide-react'

export default function StatCard({ title, value, unit, change, icon: Icon, tone = 'tone-red', subtitle }) {
  const isPositive = change?.startsWith('+')

  return (
    <article className="stat-card">
      <div className="stat-top">
        <span className={`stat-icon ${tone}`} aria-hidden="true">
          <Icon size={19} />
        </span>
        {change && (
          <span className={`trend ${isPositive ? 'trend-up' : 'trend-down'}`}>
            {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
            {change}
          </span>
        )}
      </div>
      <p className="stat-title">{title}</p>
      <div className="stat-value">
        {value}
        {unit && <span>{unit}</span>}
      </div>
      {subtitle && <p className="stat-subtitle">{subtitle}</p>}
    </article>
  )
}
