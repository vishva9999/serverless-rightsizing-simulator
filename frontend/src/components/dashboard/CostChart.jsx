import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { DollarSign } from 'lucide-react'
import { costComparisonData } from '../../data/mockData'

/** Custom tooltip for the cost chart */
function CostTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl p-3 text-sm"
      style={{ background: 'rgba(10,14,26,0.95)', border: '1px solid rgba(99,102,241,0.3)' }}>
      <p className="font-semibold text-white mb-2">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: p.color }} />
          <span style={{ color: '#94a3b8' }}>{p.name}:</span>
          <span className="font-medium text-white">${p.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

/**
 * CostChart — grouped bar chart comparing current vs. optimized monthly cost.
 * Data: mockData.costComparisonData (Phase 1 synthetic values).
 */
export default function CostChart() {
  return (
    <div className="glass-card p-5 animate-slide-up" style={{ animationDelay: '200ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'rgba(99,102,241,0.15)' }}>
            <DollarSign size={16} style={{ color: '#6366f1' }} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Cost Comparison</h3>
            <p className="text-xs" style={{ color: '#64748b' }}>Current vs. Optimized (USD/mo)</p>
          </div>
        </div>
        <span className="text-xs px-2 py-1 rounded-full"
          style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.25)' }}>
          Mock Data
        </span>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={costComparisonData} barCategoryGap="30%" barGap={4}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
          <XAxis
            dataKey="month"
            tick={{ fill: '#64748b', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(99,102,241,0.15)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`}
          />
          <Tooltip content={<CostTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '12px', color: '#94a3b8', paddingTop: '8px' }}
          />
          <Bar dataKey="current"   name="Current"   fill="#6366f1" radius={[4, 4, 0, 0]}
            fillOpacity={0.9} />
          <Bar dataKey="optimized" name="Optimized" fill="#22d3ee" radius={[4, 4, 0, 0]}
            fillOpacity={0.85} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
