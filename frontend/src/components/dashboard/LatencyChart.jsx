import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Clock } from 'lucide-react'
import { latencyTrendData } from '../../data/mockData'

function LatencyTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl p-3 text-sm"
      style={{ background: 'rgba(10,14,26,0.95)', border: '1px solid rgba(245,158,11,0.3)' }}>
      <p className="font-semibold text-white mb-2">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: p.color }} />
          <span style={{ color: '#94a3b8' }}>{p.name}:</span>
          <span className="font-medium text-white">{p.value} ms</span>
        </div>
      ))}
    </div>
  )
}

/**
 * LatencyChart — multi-line chart showing p50 / p95 / p99 latency trends over time.
 * Data: mockData.latencyTrendData (Phase 1 synthetic values).
 */
export default function LatencyChart() {
  return (
    <div className="glass-card p-5 animate-slide-up" style={{ animationDelay: '280ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'rgba(245,158,11,0.15)' }}>
            <Clock size={16} style={{ color: '#f59e0b' }} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Latency Trend</h3>
            <p className="text-xs" style={{ color: '#64748b' }}>p50 / p95 / p99 (ms)</p>
          </div>
        </div>
        <span className="text-xs px-2 py-1 rounded-full"
          style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.25)' }}>
          Mock Data
        </span>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={latencyTrendData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
          <XAxis
            dataKey="day"
            tick={{ fill: '#64748b', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(99,102,241,0.15)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}ms`}
          />
          <Tooltip content={<LatencyTooltip />} />
          <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8', paddingTop: '8px' }} />
          <Line type="monotone" dataKey="p50" name="p50" stroke="#22d3ee"
            strokeWidth={2} dot={{ fill: '#22d3ee', r: 3 }} activeDot={{ r: 5 }} />
          <Line type="monotone" dataKey="p95" name="p95" stroke="#f59e0b"
            strokeWidth={2} dot={{ fill: '#f59e0b', r: 3 }} activeDot={{ r: 5 }} />
          <Line type="monotone" dataKey="p99" name="p99" stroke="#ef4444"
            strokeWidth={2} dot={{ fill: '#ef4444', r: 3 }} activeDot={{ r: 5 }} strokeDasharray="5 3" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
