import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Flame,
  Milestone,
  Home,
  Truck,
  Cpu,
  BarChart3,
  FileText,
  Settings,
  ChevronRight,
  Shield,
} from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

const NAV_ITEMS = [
  { name: 'Command Center', path: '/', icon: LayoutDashboard },
  { name: 'Disaster Zones', path: '/zones', icon: Flame },
  { name: 'Evacuation', path: '/evacuation', icon: Milestone },
  { name: 'Shelters', path: '/shelters', icon: Home },
  { name: 'Resources', path: '/resources', icon: Truck },
  { name: 'Simulation', path: '/simulation', icon: Cpu },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Audit Logs', path: '/audit-logs', icon: FileText },
  { name: 'Settings', path: '/settings', icon: Settings },
];

const ROLE_ALLOWED_PATHS: Record<string, string[]> = {
  ADMIN: ['/', '/zones', '/evacuation', '/shelters', '/resources', '/simulation', '/analytics', '/audit-logs', '/settings'],
  DISASTER_OPERATOR: ['/', '/zones', '/evacuation', '/simulation', '/analytics'],
  FIELD_OFFICER: ['/', '/evacuation'],
  SHELTER_MANAGER: ['/', '/shelters'],
  RESOURCE_MANAGER: ['/', '/resources'],
  VIEWER: ['/', '/analytics'],
  'Incident Commander': ['/', '/zones', '/evacuation', '/shelters', '/resources', '/simulation', '/analytics', '/audit-logs', '/settings'],
  'Logistics Coordinator': ['/', '/shelters', '/resources'],
  'Field Dispatcher': ['/', '/zones', '/evacuation'],
  'Simulation Analyst': ['/', '/simulation', '/analytics'],
};

export const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const { user } = useAuth();
  const currentRole = user?.role || 'ADMIN';
  const allowedPaths = ROLE_ALLOWED_PATHS[currentRole] || ROLE_ALLOWED_PATHS.ADMIN;

  const visibleNavItems = NAV_ITEMS.filter((item) => allowedPaths.includes(item.path));

  return (
    <aside
      className={`fixed top-0 bottom-0 left-0 z-30 w-64 bg-[#090e17] border-r border-slate-800/80 flex flex-col transition-transform duration-200 ease-in-out md:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 flex items-center gap-3 border-b border-slate-800/80 bg-[#0d131f]">
        <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
          <Shield className="w-5 h-5 animate-pulse" />
        </div>
        <div className="flex flex-col">
          <span className="font-mono font-bold text-sm text-white tracking-wider">
            AEGIS COMMAND
          </span>
          <span className="font-mono text-[10px] text-cyan-400 uppercase tracking-widest">
            AI TACTICAL DECISION
          </span>
        </div>
      </div>

      {/* Navigation List */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-widest text-slate-400 flex justify-between items-center">
          <span>Operational Views</span>
          <span className="text-[9px] text-cyan-500 border border-cyan-500/30 px-1 py-0.5 rounded">
            {currentRole}
          </span>
        </div>

        {visibleNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `group flex items-center justify-between px-3 py-2.5 rounded-md text-xs font-mono font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-950/60 border border-cyan-500/40 text-cyan-300 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isActive
                          ? 'text-cyan-400'
                          : 'text-slate-400 group-hover:text-slate-200'
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>
                  {isActive && (
                    <ChevronRight className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Simulation Engine Status Widget */}
      <div className="p-3 m-3 rounded-lg bg-[#0b101b] border border-slate-800 text-[11px] font-mono">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span>SIMULATION ENGINE</span>
          <span className="flex items-center gap-1 text-emerald-400 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            ACTIVE
          </span>
        </div>
        <div className="text-[10px] text-slate-400">
          Synthetic Clock: 1.0x Realtime
        </div>
        <div className="mt-2 w-full bg-slate-800 rounded-full h-1">
          <div className="bg-cyan-500 h-1 rounded-full w-3/4"></div>
        </div>
      </div>
    </aside>
  );
};
