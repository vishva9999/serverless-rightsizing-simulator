import { useState, useEffect } from 'react'
import {
  History as HistoryIcon,
  Trash2,
  Eye,
  GitCompare,
  X,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  DollarSign,
  Clock,
  ShieldCheck,
  Cpu,
  ArrowLeft
} from 'lucide-react'
import {
  fetchHistory,
  fetchHistoryById,
  deleteHistoryItem,
  compareHistoryRuns
} from '../services/api'

export default function History() {
  const [historyItems, setHistoryItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Selected history IDs for comparison (max 2)
  const [selectedForCompare, setSelectedForCompare] = useState([])

  // Active Comparison Result
  const [compareData, setCompareData] = useState(null)
  const [compareLoading, setCompareLoading] = useState(false)

  // Active View Detail Modal Item
  const [detailItem, setDetailItem] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchHistory()
      setHistoryItems(data)
    } catch (err) {
      console.error('Failed to load history:', err)
      setError('Failed to load simulation history.')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteItem = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this simulation history record?')) return
    try {
      await deleteHistoryItem(id)
      setSelectedForCompare((prev) => prev.filter((item) => item !== id))
      loadHistory()
    } catch (err) {
      alert('Failed to delete history item: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleToggleCompare = (id) => {
    if (selectedForCompare.includes(id)) {
      setSelectedForCompare(selectedForCompare.filter((item) => item !== id))
    } else {
      if (selectedForCompare.length >= 2) {
        // Keep latest 2 selected
        setSelectedForCompare([selectedForCompare[1], id])
      } else {
        setSelectedForCompare([...selectedForCompare, id])
      }
    }
  }

  const handleRunComparison = async () => {
    if (selectedForCompare.length !== 2) return
    setCompareLoading(true)
    setError(null)
    try {
      const data = await compareHistoryRuns(selectedForCompare[0], selectedForCompare[1])
      setCompareData(data)
    } catch (err) {
      alert('Comparison failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setCompareLoading(false)
    }
  }

  const handleViewDetail = async (id) => {
    try {
      const data = await fetchHistoryById(id)
      setDetailItem(data)
    } catch (err) {
      alert('Failed to fetch detail: ' + (err.response?.data?.detail || err.message))
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <HistoryIcon size={22} className="text-indigo-400" />
            Simulation History &amp; Audit Log
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Review previous simulation runs and compare performance deltas side-by-side.
          </p>
        </div>

        {compareData ? (
          <button
            onClick={() => setCompareData(null)}
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 hover:text-white"
          >
            <ArrowLeft size={14} /> Back to History Table
          </button>
        ) : (
          <button
            onClick={handleRunComparison}
            disabled={selectedForCompare.length !== 2 || compareLoading}
            className="btn-glow text-white text-xs font-bold px-4 py-2.5 rounded-xl flex items-center gap-2 disabled:opacity-40"
          >
            <GitCompare size={16} /> Compare Selected Runs ({selectedForCompare.length}/2)
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-sm flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* --- COMPARISON VIEW MODE --- */}
      {compareData ? (
        <div className="space-y-6 animate-fade-in">
          <div className="glass-card p-6 border-indigo-500/30">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <GitCompare size={18} className="text-indigo-400" /> Side-by-Side Simulation Comparison
            </h3>

            {/* Summary Banner */}
            <div className="p-4 rounded-xl mb-6 bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Cost Difference</span>
                <span className={`text-base font-bold ${compareData.comparison_summary.cost_difference <= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {compareData.comparison_summary.cost_difference <= 0 ? '' : '+'}${compareData.comparison_summary.cost_difference}/mo
                </span>
              </div>

              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Latency Difference</span>
                <span className="text-base font-bold text-cyan-400">
                  {compareData.comparison_summary.latency_difference_ms <= 0 ? '' : '+'}{compareData.comparison_summary.latency_difference_ms} ms
                </span>
              </div>

              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Recommendation Status</span>
                <span className={`text-xs font-semibold ${compareData.comparison_summary.same_recommendation ? 'text-emerald-400' : 'text-indigo-400'}`}>
                  {compareData.comparison_summary.same_recommendation ? 'Same Recommended Memory Tier' : 'Different Tier Selected'}
                </span>
              </div>
            </div>

            {/* Side-by-Side Run Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* RUN 1 */}
              <div className="glass-card p-5 border-cyan-500/30 bg-slate-950/40">
                <p className="text-xs text-cyan-400 uppercase font-semibold tracking-wider mb-1">Run 1 (Baseline Run)</p>
                <h4 className="text-base font-bold text-white mb-1">{compareData.run_1.scenario_name}</h4>
                <p className="text-[11px] text-slate-500 mb-4">{new Date(compareData.run_1.created_at).toLocaleString()}</p>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Recommended Memory</span>
                    <span className="font-bold text-white">{compareData.run_1.recommended_memory_mb ? `${compareData.run_1.recommended_memory_mb} MB` : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Monthly Cost</span>
                    <span className="font-bold text-white">${compareData.run_1.recommended_cost ? compareData.run_1.recommended_cost.toLocaleString() : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Est. Latency</span>
                    <span className="font-bold text-white">{compareData.run_1.recommended_latency_ms ? `${compareData.run_1.recommended_latency_ms} ms` : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Est. Availability</span>
                    <span className="font-bold text-white">{compareData.run_1.recommended_availability_percent ? `${compareData.run_1.recommended_availability_percent}%` : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Status</span>
                    <span className="font-bold text-emerald-400">{compareData.run_1.status}</span>
                  </div>
                </div>
              </div>

              {/* RUN 2 */}
              <div className="glass-card p-5 border-indigo-500/30 bg-slate-950/40">
                <p className="text-xs text-indigo-400 uppercase font-semibold tracking-wider mb-1">Run 2 (Comparison Run)</p>
                <h4 className="text-base font-bold text-white mb-1">{compareData.run_2.scenario_name}</h4>
                <p className="text-[11px] text-slate-500 mb-4">{new Date(compareData.run_2.created_at).toLocaleString()}</p>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Recommended Memory</span>
                    <span className="font-bold text-white">{compareData.run_2.recommended_memory_mb ? `${compareData.run_2.recommended_memory_mb} MB` : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Monthly Cost</span>
                    <span className="font-bold text-white">${compareData.run_2.recommended_cost ? compareData.run_2.recommended_cost.toLocaleString() : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Est. Latency</span>
                    <span className="font-bold text-white">{compareData.run_2.recommended_latency_ms ? `${compareData.run_2.recommended_latency_ms} ms` : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Est. Availability</span>
                    <span className="font-bold text-white">{compareData.run_2.recommended_availability_percent ? `${compareData.run_2.recommended_availability_percent}%` : 'N/A'}</span>
                  </div>
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Status</span>
                    <span className="font-bold text-emerald-400">{compareData.run_2.status}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* --- HISTORY TABLE MODE --- */
        <div className="glass-card p-6">
          {loading ? (
            <div className="p-12 text-center text-slate-400 text-sm">Loading history log...</div>
          ) : historyItems.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm">No simulation history found. Run a simulation from the Scenarios page to log history.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 uppercase text-slate-400 tracking-wider">
                    <th className="py-3 px-3 text-center">Compare</th>
                    <th className="py-3 px-4">Date / Time</th>
                    <th className="py-3 px-4">Scenario</th>
                    <th className="py-3 px-4">Rec. Memory</th>
                    <th className="py-3 px-4">Est. Cost</th>
                    <th className="py-3 px-4">Est. Latency</th>
                    <th className="py-3 px-4">Availability</th>
                    <th className="py-3 px-4">Savings</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {historyItems.map((item) => {
                    const isSelected = selectedForCompare.includes(item.id)
                    return (
                      <tr
                        key={item.id}
                        className={`transition-colors ${
                          isSelected ? 'bg-indigo-950/40 text-white font-medium' : 'hover:bg-slate-900/40 text-slate-300'
                        }`}
                      >
                        <td className="py-3 px-3 text-center">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => handleToggleCompare(item.id)}
                            className="rounded bg-slate-900 border-slate-700 text-indigo-500 focus:ring-indigo-500"
                          />
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                          {new Date(item.created_at).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 font-bold text-white">{item.scenario_name}</td>
                        <td className="py-3 px-4">
                          {item.recommended_memory_mb ? `${item.recommended_memory_mb} MB` : 'N/A'}
                        </td>
                        <td className="py-3 px-4 font-mono">
                          {item.recommended_cost ? `$${item.recommended_cost.toLocaleString()}` : 'N/A'}
                        </td>
                        <td className="py-3 px-4">
                          {item.recommended_latency_ms ? `${item.recommended_latency_ms} ms` : 'N/A'}
                        </td>
                        <td className="py-3 px-4">
                          {item.recommended_availability_percent ? `${item.recommended_availability_percent}%` : 'N/A'}
                        </td>
                        <td className={`py-3 px-4 font-semibold ${item.savings_percent > 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {item.savings_percent !== null ? `${item.savings_percent}%` : '0%'}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${
                              item.status === 'Recommended'
                                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                                : item.status === 'Near Optimal'
                                ? 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30'
                                : 'bg-red-500/15 text-red-400 border-red-500/30'
                            }`}
                          >
                            {item.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleViewDetail(item.id)}
                              className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800"
                              title="View detail JSON"
                            >
                              <Eye size={14} />
                            </button>
                            <button
                              onClick={(e) => handleDeleteItem(item.id, e)}
                              className="p-1 rounded text-slate-400 hover:text-red-400 hover:bg-slate-800"
                              title="Delete record"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* --- DETAIL MODAL --- */}
      {detailItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="glass-card w-full max-w-2xl p-6 relative border-indigo-500/40 max-h-[85vh] overflow-y-auto">
            <button
              onClick={() => setDetailItem(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X size={18} />
            </button>

            <h3 className="text-base font-bold text-white mb-2">Simulation Run Log Detail</h3>
            <p className="text-xs text-slate-400 mb-4">
              Scenario: <strong className="text-white">{detailItem.scenario_name}</strong> | Executed at {new Date(detailItem.created_at).toLocaleString()}
            </p>

            {detailItem.simulation_detail ? (
              <div className="space-y-4 text-xs">
                <div className="p-3 rounded bg-slate-900 border border-slate-800 whitespace-pre-line text-slate-300">
                  <p className="font-bold text-indigo-400 mb-1">Human-Readable Explanation:</p>
                  {detailItem.simulation_detail.explanation}
                </div>

                <div className="p-3 rounded bg-slate-900 border border-slate-800">
                  <p className="font-bold text-indigo-400 mb-2">Full Simulation JSON:</p>
                  <pre className="font-mono text-[11px] text-slate-300 overflow-x-auto bg-slate-950 p-3 rounded">
                    {JSON.stringify(detailItem.simulation_detail, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">No detailed JSON available for this run.</p>
            )}

            <div className="mt-4 text-right">
              <button
                onClick={() => setDetailItem(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-xs font-semibold text-white hover:bg-slate-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
