import { Construction, ArrowRight } from 'lucide-react'

/**
 * Placeholder page — shown for nav items that are not yet implemented in Phase 1.
 * @param {string} pageName   - Display name of the page (e.g. "Scenarios")
 * @param {string} description - Short description of what this page will do
 * @param {string} phase       - Which phase this will be implemented in
 */
export default function Placeholder({ pageName = 'Page', description = '', phase = 'Phase 2' }) {
  const roadmapItems = {
    Scenarios:             ['Define workload scenarios', 'Set SLO targets', 'Compare multiple configs'],
    Simulator:             ['Run cost simulations', 'Apply rightsizing algorithms', 'Generate reports'],
    'Sensitivity Analysis':['Vary CPU/memory parameters', 'Plot cost sensitivity curves', 'Find optimal thresholds'],
    History:               ['View past simulations', 'Track cost trends over time', 'Export results'],
    Organizations:         ['Manage team workspaces', 'Role-based access control', 'Shared scenario library'],
    Settings:              ['Configure AWS integration', 'Set alert thresholds', 'Manage API keys'],
  }

  const items = roadmapItems[pageName] || ['Feature coming soon']

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="animate-fade-in">
        <h2 className="text-xl font-bold text-white mb-1">{pageName}</h2>
        <p className="text-sm" style={{ color: '#64748b' }}>
          {description || `This section will be available in ${phase}.`}
        </p>
      </div>

      <div className="glass-card p-8 mt-6 text-center animate-slide-up relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none"
          style={{ background: 'radial-gradient(circle at 50% 40%, rgba(99,102,241,0.07) 0, transparent 60%)' }} />

        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5"
          style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)' }}>
          <Construction size={28} style={{ color: '#6366f1' }} />
        </div>

        <h3 className="text-lg font-bold text-white mb-2">Under Construction</h3>
        <p className="text-sm mb-6 max-w-sm mx-auto" style={{ color: '#64748b' }}>
          This feature is planned for <strong className="text-white">{phase}</strong>.
          The Phase 1 foundation must be completed first.
        </p>

        {/* Planned features list */}
        <div className="text-left space-y-2 max-w-xs mx-auto">
          {items.map((item) => (
            <div key={item} className="flex items-center gap-3">
              <ArrowRight size={13} style={{ color: '#6366f1', flexShrink: 0 }} />
              <span className="text-sm" style={{ color: '#94a3b8' }}>{item}</span>
            </div>
          ))}
        </div>

        {/* Phase badge */}
        <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium"
          style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', color: '#a5b4fc' }}>
          Planned for {phase}
        </div>
      </div>
    </div>
  )
}
