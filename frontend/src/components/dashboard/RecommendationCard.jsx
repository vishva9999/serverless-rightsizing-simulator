import { Sparkles, CheckCircle2, AlertTriangle, HelpCircle, ShieldCheck, Zap, DollarSign, Clock, Cpu } from 'lucide-react'

/**
 * RecommendationCard — Displays optimal rightsizing recommendation,
 * metric breakdown, feasibility status, and "Why this configuration?" explanation.
 */
export default function RecommendationCard({ simulationResult }) {
  if (!simulationResult) {
    return <DefaultPhaseInfoCard />
  }

  const { recommendation, baseline, explanation, simulation_status } = simulationResult
  const isFeasible = simulation_status === 'success' && recommendation
  const isNearOptimalBaseline = isFeasible && baseline && recommendation.memory_mb === baseline.memory_mb

  return (
    <div className="glass-card p-6 animate-slide-up relative overflow-hidden h-full flex flex-col justify-between"
      style={{ animationDelay: '200ms' }}>

      {/* Background ambient glow */}
      <div className="absolute -top-12 -right-12 w-44 h-44 rounded-full pointer-events-none"
        style={{
          background: isFeasible
            ? 'radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(239,68,68,0.15) 0%, transparent 70%)'
        }} />

      <div>
        {/* Header row */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{
                background: isFeasible
                  ? 'linear-gradient(135deg,#10b981,#06b6d4)'
                  : 'linear-gradient(135deg,#f59e0b,#ef4444)',
                boxShadow: isFeasible ? '0 0 16px rgba(16,185,129,0.4)' : '0 0 16px rgba(239,68,68,0.4)'
              }}>
              <Sparkles size={20} className="text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Recommended Configuration</h3>
              <p className="text-xs text-slate-400">Simulation Estimate</p>
            </div>
          </div>

          <span className="text-xs px-3 py-1 rounded-full font-semibold flex items-center gap-1.5"
            style={{
              background: isFeasible ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
              color: isFeasible ? '#34d399' : '#f87171',
              border: `1px solid ${isFeasible ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`
            }}>
            {isFeasible ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
            {isNearOptimalBaseline ? 'Already Near-Optimal' : isFeasible ? 'Performance Target Met' : 'No Target Met'}
          </span>
        </div>

        {/* Highlight Banner / Memory size */}
        {isFeasible ? (
          <div className="p-4 rounded-xl mb-4"
            style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)' }}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">Recommended Memory</p>
                <p className="text-3xl font-extrabold text-white mt-0.5">{recommendation.memory_mb} MB</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400 font-medium">Cost Impact</p>
                {isNearOptimalBaseline ? (
                  <p className="text-sm font-bold text-emerald-400 mt-1">
                    Current configuration is already near-optimal
                  </p>
                ) : (
                  <p className={`text-xl font-bold ${recommendation.cost_savings_percentage >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {recommendation.cost_savings_percentage >= 0 ? '+' : ''}{recommendation.cost_savings_percentage}%
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-xl mb-4"
            style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
            <p className="text-sm font-semibold text-red-400 flex items-center gap-2">
              <AlertTriangle size={16} /> Constraint Violation
            </p>
            <p className="text-xs text-slate-300 mt-1">
              No configuration satisfies both latency and availability SLO targets.
            </p>
          </div>
        )}

        {/* Metrics Grid */}
        {isFeasible && (
          <div className="grid grid-cols-2 gap-3 mb-5">
            <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                <DollarSign size={13} className="text-emerald-400" />
                <span>Monthly Cost</span>
              </div>
              <p className="text-sm font-bold text-white">${recommendation.estimated_monthly_cost.toLocaleString()}</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                <Clock size={13} className="text-cyan-400" />
                <span>Est. Latency</span>
              </div>
              <p className="text-sm font-bold text-white">{recommendation.estimated_latency_ms} ms</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                <ShieldCheck size={13} className="text-purple-400" />
                <span>Est. Availability</span>
              </div>
              <p className="text-sm font-bold text-white">{recommendation.estimated_availability}%</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                <Cpu size={13} className="text-indigo-400" />
                <span>Status</span>
              </div>
              <p className="text-sm font-bold text-emerald-400">
                {isNearOptimalBaseline ? 'Near-Optimal' : 'Feasible'}
              </p>
            </div>
          </div>
        )}

        {/* "Why this configuration?" section */}
        <div className="pt-4 border-t border-indigo-500/15">
          <h4 className="text-xs font-semibold text-indigo-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <HelpCircle size={14} className="text-indigo-400" />
            Why this configuration?
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/40 p-3 rounded-lg border border-slate-800/80">
            {explanation}
          </p>
        </div>
      </div>
    </div>
  )
}

function DefaultPhaseInfoCard() {
  return (
    <div className="glass-card p-6 animate-slide-up relative overflow-hidden h-full">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: 'linear-gradient(135deg,#6366f1,#22d3ee)', boxShadow: '0 0 16px rgba(99,102,241,0.4)' }}>
          <Sparkles size={18} className="text-white" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">AI Recommendation Engine</h3>
          <span className="text-xs px-2 py-0.5 rounded-full font-medium mt-1 inline-block"
            style={{ background: 'rgba(16,185,129,0.15)', color: '#34d399', border: '1px solid rgba(16,185,129,0.3)' }}>
            Phase 2 Engine Ready
          </span>
        </div>
      </div>

      <p className="text-sm mb-5 leading-relaxed text-slate-400">
        Run a simulation in the <strong className="text-white">Simulator</strong> tab to evaluate candidate configurations (512MB – 3072MB) against your latency and availability targets.
      </p>

      <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-500/20 text-xs text-indigo-300 space-y-1">
        <p className="font-semibold text-white flex items-center gap-1.5">
          <Zap size={14} className="text-indigo-400" /> Dynamic Rightsizing Engine
        </p>
        <p>Calculates cost savings, estimates latency/availability trade-offs, and recommends the best feasible tier.</p>
      </div>
    </div>
  )
}
