import { useState, useEffect } from 'react'
import {
  FlaskConical,
  Plus,
  Play,
  Edit2,
  Trash2,
  Eye,
  X,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  DollarSign,
  Cpu,
  BarChart2,
  ArrowLeft,
  Calendar,
  Layers
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
import {
  fetchScenarios,
  createScenario,
  updateScenario,
  deleteScenario,
  simulateScenario
} from '../services/api'
import RecommendationCard from '../components/dashboard/RecommendationCard'

const WORKLOAD_TYPES = ['Low Traffic', 'Normal Traffic', 'High Traffic', 'Custom']

const EMPTY_FORM = {
  name: '',
  description: '',
  workload_type: 'Normal Traffic',
  request_volume: 2000000,
  baseline_memory_mb: 1024,
  baseline_latency_ms: 150,
  cpu_utilization: 65,
  current_price: 0.00001667,
  latency_target_ms: 200,
  availability_target_percent: 99.9
}

export default function Scenarios() {
  const [scenarios, setScenarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Selected scenario view mode (null = list view, object = detailed view)
  const [selectedScenario, setSelectedScenario] = useState(null)

  // Simulation execution state when running inside a scenario view
  const [simLoading, setSimLoading] = useState(false)
  const [simulationResult, setSimulationResult] = useState(null)

  // Modal Form State
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState(EMPTY_FORM)

  useEffect(() => {
    loadScenarios()
  }, [])

  const loadScenarios = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchScenarios()
      setScenarios(data)
    } catch (err) {
      console.error('Failed to load scenarios:', err)
      setError('Failed to load scenarios. Ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingId(null)
    setFormData(EMPTY_FORM)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (scenario) => {
    setEditingId(scenario.id)
    setFormData({
      name: scenario.name,
      description: scenario.description || '',
      workload_type: scenario.workload_type,
      request_volume: scenario.request_volume,
      baseline_memory_mb: scenario.baseline_memory_mb,
      baseline_latency_ms: scenario.baseline_latency_ms,
      cpu_utilization: scenario.cpu_utilization,
      current_price: scenario.current_price,
      latency_target_ms: scenario.latency_target_ms,
      availability_target_percent: scenario.availability_target_percent
    })
    setIsModalOpen(true)
  }

  const handleDeleteScenario = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm('Are you sure you want to delete this scenario?')) return
    try {
      await deleteScenario(id)
      if (selectedScenario?.id === id) {
        setSelectedScenario(null)
        setSimulationResult(null)
      }
      loadScenarios()
    } catch (err) {
      alert('Failed to delete scenario: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingId) {
        await updateScenario(editingId, formData)
      } else {
        await createScenario(formData)
      }
      setIsModalOpen(false)
      loadScenarios()
    } catch (err) {
      alert('Failed to save scenario: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleOpenScenarioView = (scenario) => {
    setSelectedScenario(scenario)
    setSimulationResult(null)
  }

  const handleRunScenarioSimulation = async () => {
    if (!selectedScenario) return
    setSimLoading(true)
    try {
      const result = await simulateScenario(selectedScenario.id)
      setSimulationResult(result)
    } catch (err) {
      alert('Simulation failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setSimLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-screen-2xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FlaskConical size={22} className="text-indigo-400" />
            Workload Scenarios
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Create, manage, and simulate serverless workload profiles.
          </p>
        </div>

        {selectedScenario ? (
          <button
            onClick={() => {
              setSelectedScenario(null)
              setSimulationResult(null)
            }}
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
          >
            <ArrowLeft size={14} /> Back to Scenarios
          </button>
        ) : (
          <button
            onClick={handleOpenCreateModal}
            className="btn-glow text-white text-xs font-semibold px-4 py-2.5 rounded-xl flex items-center gap-2"
          >
            <Plus size={16} /> Create New Scenario
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-sm flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* --- SCENARIO DETAILED VIEW MODE --- */}
      {selectedScenario ? (
        <div className="space-y-6 animate-fade-in">
          {/* Scenario Info Bar */}
          <div className="glass-card p-6 border-indigo-500/30">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <span className="text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    {selectedScenario.workload_type}
                  </span>
                  <h3 className="text-lg font-bold text-white">{selectedScenario.name}</h3>
                </div>
                <p className="text-xs text-slate-400 mt-1">{selectedScenario.description || 'No description provided.'}</p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleOpenEditModal(selectedScenario)}
                  className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-medium text-slate-300 hover:text-white hover:border-slate-500 flex items-center gap-1.5"
                >
                  <Edit2 size={14} /> Edit
                </button>
                <button
                  onClick={handleRunScenarioSimulation}
                  disabled={simLoading}
                  className="btn-glow px-5 py-2.5 rounded-xl text-xs font-bold text-white flex items-center gap-2 disabled:opacity-50"
                >
                  {simLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Simulating...
                    </>
                  ) : (
                    <>
                      <Play size={16} /> Run Simulation
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Scenario Parameter Chips */}
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mt-6 pt-4 border-t border-slate-800 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <p className="text-slate-400 text-[10px] uppercase font-semibold">Request Volume</p>
                <p className="font-bold text-white mt-0.5">{selectedScenario.request_volume.toLocaleString()}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <p className="text-slate-400 text-[10px] uppercase font-semibold">Baseline Memory</p>
                <p className="font-bold text-white mt-0.5">{selectedScenario.baseline_memory_mb} MB</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <p className="text-slate-400 text-[10px] uppercase font-semibold">Baseline Latency</p>
                <p className="font-bold text-white mt-0.5">{selectedScenario.baseline_latency_ms} ms</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <p className="text-slate-400 text-[10px] uppercase font-semibold">CPU Load</p>
                <p className="font-bold text-white mt-0.5">{selectedScenario.cpu_utilization}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <p className="text-slate-400 text-[10px] uppercase font-semibold">Unit Price</p>
                <p className="font-bold text-white mt-0.5 font-mono">${selectedScenario.current_price}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-indigo-500/20">
                <p className="text-indigo-400 text-[10px] uppercase font-semibold">Max Latency SLO</p>
                <p className="font-bold text-white mt-0.5">{selectedScenario.latency_target_ms} ms</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-indigo-500/20">
                <p className="text-indigo-400 text-[10px] uppercase font-semibold">Min Availability SLO</p>
                <p className="font-bold text-white mt-0.5">{selectedScenario.availability_target_percent}%</p>
              </div>
            </div>
          </div>

          {/* Simulation Output Area */}
          {simulationResult ? (
            <div className="space-y-6 animate-fade-in">
              <RecommendationCard simulationResult={simulationResult} />

              {/* Evaluation Table */}
              <div className="glass-card p-6">
                <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart2 size={16} className="text-indigo-400" /> Candidate Tier Evaluation Table
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 uppercase text-slate-400 tracking-wider">
                        <th className="py-2.5 px-3">Memory Tier</th>
                        <th className="py-2.5 px-3">Est. Monthly Cost</th>
                        <th className="py-2.5 px-3">Cost Savings</th>
                        <th className="py-2.5 px-3">Est. Latency</th>
                        <th className="py-2.5 px-3">Est. Availability</th>
                        <th className="py-2.5 px-3 text-center">Latency SLO</th>
                        <th className="py-2.5 px-3 text-center">Avail SLO</th>
                        <th className="py-2.5 px-3 text-center">Feasible</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {simulationResult.configurations.map((c) => {
                        const isBaseline = simulationResult.baseline.memory_mb === c.memory_mb
                        const isRec = simulationResult.recommendation?.memory_mb === c.memory_mb
                        return (
                          <tr
                            key={c.memory_mb}
                            className={`${
                              isRec
                                ? 'bg-indigo-950/40 font-semibold text-white border-l-4 border-l-indigo-500'
                                : isBaseline
                                ? 'bg-slate-900/60 text-slate-200 border-l-4 border-l-cyan-500'
                                : 'text-slate-300'
                            }`}
                          >
                            <td className="py-2.5 px-3 font-semibold text-white flex items-center gap-2">
                              {c.memory_mb} MB
                              {isBaseline && <span className="text-[9px] bg-cyan-500/20 text-cyan-300 px-1.5 py-0.5 rounded font-bold">BASELINE</span>}
                              {isRec && <span className="text-[9px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-bold">RECOMMENDED</span>}
                            </td>
                            <td className="py-2.5 px-3 font-mono">${c.estimated_monthly_cost.toLocaleString()}</td>
                            <td className={`py-2.5 px-3 font-semibold ${isBaseline ? 'text-slate-400' : c.cost_savings_percentage >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {isBaseline ? '0%' : `${c.cost_savings_percentage >= 0 ? '+' : ''}${c.cost_savings_percentage}%`}
                            </td>
                            <td className="py-2.5 px-3">{c.estimated_latency_ms} ms</td>
                            <td className="py-2.5 px-3">{c.estimated_availability}%</td>
                            <td className="py-2.5 px-3 text-center">
                              {c.latency_target_met ? <CheckCircle2 size={15} className="text-emerald-400 mx-auto" /> : <XCircle size={15} className="text-red-400 mx-auto" />}
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              {c.availability_target_met ? <CheckCircle2 size={15} className="text-emerald-400 mx-auto" /> : <XCircle size={15} className="text-red-400 mx-auto" />}
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              {c.feasible ? (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold">YES</span>
                              ) : (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/30 font-semibold">NO</span>
                              )}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Recharts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-5">
                  <h4 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
                    <DollarSign size={14} className="text-emerald-400" /> Cost vs. Memory
                  </h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={simulationResult.configurations}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                      <XAxis dataKey="memory_mb" tickFormatter={(v) => `${v}MB`} stroke="#64748b" />
                      <YAxis stroke="#64748b" tickFormatter={(v) => `$${v}`} />
                      <Tooltip />
                      <Bar dataKey="estimated_monthly_cost" radius={[4, 4, 0, 0]}>
                        {simulationResult.configurations.map((entry) => (
                          <Cell
                            key={entry.memory_mb}
                            fill={entry.memory_mb === simulationResult.recommendation?.memory_mb ? '#10b981' : entry.feasible ? '#6366f1' : '#ef4444'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="glass-card p-5">
                  <h4 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
                    <Clock size={14} className="text-cyan-400" /> Latency vs. Memory
                  </h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={simulationResult.configurations}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,102,241,0.1)" />
                      <XAxis dataKey="memory_mb" tickFormatter={(v) => `${v}MB`} stroke="#64748b" />
                      <YAxis stroke="#64748b" tickFormatter={(v) => `${v}ms`} />
                      <Tooltip />
                      <Line type="monotone" dataKey="estimated_latency_ms" stroke="#22d3ee" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <FlaskConical size={32} className="text-indigo-400 mx-auto mb-3 opacity-60" />
              <p className="text-sm font-semibold text-white">No Simulation Run Yet</p>
              <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                Click the <strong className="text-white">Run Simulation</strong> button above to evaluate candidate memory tiers against this scenario’s parameters and SLO targets.
              </p>
            </div>
          )}
        </div>
      ) : (
        /* --- SCENARIOS LIST VIEW MODE --- */
        <div className="space-y-4">
          {loading ? (
            <div className="glass-card p-12 text-center text-slate-400 text-sm">Loading scenarios...</div>
          ) : scenarios.length === 0 ? (
            <div className="glass-card p-12 text-center text-slate-400 text-sm">No scenarios found. Click "Create New Scenario" to get started.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scenarios.map((s) => (
                <div
                  key={s.id}
                  onClick={() => handleOpenScenarioView(s)}
                  className="glass-card p-5 cursor-pointer hover:border-indigo-500/50 transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        {s.workload_type}
                      </span>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleOpenEditModal(s)
                          }}
                          className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800"
                          title="Edit scenario"
                        >
                          <Edit2 size={13} />
                        </button>
                        <button
                          onClick={(e) => handleDeleteScenario(s.id, e)}
                          className="p-1 rounded text-slate-400 hover:text-red-400 hover:bg-slate-800"
                          title="Delete scenario"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </div>

                    <h3 className="text-base font-bold text-white mb-1 group-hover:text-indigo-300 transition-colors">
                      {s.name}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-2 mb-4">
                      {s.description || 'No description provided.'}
                    </p>

                    <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                      <div className="p-2 rounded bg-slate-900/60">
                        <span className="text-[10px] text-slate-500 block">Baseline Mem</span>
                        <span className="font-semibold text-white">{s.baseline_memory_mb} MB</span>
                      </div>
                      <div className="p-2 rounded bg-slate-900/60">
                        <span className="text-[10px] text-slate-500 block">Requests</span>
                        <span className="font-semibold text-white">{s.request_volume.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1 text-[10px]">
                      <Calendar size={11} /> {new Date(s.created_at).toLocaleDateString()}
                    </span>
                    <span className="text-indigo-400 font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                      Open <Eye size={12} />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* --- CREATE / EDIT MODAL FORM --- */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="glass-card w-full max-w-lg p-6 relative border-indigo-500/40">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X size={18} />
            </button>

            <h3 className="text-base font-bold text-white mb-4">
              {editingId ? 'Edit Workload Scenario' : 'Create New Workload Scenario'}
            </h3>

            <form onSubmit={handleFormSubmit} className="space-y-3">
              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Scenario Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Workload Type</label>
                  <select
                    value={formData.workload_type}
                    onChange={(e) => setFormData({ ...formData, workload_type: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    {WORKLOAD_TYPES.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Request Volume / mo</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={formData.request_volume}
                    onChange={(e) => setFormData({ ...formData, request_volume: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Baseline Mem (MB)</label>
                  <select
                    value={formData.baseline_memory_mb}
                    onChange={(e) => setFormData({ ...formData, baseline_memory_mb: parseFloat(e.target.value) })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="512">512 MB</option>
                    <option value="1024">1024 MB</option>
                    <option value="1536">1536 MB</option>
                    <option value="2048">2048 MB</option>
                    <option value="3072">3072 MB</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Baseline Latency (ms)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.baseline_latency_ms}
                    onChange={(e) => setFormData({ ...formData, baseline_latency_ms: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">CPU Load (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    required
                    value={formData.cpu_utilization}
                    onChange={(e) => setFormData({ ...formData, cpu_utilization: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Price Rate ($/GB-sec)</label>
                <input
                  type="number"
                  step="0.00000001"
                  required
                  value={formData.current_price}
                  onChange={(e) => setFormData({ ...formData, current_price: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="pt-2 border-t border-slate-800 grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-indigo-400 font-medium block mb-1">Max Latency SLO (ms)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.latency_target_ms}
                    onChange={(e) => setFormData({ ...formData, latency_target_ms: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-indigo-500/40 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-400"
                  />
                </div>

                <div>
                  <label className="text-xs text-indigo-400 font-medium block mb-1">Min Avail SLO (%)</label>
                  <input
                    type="number"
                    min="90"
                    max="100"
                    step="0.01"
                    required
                    value={formData.availability_target_percent}
                    onChange={(e) => setFormData({ ...formData, availability_target_percent: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-indigo-500/40 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-400"
                  />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-900 text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-glow text-white text-xs font-bold px-5 py-2 rounded-xl"
                >
                  {editingId ? 'Save Changes' : 'Create Scenario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
