import React, { useState, useEffect } from 'react';
import { Milestone, GitMerge, Loader2 } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { evacuationService, EvacuationRouteItem } from '../services/api';

const DEFAULT_ROUTES = [
  {
    id: 1,
    corridor: 'Corridor Alpha (Hwy 101 N)',
    flowRate: '1,850 veh/hr',
    congestion: 78,
    status: 'CAUTION',
    action: 'Rerouting alternate lanes via Exit 12',
    alternate: 'State Route 82',
    safetyScore: 72,
    timeMins: 38,
  },
  {
    id: 2,
    corridor: 'Corridor Beta (Interstate 280)',
    flowRate: '3,200 veh/hr',
    congestion: 34,
    status: 'SAFE',
    action: 'Primary outbound express transit active',
    alternate: 'None Needed',
    safetyScore: 94,
    timeMins: 22,
  },
  {
    id: 3,
    corridor: 'Corridor Gamma (Coast Hwy 1)',
    flowRate: '420 veh/hr',
    congestion: 92,
    status: 'BLOCKED',
    action: 'Emergency vehicles and authorized convoys only',
    alternate: 'Corridor Beta',
    safetyScore: 18,
    timeMins: 75,
  },
];

export const Evacuation: React.FC = () => {
  const [routes, setRoutes] = useState<any[]>(DEFAULT_ROUTES);
  const [loading, setLoading] = useState<boolean>(true);
  const [actingId, setActingId] = useState<number | null>(null);

  useEffect(() => {
    fetchRoutes();
  }, []);

  const fetchRoutes = async () => {
    try {
      const data = await evacuationService.getRoutes();
      if (data && data.length > 0) {
        const mapped = data.map((r: EvacuationRouteItem, idx: number) => ({
          id: r.id,
          corridor: `Corridor ${String.fromCharCode(65 + (idx % 26))} (Route #${r.id})`,
          flowRate: `${Math.round(2500 - r.congestion_score * 18)} veh/hr`,
          congestion: Math.round(r.congestion_score),
          status: r.route_status,
          action: r.congestion_score > 60 ? 'Contraflow recommendation active' : 'Normal throughput',
          alternate: r.congestion_score > 60 ? 'Bypass Corridor Beta' : 'Direct Egress',
          safetyScore: Math.round(r.safety_score),
          timeMins: Math.round(r.estimated_time_minutes),
        }));
        setRoutes(mapped);
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  const handleToggleContraflow = async (id: number) => {
    setActingId(id);
    try {
      const updated = await evacuationService.toggleContraflow(id);
      setRoutes(prev => prev.map(r => {
        if (r.id === id) {
          return {
            ...r,
            congestion: Math.round(updated.congestion_score),
            timeMins: Math.round(updated.estimated_time_minutes),
            flowRate: `${Math.round(2500 - updated.congestion_score * 18)} veh/hr`,
          };
        }
        return r;
      }));
    } catch {
      setRoutes(prev => prev.map(r => {
        if (r.id === id) {
          const newCongestion = r.congestion > 40 ? r.congestion - 30 : r.congestion + 30;
          return {
            ...r,
            congestion: newCongestion,
            timeMins: Math.round(r.timeMins * 0.8),
          };
        }
        return r;
      }));
    } finally {
      setActingId(null);
    }
  };

  const handleToggleStatus = async (id: number, currentStatus: string) => {
    setActingId(id);
    const nextStatus = currentStatus === 'SAFE' ? 'CAUTION' : currentStatus === 'CAUTION' ? 'BLOCKED' : 'SAFE';
    try {
      const updated = await evacuationService.updateStatus(id, nextStatus);
      setRoutes(prev => prev.map(r => {
        if (r.id === id) {
          return {
            ...r,
            status: updated.route_status,
            safetyScore: Math.round(updated.safety_score),
            congestion: Math.round(updated.congestion_score),
          };
        }
        return r;
      }));
    } catch {
      setRoutes(prev => prev.map(r => {
        if (r.id === id) {
          return { ...r, status: nextStatus };
        }
        return r;
      }));
    } finally {
      setActingId(null);
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide">
              EVACUATION ROUTING & CONGESTION
            </h1>
            <StatusBadge status="simulated" label="SYNTHETIC TRAFFIC SIMULATION" />
            {loading && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
          </div>
          <p className="text-xs text-slate-400">
            Intelligent routing models for dynamic contraflow, bottleneck mitigation, and egress safety.
          </p>
        </div>
      </div>

      <div className="bg-[#0d131f] border border-slate-800 rounded-lg overflow-hidden text-xs">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2 text-slate-300 font-semibold">
            <Milestone className="w-4 h-4 text-cyan-400" />
            <span>Active Egress Corridors ({routes.length} Monitored Routes)</span>
          </div>
          <span className="text-slate-500 text-[11px]">Algorithm: Dijkstra Dynamic Flow v2</span>
        </div>

        <div className="divide-y divide-slate-800/80">
          {routes.map((route) => (
            <div key={route.id} className="p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-white">{route.corridor}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      route.status === 'SAFE'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : route.status === 'CAUTION'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-red-950 text-red-300 border border-red-800'
                    }`}
                  >
                    {route.status}
                  </span>
                  <span className="text-[10px] text-slate-500">Est: {route.timeMins} mins</span>
                </div>
                <p className="text-slate-400 text-xs">{route.action}</p>
              </div>

              <div className="flex flex-wrap items-center gap-6 text-slate-300">
                <div>
                  <div className="text-slate-500 text-[10px]">Flow Rate</div>
                  <div className="font-semibold text-white">{route.flowRate}</div>
                </div>
                <div>
                  <div className="text-slate-500 text-[10px]">Congestion Index</div>
                  <div className="font-semibold text-white">{route.congestion}%</div>
                </div>
                <div>
                  <div className="text-slate-500 text-[10px]">Safety Score</div>
                  <div className="font-semibold text-cyan-400">{route.safetyScore}/100</div>
                </div>
                <div>
                  <div className="text-slate-500 text-[10px]">Alt Route</div>
                  <div className="font-semibold text-cyan-400">{route.alternate}</div>
                </div>

                <div className="flex items-center gap-2 pt-2 lg:pt-0">
                  <button
                    onClick={() => handleToggleContraflow(route.id)}
                    disabled={actingId === route.id}
                    className="px-2.5 py-1.5 rounded bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-200 text-xs flex items-center gap-1 transition-colors"
                  >
                    <GitMerge className="w-3.5 h-3.5" />
                    <span>Contraflow</span>
                  </button>
                  <button
                    onClick={() => handleToggleStatus(route.id, route.status)}
                    disabled={actingId === route.id}
                    className="px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors"
                  >
                    Cycle Status
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
