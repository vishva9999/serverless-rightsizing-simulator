import { useState, useEffect } from 'react'
import {
  Sliders,
  Play,
  Info,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Database,
  DollarSign,
  Clock,
  Cpu,
  RefreshCw,
  Sparkles
} from 'lucide-react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts'
import {
  fetchScenarios,
  fetchSensitivityVariables,
  runSensitivityAnalysis
} from '../services/api'

export default function Sensitivity() {
  const [scenarios, setScenarios] = useState([])
  const [variables, setVariables] = useState([])
  const [loading, setLoading] = useState(true)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [error, setError] = useState(null)

  // Selection form state
  const [selectedScenarioId, setSelectedScenarioId] = useState('')
  const [selectedVariable, setSelectedVariable] = useState('request_volume')
  const [customValuesInput, setCustomValuesInput] = useState('')

  // Analysis result
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [scenData, varData] = await Promise.all([
        fetchScenarios().catch(() => []),
        fetchSensitivityVariables().catch(() => [])
      ])
      setScenarios(scenData)
      setVariables(varData)

      if (scenData.length > 0) {
        setSelectedScenarioId(scenData[0].id)
      }
    } catch (err) {
      console.error('Failed to load initial data:', err)
      setError('Failed to load scenarios or sensitivity variables.')
    } finally {
      setLoading(false)
    }
  }

  const getSelectedScenario = () => {
    return scenarios.find((s) => s.id === selectedScenarioId)
  }

  // Generate preset values based on selected scenario and variable
  const getPresets = () => {
    const scenario = getSelectedScenario()
    if (!scenario) return []

    switch (selectedVariable) {
      case 'request_volume': {
        const base = scenario.request_volume
        return [
          { label: '-50%', value: Math.max(0, Math.round(base * 0.5)) },
          { label: '-25%', value: Math.max(0, Math.round(base * 0.75)) },
          { label: 'Baseline', value: base },
          { label: '+25%', value: Math.round(base * 1.25) },
          { label: '+50%', value: Math.round(base * 1.5) },
          { label: '+100%', value: Math.round(base * 2.0) }
        ]
      }
      case 'cpu_utilization':
        return [
          { label: '25%', value: 25 },
          { label: '40%', value: 40 },
          { label: '50% (Baseline)', value: 50 },
          { label: '65%', value: 65 },
          { label: '80%', value: 80 }
        ]
      case 'baseline_latency_ms':
        return [
          { label: '80 ms', value: 80 },
          { label: '120 ms', value: 120 },
          { label: '150 ms (Baseline)', value: 150 },
          { label: '200 ms', value: 200 },
          { label: '250 ms', value: 250 }
        ]
      case 'latency_target_ms':
        return [
          { label: '100 ms', value: 100 },
          { label: '150 ms', value: 150 },
          { label: '200 ms (Target)', value: 200 },
          { label: '250 ms', value: 250 },
          { label: '300 ms', value: 300 }
        ]
      case 'availability_target_percent':
        return [
          { label: '95.0%', value: 95.0 },
          { label: '98.0%', value: 98.0 },
          { label: '99.0%', value: 99.0 },
          { label: '99.5%', value: 99.5 },
          { label: '99.9%', value: 99.9 }
        ]
      case 'current_price':
        return [
          { label: '$0.000010', value: 0.000010 },
          { label: '$0.00001667', value: 0.00001667 },
          { label: '$0.000025', value: 0.000025 },
          { label: '$0.000035', value: 0.000035 }
        ]
      default:
        return []
    }
  }

  const handleApplyPreset = () => {
    const presets = getPresets()
    const vals = presets.map((p) => p.value)
    setCustomValuesInput(vals.join(', '))
  }

  const handleRunAnalysis = async (customVals = null) => {
    if (!selectedScenarioId) {
      alert('Please select a workload scenario.')
      return
    }

    let valuesToUse = customVals
    if (!valuesToUse) {
      if (customValuesInput.trim()) {
        valuesToUse = customValuesInput
          .split(',')
          .map((v) => parseFloat(v.trim()))
          .filter((v) => !isNaN(v))
      } else {
        valuesToUse = getPresets().map((p) => p.value)
      }
    }

    if (!valuesToUse || valuesToUse.length === 0) {
      alert('Please enter valid numeric values for sensitivity analysis.')
      return
    }

    setAnalysisLoading(true)
    setError(null)

    try {
      const payload = {
        scenario_id: selectedScenarioId,
        variable: selectedVariable,
        values: valuesToUse
      }
      const data = await runSensitivityAnalysis(payload)
      setResult(data)
    } catch (err) {
      console.error('Sensitivity analysis failed:', err)
      setError('Analysis failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setAnalysisLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sliders size={22} className="text-indigo-400" />
            Parameter Sensitivity Analysis
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Explore how optimal serverless recommendations adapt as workload parameters and SLO targets change.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-sm flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* --- SENSITIVITY WORKBENCH CONTROLS --- */}
      <div className="glass-card p-6 border-indigo-500/30">
        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <Sparkles size={16} className="text-indigo-400" /> Workbench Parameters
        </h3>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading scenarios and variables...</div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Scenario Selector */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  1. Select Workload Scenario
                </label>
                <select
                  value={selectedScenarioId}
                  onChange={(e) => setSelectedScenarioId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  {scenarios.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.workload_type} — {s.request_volume.toLocaleString()} reqs/mo)
                    </option>
                  ))}
                </select>
              </div>

              {/* Variable Selector */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  2. Select Variable to Test
                </label>
                <select
                  value={selectedVariable}
                  onChange={(e) => setSelectedVariable(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  {variables.map((v) => (
                    <option key={v.key} value={v.key}>
                      {v.label} ({v.unit})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Presets & Custom Values */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-300">
                  3. Test Values (Comma-separated or click Preset)
                </label>
                <button
                  type="button"
                  onClick={handleApplyPreset}
                  className="text-[11px] font-semibold text-indigo-400 hover:underline"
                >
                  Load Recommended Preset Points
                </button>
              </div>

              {/* Preset Chips */}
              <div className="flex flex-wrap gap-2 mb-3">
                {getPresets().map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      const currentVals = customValuesInput
                        ? customValuesInput.split(',').map((v) => v.trim())
                        : []
                      if (!currentVals.includes(String(preset.value))) {
                        setCustomValuesInput([...currentVals, preset.value].join(', '))
                      }
                    }}
                    className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-700 hover:border-indigo-500 text-xs text-slate-300 hover:text-white transition-colors"
                  >
                    {preset.label}: <strong>{preset.value}</strong>
                  </button>
                ))}
              </div>

              <input
                type="text"
                value={customValuesInput}
                onChange={(e) => setCustomValuesInput(e.target.value)}
                placeholder="e.g. 50000, 75000, 100000, 150000, 200000"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>

            {/* Run Button */}
            <div className="pt-2 flex justify-end">
              <button
                onClick={() => handleRunAnalysis()}
                disabled={analysisLoading}
                className="btn-glow text-white text-xs font-bold px-6 py-2.5 rounded-xl flex items-center gap-2 disabled:opacity-40"
              >
                {analysisLoading ? <RefreshCw size={16} className="animate-spin" /> : <Play size={16} />}
                {analysisLoading ? 'Running Sensitivity Analysis...' : 'Run Sensitivity Analysis'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* --- RESULTS DASHBOARD --- */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* Automated Insight Summary Callout */}
          <div className="glass-card p-5 border-indigo-500/40 bg-slate-950/60">
            <div className="flex items-start gap-3">
              <Sparkles size={20} className="text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-white mb-1">
                  Sensitivity Insight Summary — {result.scenario_name}
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {result.insight_summary}
                </p>
                <p className="text-[10px] text-slate-500 mt-2">
                  ⚠ {result.disclaimer}
                </p>
              </div>
            </div>
          </div>

          {/* 3 Interactive Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Chart 1: Recommended Memory */}
            <div className="glass-card p-5">
              <h4 className="text-xs font-bold text-white mb-4 flex items-center gap-1.5">
                <Cpu size={15} className="text-indigo-400" /> Recommended Memory (MB)
              </h4>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={result.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" />
                    <XAxis dataKey="input_value" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 10 }} domain={[0, 3500]} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: 12, fontSize: 11 }}
                    />
                    <Bar dataKey="recommended_memory_mb" fill="#818cf8" radius={[4, 4, 0, 0]} name="Memory (MB)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Estimated Monthly Cost */}
            <div className="glass-card p-5">
              <h4 className="text-xs font-bold text-white mb-4 flex items-center gap-1.5">
                <DollarSign size={15} className="text-emerald-400" /> Estimated Cost ($/month)
              </h4>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={result.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" />
                    <XAxis dataKey="input_value" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: 12, fontSize: 11 }}
                    />
                    <Line type="monotone" dataKey="recommended_cost" stroke="#34d399" strokeWidth={2} dot={{ r: 4 }} name="Cost ($/mo)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 3: Estimated Latency */}
            <div className="glass-card p-5">
              <h4 className="text-xs font-bold text-white mb-4 flex items-center gap-1.5">
                <Clock size={15} className="text-cyan-400" /> Estimated Latency (ms)
              </h4>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={result.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" />
                    <XAxis dataKey="input_value" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: 12, fontSize: 11 }}
                    />
                    <Line type="monotone" dataKey="recommended_latency_ms" stroke="#22d3ee" strokeWidth={2} dot={{ r: 4 }} name="Latency (ms)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* Results Table */}
          <div className="glass-card p-6">
            <h4 className="text-sm font-bold text-white mb-4">
              Sensitivity Evaluation Points Table ({result.variable_label})
            </h4>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 uppercase text-slate-400 tracking-wider">
                    <th className="py-3 px-4">{result.variable_label} Value</th>
                    <th className="py-3 px-4">Recommended Memory</th>
                    <th className="py-3 px-4">Est. Cost ($/mo)</th>
                    <th className="py-3 px-4">Est. Latency (ms)</th>
                    <th className="py-3 px-4">Availability (%)</th>
                    <th className="py-3 px-4">Savings (%)</th>
                    <th className="py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {result.points.map((pt, idx) => {
                    const isBaseline = Math.abs(pt.input_value - result.baseline_value) < 0.0001
                    return (
                      <tr
                        key={idx}
                        className={`transition-colors ${
                          isBaseline ? 'bg-indigo-950/60 font-bold text-white border-l-4 border-l-indigo-400' : 'hover:bg-slate-900/40 text-slate-300'
                        }`}
                      >
                        <td className="py-3 px-4 flex items-center gap-2">
                          <span className="font-mono">{pt.input_value.toLocaleString()}</span>
                          {isBaseline && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase font-semibold">
                              Baseline
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 font-bold text-white">
                          {pt.recommended_memory_mb ? `${pt.recommended_memory_mb} MB` : 'N/A'}
                        </td>
                        <td className="py-3 px-4 font-mono">
                          {pt.recommended_cost ? `$${pt.recommended_cost.toLocaleString()}` : 'N/A'}
                        </td>
                        <td className="py-3 px-4">
                          {pt.recommended_latency_ms ? `${pt.recommended_latency_ms} ms` : 'N/A'}
                        </td>
                        <td className="py-3 px-4">
                          {pt.recommended_availability_percent ? `${pt.recommended_availability_percent}%` : 'N/A'}
                        </td>
                        <td className={`py-3 px-4 font-semibold ${pt.savings_percent > 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {pt.savings_percent !== null ? `${pt.savings_percent}%` : '0%'}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold border ${
                              pt.simulation_status === 'Recommended'
                                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                                : 'bg-red-500/15 text-red-400 border-red-500/30'
                            }`}
                          >
                            {pt.simulation_status}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
