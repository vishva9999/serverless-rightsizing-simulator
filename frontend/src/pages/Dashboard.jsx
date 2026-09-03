import { useState, useEffect } from 'react'
import SummaryCards from '../components/dashboard/SummaryCards'
import CostChart from '../components/dashboard/CostChart'
import LatencyChart from '../components/dashboard/LatencyChart'
import RequestVolumeChart from '../components/dashboard/RequestVolumeChart'
import RecommendationCard from '../components/dashboard/RecommendationCard'
import { recentActivity } from '../data/mockData'
import { fetchMetricsSummary, fetchHealth, runSimulation, fetchScenarios, fetchHistory } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { CheckCircle, AlertTriangle, Database, RefreshCw, Layers, History, Sliders, ArrowRight, Building2, Shield, User } from 'lucide-react'

/**
 * Dashboard page — Phase 6 with user/organization welcome, live scenarios, and simulations.
 */
export default function Dashboard({ onNavigate }) {
  const { user } = useAuth()
  const [apiStatus, setApiStatus] = useState({ loaded: false, ok: false, data: null })
  const [dashboardSimResult, setDashboardSimResult] = useState(null)

  // Phase 3 Metrics State
  const [stats, setStats] = useState({ scenariosCount: 0, historyCount: 0, latestHistory: [] })

  useEffect(() => {
    const loadApiData = async () => {
      try {
        const [health, metrics, scenarios, historyList, sim] = await Promise.all([
          fetchHealth(),
          fetchMetricsSummary(),
          fetchScenarios().catch(() => []),
          fetchHistory().catch(() => []),
          runSimulation({
            scenario_name: 'Dashboard Overview',
            cpu_utilization: 65,
            memory_mb: 1024,
            baseline_latency_ms: 150,
            request_volume: 2000000,
            current_price: 0.00001667,
            latency_target_ms: 200,
            availability_target: 99.9
          }).catch(() => null)
        ])

        setApiStatus({ loaded: true, ok: health.status === 'ok', data: metrics })
        setDashboardSimResult(sim)
        setStats({
          scenariosCount: scenarios.length,
          historyCount: historyList.length,
          latestHistory: historyList.slice(0, 4)
        })
      } catch {
        setApiStatus({ loaded: true, ok: false, data: null })
      }
    }
    loadApiData()
  }, [])

  return (
    <div className="p-6 space-y-6 max-w-screen-2xl mx-auto">

      {/* ── Welcome Banner (Phase 6) ─────────────────────────── */}
      {user && (
        <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-3xl p-5 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
          <div className="flex items-center space-x-3.5">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/25">
              {user.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Welcome back, {user.full_name}
              </h2>
              <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-slate-400">
                <span className="flex items-center space-x-1">
                  <Building2 className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Workspace: <strong className="text-slate-200">Organization ({user.organization_id})</strong></span>
                </span>
                <span>•</span>
                <span className="flex items-center space-x-1">
                  <Shield className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Role: <strong className="text-cyan-300 uppercase font-semibold">{user.role}</strong></span>
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2 text-xs text-slate-300">
              <Layers size={14} className="text-indigo-400" />
              <span>Scenarios: <strong className="text-white">{stats.scenariosCount}</strong></span>
            </div>
            <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2 text-xs text-slate-300">
              <History size={14} className="text-cyan-400" />
              <span>Simulations: <strong className="text-white">{stats.historyCount}</strong></span>
            </div>
          </div>
        </div>
      )}

      {/* ── Backend API Status Banner ─────────────────────────── */}
      <ApiStatusBanner status={apiStatus} />

      {/* ── Sensitivity Analysis Promo Card ─────────────────── */}
      <div className="glass-card p-4 border-indigo-500/30 bg-indigo-950/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <Sliders size={20} className="text-indigo-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Sensitivity Analysis Available</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Explore how recommended configurations change when request volume, CPU, latency, or SLO targets vary.
            </p>
          </div>
        </div>

        {onNavigate && (
          <button
            onClick={() => onNavigate('sensitivity')}
            className="btn-glow text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-2 shrink-0"
          >
            Open Sensitivity Analysis <ArrowRight size={14} />
          </button>
        )}
      </div>

      {/* ── Summary Cards ────────────────────────────────────── */}
      <SummaryCards />

      {/* ── Charts Row ───────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CostChart />
        <LatencyChart />
      </div>

      {/* ── Bottom Row: Request Volume + Recommendation + Activity ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1">
          <RequestVolumeChart />
        </div>
        <div className="lg:col-span-1">
          <RecommendationCard simulationResult={dashboardSimResult} />
        </div>
        <div className="lg:col-span-1">
          <RecentHistoryFeed historyItems={stats.latestHistory} />
        </div>
      </div>

      {/* ── Live Metrics from API (if connected) ─────────────── */}
      {apiStatus.ok && apiStatus.data && (
        <LiveMetricsPanel data={apiStatus.data} />
      )}
    </div>
  )
}

/* ── API Status Banner ───────────────────────────────────────────────────── */
function ApiStatusBanner({ status }) {
  if (!status.loaded) {
    return (
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm animate-fade-in"
        style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)' }}>
        <RefreshCw size={15} className="animate-spin" style={{ color: '#6366f1' }} />
        <span style={{ color: '#94a3b8' }}>Connecting to backend API…</span>
      </div>
    )
  }

  if (status.ok) {
    return (
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm animate-fade-in"
        style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)' }}>
        <CheckCircle size={15} style={{ color: '#34d399' }} />
        <span style={{ color: '#94a3b8' }}>
          Backend API connected — Authentication &amp; Multi-Tenant Isolation Active ({status.data?.dataset_info?.total_records?.toLocaleString()} CSV records)
        </span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm animate-fade-in"
      style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)' }}>
      <AlertTriangle size={15} style={{ color: '#fbbf24' }} />
      <span style={{ color: '#94a3b8' }}>
        Backend API offline — start the FastAPI server with{' '}
        <code className="font-mono text-xs px-1.5 py-0.5 rounded"
          style={{ background: 'rgba(0,0,0,0.3)', color: '#fbbf24' }}>
          uvicorn app.main:app --reload
        </code>
      </span>
    </div>
  )
}

