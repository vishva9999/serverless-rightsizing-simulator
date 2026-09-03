import { DollarSign, TrendingDown, TrendingUp, Clock, Shield, Activity } from 'lucide-react'
import { summaryMetrics } from '../../data/mockData'

/**
 * Icon map — matches each metric key to a Lucide icon and a color.
 */
const CARD_CONFIG = {
  currentMonthlyCost:   { icon: DollarSign,   color: '#6366f1', glow: 'rgba(99,102,241,0.3)'  },
  optimizedMonthlyCost: { icon: TrendingDown,  color: '#22d3ee', glow: 'rgba(34,211,238,0.3)'  },
  estimatedSavings:     { icon: TrendingUp,    color: '#10b981', glow: 'rgba(16,185,129,0.3)'  },
  averageLatency:       { icon: Clock,         color: '#f59e0b', glow: 'rgba(245,158,11,0.3)'  },
  availability:         { icon: Shield,        color: '#8b5cf6', glow: 'rgba(139,92,246,0.3)'  },
  monthlyRequests:      { icon: Activity,      color: '#ec4899', glow: 'rgba(236,72,153,0.3)'  },
}

/**
 * SummaryCards — renders 6 metric cards across the top of the dashboard.
 * Data source: mockData.js (Phase 1 — synthetic values).
 */
export default function SummaryCards() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {Object.entries(summaryMetrics).map(([key, metric], idx) => (
        <MetricCard
          key={key}
          metric={metric}
          config={CARD_CONFIG[key]}
          delay={idx * 60}
        />
      ))}
    </div>
  )
}

function MetricCard({ metric, config, delay }) {
  const Icon = config.icon
  const isPositiveTrend = metric.trend === 'up'
  // For cost metrics, "up" is bad; for savings/availability/requests, "up" is good
  const changeColor = metric.trend === 'down' && metric.label.includes('Latency')
    ? '#10b981'    // lower latency = good (green)
    : metric.trend === 'down' && metric.label.includes('Optimized')
    ? '#10b981'    // lower cost = good (green)
    : isPositiveTrend && metric.label.includes('Current')
    ? '#ef4444'    // current cost rising = bad (red)
    : '#10b981'

  return (
    <div
      className="glass-card p-5 animate-slide-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Top row: icon + change badge */}
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center"
          style={{ background: `${config.color}20`, boxShadow: `0 0 12px ${config.glow}` }}
        >
          <Icon size={20} style={{ color: config.color }} />
        </div>
        <span
          className="text-xs font-semibold px-2 py-1 rounded-full"
          style={{ background: `${changeColor}15`, color: changeColor, border: `1px solid ${changeColor}30` }}
        >
          {metric.change}
        </span>
      </div>

      {/* Value */}
      <p className="text-2xl font-bold text-white mb-1">{metric.value}</p>

      {/* Label */}
      <p className="text-sm" style={{ color: '#64748b' }}>{metric.label}</p>

      {/* Subtle bottom accent line */}
      <div
        className="mt-4 h-0.5 rounded-full"
        style={{ background: `linear-gradient(90deg, ${config.color}60, transparent)` }}
      />
    </div>
  )
}
