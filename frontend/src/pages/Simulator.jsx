import { useState, useEffect } from 'react'
import {
  Play,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Sparkles,
  AlertTriangle,
  Clock,
  DollarSign,
  ShieldCheck,
  Cpu,
  Sliders,
  BarChart2
} from 'lucide-react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'
import { runSimulation } from '../services/api'
import RecommendationCard from '../components/dashboard/RecommendationCard'

// Preset scenarios for instant student testing
const PRESETS = [
  {
    name: 'Normal Traffic',
    scenario_name: 'Normal Traffic',
    cpu_utilization: 65,
    memory_mb: 1024,
    baseline_latency_ms: 150,
    request_volume: 2000000,
    current_price: 0.00001667,
    latency_target_ms: 200,
    availability_target: 99.9
  },
  {
    name: 'High Load Peak',
    scenario_name: 'High Load Peak',
    cpu_utilization: 90,
    memory_mb: 1024,
    baseline_latency_ms: 220,
    request_volume: 8000000,
    current_price: 0.00001667,
    latency_target_ms: 180,
    availability_target: 99.9
  },
  {
    name: 'Low Traffic Night',
    scenario_name: 'Low Traffic Night',
    cpu_utilization: 20,
    memory_mb: 1024,
    baseline_latency_ms: 110,
    request_volume: 100000,
    current_price: 0.00001667,
    latency_target_ms: 250,
    availability_target: 99.5
  },
  {
    name: 'Strict Latency SLO',
    scenario_name: 'Strict Latency SLO',
    cpu_utilization: 50,
    memory_mb: 1024,
    baseline_latency_ms: 160,
    request_volume: 3000000,
    current_price: 0.00001667,
    latency_target_ms: 95,
    availability_target: 99.95
  }
]

