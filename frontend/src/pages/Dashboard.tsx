import React, { useState } from 'react';
import {
  Flame,
  Users,
  Home,
  Truck,
  BrainCircuit,
  AlertTriangle,
  Play,
  RotateCcw,
  Radio,
} from 'lucide-react';
import { MetricCard } from '../components/ui/MetricCard';
import { TacticalMap } from '../map/TacticalMap';
import { TelemetryCharts } from '../charts/TelemetryCharts';
import { StatusBadge } from '../components/ui/StatusBadge';
import { zoneService, auditLogService } from '../services/api';

export const Dashboard: React.FC = () => {
  const [drillActive, setDrillActive] = useState(true);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const triggerAction = async (msg: string, type: 'pulse' | 'ai' = 'pulse') => {
    setActionNotice(msg);
    try {
      if (type === 'pulse') {
        await zoneService.triggerHazardPulse(1, 15);
      }
      await auditLogService.recordLog({
        action: type === 'pulse' ? 'SIMULATE_HAZARD_PULSE' : 'RUN_AI_DISPATCH_OPTIMIZER',
        entity_type: 'COMMAND_CENTER_DASHBOARD',
        entity_id: 'SECTOR-01',
        new_value: { notification: msg },
      });
    } catch {
      // Offline fallback
    }
    setTimeout(() => setActionNotice(null), 4000);
  };

  return (
    <div className="space-y-6">
      {/* Action Notification Toast */}
      {actionNotice && (
        <div className="bg-cyan-950 border border-cyan-500/60 text-cyan-200 px-4 py-2.5 rounded-lg font-mono text-xs flex items-center justify-between shadow-lg animate-pulse">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400" />
            <span>[SIMULATED DISPATCH ACTION]: {actionNotice}</span>
          </div>
          <span className="text-[10px] bg-cyan-900/60 px-2 py-0.5 rounded text-cyan-300">
            SIMULATED EVENT
          </span>
        </div>
      )}

      {/* Top Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-mono font-bold text-white tracking-wide">
              COMMAND CENTER OVERVIEW
            </h1>
            <StatusBadge status="nominal" label="SYSTEM OPERATIONAL" />
            <StatusBadge status="simulated" label="SYNTHETIC SCENARIO" />
          </div>
          <p className="text-xs font-mono text-slate-400">
            Sector Pacific-Northwest / Scenario: Alpha-Seismic-Cluster-07 (Simulated Environment)
          </p>
        </div>

        {/* Quick Simulation Action Triggers */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <button
            onClick={() => triggerAction('Seismic tremor synthetic event triggered (Magnitude 6.4 sim)', 'pulse')}
            className="px-3 py-2 rounded bg-red-950/80 hover:bg-red-900 border border-red-700/60 text-red-200 flex items-center gap-1.5 transition-colors"
          >
            <Flame className="w-3.5 h-3.5 text-red-400" />
            <span>Simulate Hazard Pulse</span>
          </button>

          <button
            onClick={() => triggerAction('AI Resource Optimization recalculation executed for 12 sectors', 'ai')}
            className="px-3 py-2 rounded bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-700/60 text-cyan-200 flex items-center gap-1.5 transition-colors"
          >
            <BrainCircuit className="w-3.5 h-3.5 text-cyan-400" />
            <span>Run AI Dispatcher</span>
          </button>

          <button
            onClick={() => setDrillActive(!drillActive)}
            className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Toggle Exercise State"
          >
            {drillActive ? <RotateCcw className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Telemetry Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Active Hazards"
          value="3 Zones"
          status="critical"
          icon={Flame}
          subtext="Simulated Wildfire & Seismic"
          badge="TIER 4"
        />
        <MetricCard
          title="Evacuees In-Transit"
          value="18,420"
          change="+1,240/hr"
          isPositive={true}
          status="warning"
          icon={Users}
          subtext="Flow efficiency: 84%"
          badge="CORRIDOR A-9"
        />
        <MetricCard
          title="Shelter Occupancy"
          value="68.4%"
          change="+4.2%"
          isPositive={false}
          status="nominal"
          icon={Home}
          subtext="12 of 18 Shelters Active"
          badge="4,210 BEDS REMAIN"
        />
        <MetricCard
          title="Fleet Deployed"
          value="84 / 100"
          status="info"
          icon={Truck}
          subtext="16 Buses in reserve"
          badge="84% DEPLOYED"
        />
        <MetricCard
          title="AI Confidence"
          value="94.6%"
          status="nominal"
          icon={BrainCircuit}
          subtext="Scikit Model v1.2"
          badge="MULTI-CRITERIA"
        />
      </div>

      {/* Main Grid: Map & Live Incident Ticker */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Panel (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <TacticalMap className="h-[430px] w-full" />
          <TelemetryCharts />
        </div>

        {/* Tactical Feed & Decision Queue (1 col) */}
        <div className="space-y-4">
          {/* AI Decision Recommendations */}
          <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 font-mono">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  AI Decision Support Recommendations
                </h3>
              </div>
              <span className="text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800/60 px-1.5 py-0.5 rounded">
                SIMULATED AI
              </span>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="p-2.5 rounded bg-slate-900/90 border border-amber-500/30">
                <div className="flex items-center justify-between text-amber-300 font-semibold mb-1">
                  <span>Reroute Evacuation Corridor B</span>
                  <span className="text-[10px] bg-amber-950 px-1.5 rounded">URGENT</span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Projected hazard perimeter expansion intersects Sector 4 bridge in 42 mins. Reroute via Hwy 101 South.
                </p>
                <div className="mt-2 flex justify-end">
                  <button
                    onClick={() => triggerAction('Corridor B reroute simulated instructions broadcasted')}
                    className="px-2 py-1 bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-[10px] rounded transition-colors"
                  >
                    Simulate Approval
                  </button>
                </div>
              </div>

              <div className="p-2.5 rounded bg-slate-900/90 border border-cyan-500/30">
                <div className="flex items-center justify-between text-cyan-300 font-semibold mb-1">
                  <span>Dispatch 8 Reserve Fleets to Shelter Beta</span>
                  <span className="text-[10px] bg-cyan-950 px-1.5 rounded">REBALANCE</span>
                </div>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Shelter Alpha approaching 85% capacity threshold. Pre-position transit assets to Shelter Beta.
                </p>
                <div className="mt-2 flex justify-end">
                  <button
                    onClick={() => triggerAction('Fleet rebalance simulated dispatch deployed')}
                    className="px-2 py-1 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-[10px] rounded transition-colors"
                  >
                    Simulate Approval
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Incident Log Feed */}
          <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 font-mono">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Simulated Incident Telemetry</span>
              </h3>
              <span className="text-[10px] text-slate-400">Live Feed</span>
            </div>

            <div className="space-y-2 text-xs divide-y divide-slate-800/60">
              <div className="pt-2 flex items-start gap-2.5">
                <span className="text-[10px] text-cyan-400 mt-0.5">14:12:08</span>
                <div>
                  <div className="text-slate-200 font-semibold">Plume Dispersion Update</div>
                  <div className="text-slate-400 text-[11px]">Radius expanded +0.4 km NW (Simulated engine)</div>
                </div>
              </div>
              <div className="pt-2 flex items-start gap-2.5">
                <span className="text-[10px] text-amber-400 mt-0.5">14:08:45</span>
                <div>
                  <div className="text-slate-200 font-semibold">Shelter Alpha Near Capacity</div>
                  <div className="text-slate-400 text-[11px]">650 / 800 beds occupied; triage unit active</div>
                </div>
              </div>
              <div className="pt-2 flex items-start gap-2.5">
                <span className="text-[10px] text-emerald-400 mt-0.5">14:02:11</span>
                <div>
                  <div className="text-slate-200 font-semibold">Evacuation Route 7 Clear</div>
                  <div className="text-slate-400 text-[11px]">Bottleneck relieved by simulated traffic routing</div>
                </div>
              </div>
              <div className="pt-2 flex items-start gap-2.5">
                <span className="text-[10px] text-slate-400 mt-0.5">13:55:00</span>
                <div>
                  <div className="text-slate-200 font-semibold">Simulated Scenario Initialized</div>
                  <div className="text-slate-400 text-[11px]">Scenario Alpha-Seismic-Cluster-07 loaded</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