/* ── Live Metrics Panel (real CSV stats from backend) ────────────────────── */
function LiveMetricsPanel({ data }) {
  const items = [
    { label: 'Avg CPU Utilization', value: `${data.average_cpu_utilization}%` },
    { label: 'Avg Memory',          value: `${data.average_memory_mb} MB` },
    { label: 'Avg Latency',         value: `${data.average_latency_ms} ms` },
    { label: 'Total Requests',      value: data.total_request_volume?.toLocaleString() },
    { label: 'Avg Availability',    value: `${data.average_availability}%` },
    { label: 'Est. Total Cost',     value: `$${data.total_estimated_cost?.toFixed(4)}` },
  ]

  return (
    <div className="glass-card p-5 animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <Database size={16} style={{ color: '#22d3ee' }} />
        <h3 className="text-sm font-semibold text-white">Live Stats from CSV Dataset</h3>
        <span className="ml-auto text-xs px-2 py-0.5 rounded-full"
          style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.25)' }}>
          Real API Data
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {items.map(({ label, value }) => (
          <div key={label} className="text-center p-3 rounded-xl"
            style={{ background: 'rgba(34,211,238,0.05)', border: '1px solid rgba(34,211,238,0.12)' }}>
            <p className="text-lg font-bold text-white">{value}</p>
            <p className="text-xs mt-1" style={{ color: '#64748b' }}>{label}</p>
          </div>
        ))}
      </div>
      <p className="text-xs mt-3" style={{ color: '#475569' }}>
        ⚠ {data.note}
      </p>
    </div>
  )
}

/* ── Recent History Feed (Live Simulation Log) ──────────────────────────── */
function RecentHistoryFeed({ historyItems }) {
  if (!historyItems || historyItems.length === 0) {
    return (
      <div className="glass-card p-5 animate-slide-up h-full">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <History size={16} className="text-indigo-400" /> Recent Simulation History
        </h3>
        <div className="space-y-3">
          {recentActivity.map((item) => (
            <div key={item.id} className="flex items-start gap-3">
              <span className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0 bg-emerald-400" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white leading-snug">{item.event}</p>
                <p className="text-xs mt-0.5 text-slate-500">{item.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card p-5 animate-slide-up h-full">
      <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
        <History size={16} className="text-indigo-400" /> Recent Simulation Runs
      </h3>
      <div className="space-y-3">
        {historyItems.map((h) => (
          <div key={h.id} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
            <div>
              <p className="font-semibold text-white">{h.scenario_name}</p>
              <p className="text-[10px] text-slate-500">{new Date(h.created_at).toLocaleTimeString()}</p>
            </div>
            <div className="text-right">
              <span className="font-bold text-indigo-300 block">{h.recommended_memory_mb ? `${h.recommended_memory_mb} MB` : 'N/A'}</span>
              <span className="text-[10px] text-emerald-400 font-semibold">{h.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
