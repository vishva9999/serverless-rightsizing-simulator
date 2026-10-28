import React from 'react';
import { Database, Server, Shield } from 'lucide-react';
import { useHealth } from '../hooks/useHealth';
import { StatusBadge } from '../components/ui/StatusBadge';

export const Settings: React.FC = () => {
  const { health } = useHealth();

  return (
    <div className="space-y-6 font-mono text-xs max-w-4xl">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide">
              SYSTEM & ENVIRONMENT SETTINGS
            </h1>
            <StatusBadge status="nominal" label="SETTINGS CONFIGURED" />
          </div>
          <p className="text-slate-400">
            Platform runtime configuration, API gateways, database health, and safety parameters.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Backend & Connectivity */}
        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex items-center gap-2 text-white font-semibold border-b border-slate-800 pb-2">
            <Server className="w-4 h-4 text-cyan-400" />
            <span>Backend Services Configuration</span>
          </div>

          <div className="space-y-2 text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">API Endpoint:</span>
              <span>http://localhost:8000/api</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">WebSocket Endpoint:</span>
              <span>ws://localhost:8000/ws</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Backend Health:</span>
              <span className="text-emerald-400 font-bold">{health?.status.toUpperCase() || 'CONNECTING'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Uptime:</span>
              <span>{health ? `${health.uptime_seconds}s` : 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Database Health */}
        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex items-center gap-2 text-white font-semibold border-b border-slate-800 pb-2">
            <Database className="w-4 h-4 text-cyan-400" />
            <span>Database Storage Engine</span>
          </div>

          <div className="space-y-2 text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">Dialect / Engine:</span>
              <span className="text-cyan-400">{health?.database.engine || 'postgresql'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Status:</span>
              <span className={health?.database.connected ? 'text-emerald-400' : 'text-amber-400'}>
                {health?.database.message || 'Testing...'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Fallback Allowed:</span>
              <span className="text-slate-300">YES (SQLite Dev Mode)</span>
            </div>
          </div>
        </div>

        {/* Safety & Compliance Policy */}
        <div className="md:col-span-2 bg-[#0d131f] border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex items-center gap-2 text-white font-semibold border-b border-slate-800 pb-2">
            <Shield className="w-4 h-4 text-amber-400" />
            <span>Operational Safety & Disclaimer Policy</span>
          </div>

          <p className="text-slate-400 leading-relaxed">
            This platform operates in strictly isolated simulation mode (<code className="text-cyan-300">IS_SIMULATION_MODE=true</code>).
            All routes, shelters, sensor readings, and casualty statistics are generated for algorithmic evaluation.
            Under no circumstance does this software execute API requests to live emergency dispatchers or municipal sirens.
          </p>
        </div>
      </div>
    </div>
  );
};
