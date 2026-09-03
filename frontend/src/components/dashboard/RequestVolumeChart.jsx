import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Activity } from 'lucide-react'
import { requestVolumeData } from '../../data/mockData'

function VolumeTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl p-3 text-sm"
      style={{ background: 'rgba(10,14,26,0.95)', border: '1px solid rgba(236,72,153,0.3)' }}>
      <p className="font-semibold text-white mb-1">{label}</p>
      <div className="flex items-center gap-2">
        <span className="w-2.5 h-2.5 rounded-full" style={{ background: '#ec4899' }} />
        <span style={{ color: '#94a3b8' }}>Requests:</span>
        <span className="font-medium text-white">{payload[0]?.value?.toLocaleString()}</span>
      </div>
    </div>
  )
}

/**
 * RequestVolumeChart — area chart showing request volume throughout the day.
 * Data: mockData.requestVolumeData (Phase 1 synthetic values).
 */
export default function RequestVolumeChart() {
  return (
    <div className="glass-card p-5 animate-slide-up" style={{ animationDelay: '360ms' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'rgba(236,72,153,0.15)' }}>
            <Activity size={16} style={{ color: '#ec4899' }} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Request Volume</h3>
            <p className="text-xs" style={{ color: '#64748b' }}>Hourly distribution (today)</p>
          </div>
        </div>
        <span className="text-xs px-2 py-1 rounded-full"
          style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.25)' }}>
          Mock Data
        </span>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={requestVolumeData}>
          <defs>
            <linearGradient id="requestGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#ec4899" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ec4899" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.08)" />
          <XAxis
            dataKey="time"
            tick={{ fill: '#64748b', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(99,102,241,0.15)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
          />
          <Tooltip content={<VolumeTooltip />} />
          <Area
            type="monotone"
            dataKey="requests"
            stroke="#ec4899"
            strokeWidth={2}
            fill="url(#requestGradient)"
            dot={false}
            activeDot={{ r: 5, fill: '#ec4899' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
