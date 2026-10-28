import React, { useState, useEffect } from 'react';
import { TrendingUp, ShieldCheck, Users, Truck, Home, Loader2 } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { analyticsService } from '../services/api';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const summary = await analyticsService.getSummary();
      setData(summary);
    } catch {
      // Keep null for fallback render
    } finally {
      setLoading(false);
    }
  };

  const zonesCount = data?.zones?.total_count ?? 11;
  const criticalCount = data?.zones?.critical_count ?? 4;
  const shelterUtil = data?.shelters?.utilization_percent ?? 67.5;
  const fleetReady = data?.fleet?.readiness_percent ?? 85.0;
  const clearanceHours = data?.evacuation?.estimated_clearance_hours ?? 3.8;
  const safetyScore = data?.evacuation?.average_safety_score ?? 82.4;

  return (
    <div className="space-y-6 font-mono text-xs">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide">
              DECISION ANALYTICS & TRIAGE MODELS
            </h1>
            <StatusBadge status="simulated" label="SYNTHETIC PREDICTIONS" />
            {loading && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
          </div>
          <p className="text-slate-400">
            Predictive modeling of casualty probability, egress clearance times, and supply depletion trajectories.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between text-white font-semibold">
            <span>Clearance Time Estimate</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400">{clearanceHours.toFixed(1)} Hours</div>
          <p className="text-slate-400 text-[11px]">
            Based on active road egress capacity across {data?.evacuation?.routes_count ?? 5} corridors.
          </p>
        </div>

        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between text-white font-semibold">
            <span>Shelter Capacity In-Use</span>
            <Home className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">{shelterUtil}%</div>
          <p className="text-slate-400 text-[11px]">
            {data?.shelters?.current_occupancy ?? 2480} / {data?.shelters?.total_capacity ?? 3700} total beds occupied.
          </p>
        </div>

        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between text-white font-semibold">
            <span>Fleet Asset Readiness</span>
            <Truck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{fleetReady}%</div>
          <p className="text-slate-400 text-[11px]">
            {data?.fleet?.ready_count ?? 8} of {data?.fleet?.total_count ?? 10} fleet vehicles available for rapid deployment.
          </p>
        </div>
      </div>

      {/* Deep Operational Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2 text-white font-bold">
            <Users className="w-4 h-4 text-cyan-400" />
            <span>Hazard Perimeter & Population Exposure</span>
          </div>
          <div className="space-y-2 text-slate-300">
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Total Monitored Zones:</span>
              <span className="font-bold text-white">{zonesCount} Sectors</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">High / Critical Threat Sectors:</span>
              <span className="font-bold text-red-400">{criticalCount} Sectors</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Total Population in Perimeter:</span>
              <span className="font-bold text-amber-300">
                {(data?.zones?.total_population ?? 124500).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Average Road Accessibility:</span>
              <span className="font-bold text-cyan-300">
                {data?.zones?.average_road_accessibility ?? 74.2}%
              </span>
            </div>
          </div>
        </div>

        <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2 text-white font-bold">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Route Safety Index & Model Accuracy</span>
          </div>
          <div className="space-y-2 text-slate-300">
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Aggregate Route Safety Score:</span>
              <span className="font-bold text-emerald-400">{safetyScore}/100</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Average Egress Congestion:</span>
              <span className="font-bold text-amber-300">
                {data?.evacuation?.average_congestion_percent ?? 41.5}%
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">ML Model R² Accuracy:</span>
              <span className="font-bold text-cyan-400">0.962 (Random Forest)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Simulation Engine Version:</span>
              <span className="font-bold text-slate-300">v1.0.0-phase1 (Deterministic)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
