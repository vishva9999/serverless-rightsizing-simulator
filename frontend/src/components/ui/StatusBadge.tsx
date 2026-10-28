import React from 'react';

interface StatusBadgeProps {
  status: 'nominal' | 'warning' | 'critical' | 'info' | 'simulated';
  label?: string;
  className?: string;
  pulse?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  className = '',
  pulse = false,
}) => {
  const styles = {
    nominal: 'bg-emerald-950/70 border-emerald-600 text-emerald-300',
    warning: 'bg-amber-950/70 border-amber-600 text-amber-300',
    critical: 'bg-red-950/70 border-red-600 text-red-300',
    info: 'bg-cyan-950/70 border-cyan-600 text-cyan-300',
    simulated: 'bg-purple-950/70 border-purple-500 text-purple-300',
  };

  const dotStyles = {
    nominal: 'bg-emerald-400',
    warning: 'bg-amber-400',
    critical: 'bg-red-400',
    info: 'bg-cyan-400',
    simulated: 'bg-purple-400',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border uppercase tracking-wider ${styles[status]} ${className}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${dotStyles[status]} ${
          pulse ? 'animate-ping' : ''
        }`}
      />
      {label || status}
    </span>
  );
};
