import React, { useState, useEffect } from 'react';
import { Menu, Wifi, WifiOff, Clock, Database, UserCheck, LogOut } from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';
import { useHealth } from '../../hooks/useHealth';
import { formatTime } from '../../utils/formatters';

interface TopNavProps {
  onToggleSidebar: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { health, loading: healthLoading } = useHealth(8000);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const isBackendOnline = !healthLoading && health?.status === 'ok';

  return (
    <header className="h-16 bg-[#090e17] border-b border-slate-800/80 px-4 flex items-center justify-between sticky top-0 z-20">
      {/* Left: Mobile Toggle & Context Breadcrumb */}
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          aria-label="Toggle Sidebar Navigation"
          className="p-2 rounded-md bg-slate-900 border border-slate-800 text-slate-300 hover:text-white md:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2 font-mono text-xs text-slate-400">
          <span className="text-cyan-400 font-semibold">HQ-SECTOR-ALPHA</span>
          <span>/</span>
          <span className="text-slate-200">TACTICAL OPERATIONS</span>
        </div>
      </div>

      {/* Middle: System Clock & Live Status Indicators */}
      <div className="flex items-center gap-3 md:gap-6 font-mono text-xs">
        {/* UTC Clock */}
        <div className="hidden lg:flex items-center gap-1.5 text-slate-300 bg-[#0d131f] px-2.5 py-1 rounded border border-slate-800">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{formatTime(currentTime)}</span>
        </div>

        {/* Backend API Connection Indicator */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded border ${
            isBackendOnline
              ? 'bg-emerald-950/40 border-emerald-600/40 text-emerald-300'
              : 'bg-amber-950/40 border-amber-600/40 text-amber-300'
          }`}
          title={health?.database.message || 'Connecting to backend'}
        >
          {isBackendOnline ? (
            <Wifi className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          )}
          <span className="hidden sm:inline">
            API {isBackendOnline ? 'ONLINE' : 'DEGRADED'}
          </span>
        </div>

        {/* Database Status */}
        <div
          className={`hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded border ${
            health?.database.connected
              ? 'bg-cyan-950/40 border-cyan-600/40 text-cyan-300'
              : 'bg-slate-900 border-slate-800 text-slate-400'
          }`}
        >
          <Database className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-[11px]">
            DB: {health?.database.engine ? health.database.engine.toUpperCase() : 'CHECKING'}
          </span>
        </div>
      </div>

      {/* Right: Operator Profile & Session Action */}
      <div className="flex items-center gap-3">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col text-right font-mono">
              <span className="text-xs font-semibold text-white">
                {user.full_name || user.name || user.username}
              </span>
              <span className="text-[10px] text-cyan-400">
                {user.username} | {user.role}
              </span>
            </div>
            <div className="p-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <UserCheck className="w-4 h-4" />
            </div>
            <button
              id="logout-btn"
              onClick={logout}
              title="End Session"
              aria-label="Log Out"
              className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-red-400 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <a
            href="/login"
            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-mono font-bold text-xs rounded transition-colors"
          >
            SIGN IN
          </a>
        )}
      </div>
    </header>
  );
};
