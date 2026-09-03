import React from 'react'
import { Activity, Bell, User, Zap, Building2, Shield } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function Header() {
  const { user } = useAuth()

  return (
    <header
      className="h-16 flex items-center justify-between px-6 bg-slate-900/90 backdrop-blur-xl border-b border-slate-800"
    >
      {/* ── Left: Brand ─────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-br from-indigo-500 to-cyan-500 shadow-lg shadow-indigo-500/20">
          <Zap size={18} className="text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white leading-none">
            Serverless Rightsizing
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Cost &amp; Performance Simulator
          </p>
        </div>
      </div>

      {/* ── Center: Phase 6 Auth badge ───────────────────────── */}
      <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
        <Shield size={12} className="text-indigo-400" />
        <span>Phase 6 — RBAC &amp; Organizations</span>
      </div>

      {/* ── Right: User & Status Context ─────────────────────── */}
      <div className="flex items-center gap-4">
        {/* Status dot */}
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block shadow-sm shadow-emerald-400" />
          <span>Local Engine Active</span>
        </div>

        {/* User Pill */}
        {user && (
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700 text-xs">
            <div className="w-5 h-5 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center text-white font-bold text-[10px]">
              {user.full_name?.charAt(0) || 'U'}
            </div>
            <span className="text-white font-medium">{user.full_name}</span>
            <span className="text-slate-500">|</span>
            <span className="text-indigo-400 uppercase font-semibold text-[10px]">{user.role}</span>
          </div>
        )}
      </div>
    </header>
  )
}
