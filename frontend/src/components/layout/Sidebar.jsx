import React from 'react'
import {
  LayoutDashboard,
  FlaskConical,
  Cpu,
  LineChart,
  History,
  Building2,
  Settings,
  ChevronRight,
  LogOut,
  UserCheck
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function Sidebar({ activePage, onNavigate }) {
  const { user, logout, hasRole } = useAuth()

  // Role-based visibility
  const isAdmin = hasRole('admin')
  const isAnalyst = hasRole('analyst')
  const isViewer = hasRole('viewer')

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'analyst', 'viewer'] },
    { id: 'scenarios', label: 'Scenarios', icon: FlaskConical, roles: ['admin', 'analyst', 'viewer'] },
    { id: 'simulator', label: 'Simulator', icon: Cpu, roles: ['admin', 'analyst'] },
    { id: 'sensitivity', label: 'Sensitivity Analysis', icon: LineChart, roles: ['admin', 'analyst'] },
    { id: 'history', label: 'History', icon: History, roles: ['admin', 'analyst', 'viewer'] },
    { id: 'organizations', label: 'Organizations', icon: Building2, roles: ['admin', 'analyst'] },
    { id: 'settings', label: 'Settings', icon: Settings, roles: ['admin', 'analyst', 'viewer'] },
  ]

  const visibleItems = navItems.filter(item => {
    if (!user || !user.role) return true
    return item.roles.includes(user.role.toLowerCase())
  })

  return (
    <aside
      className="w-64 flex-shrink-0 flex flex-col h-full bg-slate-900/95 backdrop-blur-xl border-r border-slate-800"
    >
      {/* ── Navigation List ────────────────────────────────── */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Main navigation">
        <p className="px-3 mb-3 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
          Navigation
        </p>

        {visibleItems.map((item) => (
          <NavButton
            key={item.id}
            item={item}
            active={activePage === item.id}
            onClick={() => onNavigate(item.id)}
          />
        ))}
      </nav>

      {/* ── User Account & Organization Context ─────────────── */}
      {user && (
        <div className="p-3 mx-3 mb-3 bg-slate-800/80 border border-slate-700/80 rounded-2xl">
          <div className="flex items-center space-x-2.5 mb-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs uppercase">
              {user.full_name?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-white truncate">{user.full_name}</div>
              <div className="text-[10px] text-slate-400 truncate">{user.email}</div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-700/60">
            <span
              className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                user.role === 'admin'
                  ? 'bg-purple-500/10 text-purple-300 border border-purple-500/20'
                  : user.role === 'analyst'
                  ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                  : 'bg-slate-700 text-slate-300'
              }`}
            >
              {user.role}
            </span>

            <button
              onClick={logout}
              className="text-slate-400 hover:text-red-400 text-xs flex items-center space-x-1 p-1 rounded hover:bg-slate-700/50 transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="text-[11px]">Logout</span>
            </button>
          </div>
        </div>
      )}
    </aside>
  )
}

function NavButton({ item, active, onClick }) {
  const Icon = item.icon
  return (
    <button
      id={`nav-${item.id}`}
      onClick={onClick}
      className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
        active
          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 font-semibold'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
      }`}
    >
      <Icon size={16} className="flex-shrink-0" />
      <span className="flex-1 text-left">{item.label}</span>
      {active && <ChevronRight size={14} className="text-white" />}
    </button>
  )
}
