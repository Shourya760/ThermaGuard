// Interactive Area chart showing diurnal temperature curve and heat index metrics
import { useState } from 'react'
import { Activity } from 'lucide-react'
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'
import { convertTemp } from '../../utils/tempUtils'

export default function TemperatureTrendChart({
  data = [],
  title = 'Daily temperature profile',
  subtitle = 'Illustrative temperature curve for a hot day',
  unit = '°C'
}) {
  const [showHeatIndex, setShowHeatIndex] = useState(false)

  // Map temperatures according to active unit (°C or °F)
  const chartData = data.map((d) => ({
    ...d,
    displayTemp: convertTemp(d.temp, unit),
    displayHeatIndex: d.heatIndex ? convertTemp(d.heatIndex, unit) : undefined,
  }))

  const yDomain = unit === '°F' ? [70, 125] : [25, 52]

  return (
    <section className="panel trend-panel">
      <div className="panel-heading">
        <div>
          <div className="panel-title">
            <Activity size={18} /> {title}
          </div>
          <p>{subtitle}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {data?.[0]?.heatIndex && (
            <button
              type="button"
              className="text-button"
              style={{ fontSize: '11px', textDecoration: showHeatIndex ? 'underline' : 'none' }}
              onClick={() => setShowHeatIndex(!showHeatIndex)}
            >
              {showHeatIndex ? 'Hide Heat Index' : '+ Show Heat Index'}
            </button>
          )}
          <span className="chart-unit">TEMPERATURE · {unit}</span>
        </div>
      </div>

      <div className="chart-area">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="heatFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f97352" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#f97352" stopOpacity={0.01} />
              </linearGradient>
              <linearGradient id="heatIndexFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#edf1f4" strokeDasharray="4 5" vertical={false} />
            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#8a9aa6', fontSize: 11 }}
              dy={10}
            />
            <YAxis
              domain={yDomain}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#8a9aa6', fontSize: 11 }}
            />
            <Tooltip
              formatter={(val, name) => [`${val} ${unit}`, name]}
              contentStyle={{
                borderRadius: 12,
                border: '1px solid #e6edf0',
                fontSize: 12,
                boxShadow: '0 4px 12px rgba(0,0,0,0.06)'
              }}
            />
            <Area
              type="monotone"
              dataKey="displayTemp"
              name={`Ambient Temp (${unit})`}
              stroke="#f06a4f"
              strokeWidth={3}
              fill="url(#heatFill)"
              dot={{ r: 3, fill: '#f06a4f', strokeWidth: 0 }}
              activeDot={{ r: 5 }}
            />
            {showHeatIndex && (
              <Area
                type="monotone"
                dataKey="displayHeatIndex"
                name={`Feels Like (${unit})`}
                stroke="#dc2626"
                strokeWidth={2}
                strokeDasharray="4 4"
                fill="url(#heatIndexFill)"
                dot={{ r: 2, fill: '#dc2626', strokeWidth: 0 }}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
