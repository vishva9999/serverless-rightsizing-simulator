import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

export const SimulationBanner: React.FC = () => {
  return (
    <aside
      aria-label="Simulation Environment Notice"
      className="bg-gradient-to-r from-amber-950/90 via-slate-900/90 to-amber-950/90 border-b border-amber-500/40 px-4 py-1.5 text-xs text-amber-200 flex items-center justify-between shadow-inner backdrop-blur-md"
    >
      <div className="flex items-center gap-2 font-mono">
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        </span>
        <div className="flex items-center gap-1.5 font-bold tracking-wider text-amber-300">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>SIMULATION MODE ACTIVE</span>
        </div>
        <span className="hidden md:inline text-amber-200/80">
          — All disaster zones, casualties, sensor feeds & resource fleets are mathematically simulated.
        </span>
      </div>

      <div className="flex items-center gap-2 font-mono text-[11px] text-amber-300/90">
        <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
        <span className="font-semibold">NO REAL DISPATCH</span>
      </div>
    </aside>
  );
};
