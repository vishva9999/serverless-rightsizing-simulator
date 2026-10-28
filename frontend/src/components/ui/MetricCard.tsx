import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  status?: 'critical' | 'warning' | 'nominal' | 'info';
  subtext?: string;
  icon: LucideIcon;
  badge?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  isPositive,
  status = 'nominal',
  subtext,
  icon: Icon,
  badge,
}) => {
  const borderColors = {
    nominal: 'border-slate-800 hover:border-emerald-500/50',
    warning: 'border-amber-900/60 hover:border-amber-500/60',
    critical: 'border-red-900/60 hover:border-red-500/60',
    info: 'border-cyan-900/60 hover:border-cyan-500/60',
  };

  const glowEffects = {
    nominal: 'group-hover:text-emerald-400',
    warning: 'group-hover:text-amber-400',
    critical: 'group-hover:text-red-400',
    info: 'group-hover:text-cyan-400',
  };

  const statusGlows = {
    nominal: 'bg-emerald-500/10 text-emerald-400',
    warning: 'bg-amber-500/10 text-amber-400',
    critical: 'bg-red-500/10 text-red-400',
    info: 'bg-cyan-500/10 text-cyan-400',
  };

  return (
    <div
      className={`group relative bg-[#0d131f] border ${borderColors[status]} rounded-lg p-4 transition-all duration-200 shadow-sm hover:shadow-lg`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2 rounded-md ${statusGlows[status]} transition-colors`}>
          <Icon className={`w-4 h-4 ${glowEffects[status]}`} />
        </div>
      </div>

      <div className="flex items-baseline justify-between">
        <div className="text-2xl font-bold font-mono tracking-tight text-white">
          {value}
        </div>
        {change && (
          <span
            className={`text-xs font-mono font-medium ${
              isPositive ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {change}
          </span>
        )}
      </div>

      <div className="mt-2 flex items-center justify-between text-xs font-mono text-slate-400">
        <span>{subtext}</span>
        {badge && (
          <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300">
            {badge}
          </span>
        )}
      </div>
    </div>
  );
};