export default function Simulator() {
  const [formData, setFormData] = useState(PRESETS[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [simulationResult, setSimulationResult] = useState(null)

  useEffect(() => {
    handleRunSimulation(PRESETS[0])
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'scenario_name' ? value : parseFloat(value) || 0
    }))
  }

  const handleApplyPreset = (preset) => {
    setFormData(preset)
    handleRunSimulation(preset)
  }

  const handleRunSimulation = async (payloadToRun = formData) => {
    setLoading(true)
    setError(null)
    try {
      const data = await runSimulation(payloadToRun)
      setSimulationResult(data)
    } catch (err) {
      console.error('Simulation request failed:', err)
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((d) => `${d.loc.join('.')}: ${d.msg}`).join(', '))
      } else {
        setError('Failed to run simulation. Please check your inputs and ensure backend API is running.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sliders size={22} className="text-indigo-400" />
            Rightsizing Simulator
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Simulate serverless memory tiers (512MB – 3072MB) to optimize cost while adhering to SLO targets.
          </p>
        </div>

        {/* Preset quick buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500 font-medium mr-1">Presets:</span>
          {PRESETS.map((p) => (
            <button
              key={p.name}
              onClick={() => handleApplyPreset(p)}
              className="text-xs px-3 py-1.5 rounded-lg transition-all border font-medium bg-slate-900 border-indigo-500/20 text-slate-300 hover:border-indigo-400 hover:text-white hover:bg-indigo-950/40"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Form Left, Results Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* --- LEFT FORM PANEL (5 cols) --- */}
        <div className="lg:col-span-5 glass-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Cpu size={18} className="text-cyan-400" />
              Workload &amp; Target Parameters
            </h3>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs flex items-start gap-2">
                <AlertTriangle size={16} className="text-red-400 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-200">Simulation Error</p>
                  <p className="mt-0.5">{error}</p>
                </div>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleRunSimulation()
              }}
              className="space-y-3"
            >
              <div>
                <label className="text-xs text-slate-400 font-medium mb-1 block">Scenario Name</label>
                <input
                  type="text"
                  name="scenario_name"
                  value={formData.scenario_name}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 font-medium mb-1 block">CPU Utilization (%)</label>
                  <input
                    type="number"
                    name="cpu_utilization"
                    min="0"
                    max="100"
                    step="0.1"
                    value={formData.cpu_utilization}
                    onChange={handleInputChange}
                    required
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="text-xs text-slate-400 font-medium mb-1 block">Baseline Memory (MB)</label>
                  <select
                    name="memory_mb"
                    value={formData.memory_mb}
                    onChange={handleInputChange}
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="512">512 MB</option>
                    <option value="1024">1024 MB</option>
                    <option value="1536">1536 MB</option>
                    <option value="2048">2048 MB</option>
                    <option value="3072">3072 MB</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 font-medium mb-1 block">Baseline Latency (ms)</label>
                  <input
                    type="number"
                    name="baseline_latency_ms"
                    min="1"
                    step="1"
                    value={formData.baseline_latency_ms}
                    onChange={handleInputChange}
                    required
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="text-xs text-slate-400 font-medium mb-1 block">Request Volume / mo</label>
                  <input
                    type="number"
                    name="request_volume"
                    min="0"
                    step="10000"
                    value={formData.request_volume}
                    onChange={handleInputChange}
                    required
                    className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium mb-1 block">Price ($/GB-sec)</label>
                <input
                  type="number"
                  name="current_price"
                  min="0"
                  step="0.00000001"
                  value={formData.current_price}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              {/* SLO Targets */}
              <div className="pt-3 border-t border-slate-800">
                <p className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">SLO Target Constraints</p>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-400 font-medium mb-1 block">Max Latency Target (ms)</label>
                    <input
                      type="number"
                      name="latency_target_ms"
                      min="1"
                      step="1"
                      value={formData.latency_target_ms}
                      onChange={handleInputChange}
                      required
                      className="w-full bg-slate-900 border border-indigo-500/40 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-400"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 font-medium mb-1 block">Min Availability (%)</label>
                    <input
                      type="number"
                      name="availability_target"
                      min="90"
                      max="100"
                      step="0.01"
                      value={formData.availability_target}
                      onChange={handleInputChange}
                      required
                      className="w-full bg-slate-900 border border-indigo-500/40 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-400"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 btn-glow text-white font-semibold py-2.5 px-4 rounded-xl text-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Simulating...
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      Run Rightsizing Simulation
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => handleApplyPreset(PRESETS[0])}
                  className="p-2.5 rounded-xl border border-slate-700 bg-slate-900 text-slate-400 hover:text-white hover:border-slate-500 transition-colors"
                  title="Reset to default preset"
                >
                  <RotateCcw size={16} />
                </button>
              </div>
            </form>
          </div>

          <p className="text-[11px] text-slate-500 mt-4 border-t border-slate-800/80 pt-3">
            ⚠ Simulation Estimate: Mathematical approximation model for student learning. Not official AWS billing.
          </p>
        </div>

        {/* --- RIGHT RESULTS PANEL (7 cols) --- */}
        <div className="lg:col-span-7 space-y-6">

          {/* Top Recommendation Summary Card */}
          <RecommendationCard simulationResult={simulationResult} />

          {/* Baseline vs Best Comparison Summary Cards */}
          {simulationResult && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="glass-card p-4 border-cyan-500/30">
                <p className="text-xs text-cyan-400 uppercase font-semibold tracking-wider flex items-center justify-between">
                  <span>Baseline Setup</span>
                  <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded font-bold">CURRENT</span>
                </p>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-xl font-bold text-white">{simulationResult.baseline.memory_mb} MB</span>
                  <span className="text-sm font-semibold text-slate-300">${simulationResult.baseline.estimated_monthly_cost.toLocaleString()}/mo</span>
                </div>
                <div className="mt-3 text-xs text-slate-400 flex justify-between">
                  <span>Latency: <strong className="text-slate-200">{simulationResult.baseline.latency_ms} ms</strong></span>
                  <span>Availability: <strong className="text-slate-200">{simulationResult.baseline.availability}%</strong></span>
                </div>
              </div>

              <div className="glass-card p-4 border-indigo-500/40 bg-indigo-950/20">
                <p className="text-xs text-indigo-400 uppercase font-semibold tracking-wider flex items-center gap-1">
                  <Sparkles size={13} /> Recommended Rightsizing
                </p>
                {simulationResult.recommendation ? (
                  <>
                    <div className="mt-2 flex items-baseline justify-between">
                      <span className="text-xl font-bold text-white">{simulationResult.recommendation.memory_mb} MB</span>
                      <span className="text-sm font-semibold text-emerald-400">${simulationResult.recommendation.estimated_monthly_cost.toLocaleString()}/mo</span>
                    </div>
                    <div className="mt-3 text-xs text-slate-400 flex justify-between">
                      <span>Latency: <strong className="text-slate-200">{simulationResult.recommendation.estimated_latency_ms} ms</strong></span>
                      <span>
                        Savings:{' '}
                        {simulationResult.recommendation.memory_mb === simulationResult.baseline.memory_mb ? (
                          <strong className="text-emerald-400">Near-Optimal (0%)</strong>
                        ) : (
                          <strong className="text-emerald-400">{simulationResult.recommendation.cost_savings_percentage}%</strong>
                        )}
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="text-xs text-red-400 mt-3 font-medium">No Feasible Recommendation</p>
                )}
              </div>
            </div>
          )}

        </div>
      </div>

      {/* --- BOTTOM SECTION: COMPARISON TABLE & CHARTS --- */}
      {simulationResult && (
        <div className="space-y-6">

          {/* Comparison Table */}
          <div className="glass-card p-6">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <BarChart2 size={18} className="text-indigo-400" />
              Candidate Configuration Evaluation Table
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-xs uppercase text-slate-400 tracking-wider">
                    <th className="py-3 px-4">Configuration</th>
                    <th className="py-3 px-4">Est. Monthly Cost</th>
                    <th className="py-3 px-4">Cost Savings</th>
                    <th className="py-3 px-4">Est. Latency</th>
                    <th className="py-3 px-4">Est. Availability</th>
                    <th className="py-3 px-4 text-center">Latency Target</th>
                    <th className="py-3 px-4 text-center">Availability Target</th>
                    <th className="py-3 px-4 text-center">Feasible</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {simulationResult.configurations.map((c) => {
                    const isBaseline = simulationResult.baseline.memory_mb === c.memory_mb
                    const isRecommended = simulationResult.recommendation?.memory_mb === c.memory_mb
                    return (
                      <tr
                        key={c.memory_mb}
                        className={`transition-colors ${
                          isRecommended
                            ? 'bg-indigo-950/40 font-medium text-white border-l-4 border-l-indigo-500'
                            : isBaseline
                            ? 'bg-slate-900/60 text-slate-200 border-l-4 border-l-cyan-500'
                            : 'hover:bg-slate-900/40 text-slate-300'
                        }`}
                      >
                        <td className="py-3 px-4 flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-white">{c.memory_mb} MB</span>
                          {isBaseline && (
                            <span className="text-[10px] bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded font-bold">
                              BASELINE
                            </span>
                          )}
                          {isRecommended && (
                            <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded font-bold">
                              RECOMMENDED
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 font-mono">${c.estimated_monthly_cost.toLocaleString()}</td>
                        <td className={`py-3 px-4 font-semibold ${isBaseline ? 'text-slate-400' : c.cost_savings_percentage >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          {isBaseline ? '0%' : `${c.cost_savings_percentage >= 0 ? '+' : ''}${c.cost_savings_percentage}%`}
                        </td>
                        <td className="py-3 px-4">{c.estimated_latency_ms} ms</td>
                        <td className="py-3 px-4">{c.estimated_availability}%</td>
                        <td className="py-3 px-4 text-center">
                          {c.latency_target_met ? (
                            <CheckCircle2 size={16} className="text-emerald-400 mx-auto" />
                          ) : (
                            <XCircle size={16} className="text-red-400 mx-auto" />
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {c.availability_target_met ? (
                            <CheckCircle2 size={16} className="text-emerald-400 mx-auto" />
                          ) : (
                            <XCircle size={16} className="text-red-400 mx-auto" />
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {c.feasible ? (
                            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold">
                              YES
                            </span>
                          ) : (
                            <span className="text-xs px-2 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/30 font-semibold">
                              NO
                            </span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Visual Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Chart 1: Cost vs Memory */}
            <div className="glass-card p-5">
              <h4 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <DollarSign size={16} className="text-emerald-400" />
                Cost vs. Memory Configuration
              </h4>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={simulationResult.configurations}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                  <XAxis dataKey="memory_mb" tickFormatter={(v) => `${v}MB`} stroke="#64748b" />
                  <YAxis stroke="#64748b" tickFormatter={(v) => `$${v}`} />
                  <Tooltip content={<CustomTooltip unit="$" />} />
                  <Bar dataKey="estimated_monthly_cost" name="Est. Monthly Cost" radius={[4, 4, 0, 0]}>
                    {simulationResult.configurations.map((entry) => (
                      <Cell
                        key={`cell-${entry.memory_mb}`}
                        fill={entry.memory_mb === simulationResult.recommendation?.memory_mb ? '#10b981' : entry.feasible ? '#6366f1' : '#ef4444'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Chart 2: Latency vs Memory */}
            <div className="glass-card p-5">
              <h4 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Clock size={16} className="text-cyan-400" />
                Latency vs. Memory Configuration
              </h4>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={simulationResult.configurations}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                  <XAxis dataKey="memory_mb" tickFormatter={(v) => `${v}MB`} stroke="#64748b" />
                  <YAxis stroke="#64748b" tickFormatter={(v) => `${v}ms`} />
                  <Tooltip content={<CustomTooltip unit="ms" />} />
                  <Line
                    type="monotone"
                    dataKey="estimated_latency_ms"
                    name="Est. Latency"
                    stroke="#22d3ee"
                    strokeWidth={2}
                    dot={{ r: 4, fill: '#22d3ee' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

          </div>

        </div>
      )}
    </div>
  )
}

function CustomTooltip({ active, payload, label, unit }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-xs shadow-xl text-white">
      <p className="font-bold border-b border-slate-800 pb-1 mb-1">{label} MB Tier</p>
      <p style={{ color: payload[0].color || '#22d3ee' }}>
        {payload[0].name}: {unit === '$' ? `$${payload[0].value.toLocaleString()}` : `${payload[0].value} ${unit}`}
      </p>
    </div>
  )
}
