import React, { useState, useEffect } from 'react';
import { Flame, Zap, Loader2 } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { zoneService, ZoneItem } from '../services/api';

const DEFAULT_ZONES = [
  {
    id: 1,
    zone_code: 'ZONE-NORTH-01',
    zone_name: 'Sector North Ridge',
    type: 'WILDFIRE_CLUSTER',
    severity: 'CRITICAL',
    risk_score: 84.5,
    population: 14200,
    evacStatus: 'MANDATORY_EVACUATION',
    road_accessibility: 42.0,
    spreadRate: '2.4 km/h NW',
  },
  {
    id: 2,
    zone_code: 'ZONE-RIVER-02',
    zone_name: 'Sector West River Basin',
    type: 'FLOOD_SURGE',
    severity: 'HIGH',
    risk_score: 68.0,
    population: 8500,
    evacStatus: 'WARNING_ADVISORY',
    road_accessibility: 58.5,
    spreadRate: '0.8 km/h Rising',
  },
  {
    id: 3,
    zone_code: 'ZONE-IND-03',
    zone_name: 'Sector Industrial District',
    type: 'HAZMAT_PLUME',
    severity: 'MEDIUM',
    risk_score: 41.2,
    population: 3100,
    evacStatus: 'SHELTER_IN_PLACE',
    road_accessibility: 88.0,
    spreadRate: 'Stationary',
  },
];

export const DisasterZones: React.FC = () => {
  const [zones, setZones] = useState<any[]>(DEFAULT_ZONES);
  const [loading, setLoading] = useState<boolean>(true);
  const [pulsingId, setPulsingId] = useState<number | null>(null);

  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const data = await zoneService.getZones();
      if (data && data.length > 0) {
        const mapped = data.map((z: ZoneItem) => ({
          id: z.id,
          zone_code: z.zone_code,
          zone_name: z.zone_name,
          type: z.risk_level === 'CRITICAL' ? 'FIRE/EARTHQUAKE' : 'FLOOD/HYDRO',
          severity: z.risk_level,
          risk_score: z.risk_score,
          population: z.population,
          evacStatus: z.evacuation_priority === 'CRITICAL' ? 'MANDATORY_EVACUATION' : 'MONITORING',
          road_accessibility: z.road_accessibility,
          spreadRate: `${(z.risk_score * 0.03).toFixed(1)} km/h Vector`,
        }));
        setZones(mapped);
      }
    } catch {
      // Fallback to default
    } finally {
      setLoading(false);
    }
  };

  const handlePulse = async (id: number) => {
    setPulsingId(id);
    try {
      const updated = await zoneService.triggerHazardPulse(id, 8.0);
      setZones(prev => prev.map(z => {
        if (z.id === id) {
          return {
            ...z,
            risk_score: updated.risk_score,
            severity: updated.risk_level,
            road_accessibility: updated.road_accessibility,
          };
        }
        return z;
      }));
    } catch {
      setZones(prev => prev.map(z => {
        if (z.id === id) {
          return {
            ...z,
            risk_score: Math.min(100, z.risk_score + 8),
            severity: z.risk_score + 8 > 80 ? 'CRITICAL' : 'HIGH',
          };
        }
        return z;
      }));
    } finally {
      setPulsingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800 font-mono">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide">
              DISASTER ZONES MONITORING
            </h1>
            <StatusBadge status="simulated" label="SYNTHETIC HAZARD DATA" />
            {loading && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
          </div>
          <p className="text-xs text-slate-400">
            Real-time tracking of simulated hazard footprints, plume vectors, and population perimeters.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-cyan-400 font-bold">{zones.length} Active Zones Monitored</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
        {zones.map((zone) => (
          <div
            key={zone.id}
            className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-cyan-400 font-bold">{zone.zone_code}</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  zone.severity === 'CRITICAL'
                    ? 'bg-red-950/80 border border-red-700 text-red-300'
                    : zone.severity === 'HIGH'
                    ? 'bg-amber-950/80 border border-amber-700 text-amber-300'
                    : 'bg-emerald-950/80 border border-emerald-700 text-emerald-300'
                }`}
              >
                {zone.severity} ({zone.risk_score.toFixed(0)}%)
              </span>
            </div>

            <div>
              <h3 className="text-sm font-bold text-white">{zone.zone_name}</h3>
              <div className="flex items-center gap-1 text-xs text-slate-400 mt-0.5">
                <Flame className="w-3.5 h-3.5 text-amber-400" />
                <span>{zone.type}</span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs border-t border-slate-800/80 pt-2 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">Affected Population:</span>
                <span className="font-semibold text-white">{zone.population.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Road Access:</span>
                <span className="text-cyan-300 font-mono">{zone.road_accessibility.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Evacuation Status:</span>
                <span className="text-amber-300">{zone.evacStatus}</span>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/60">
              <button
                onClick={() => handlePulse(zone.id)}
                disabled={pulsingId === zone.id}
                className="px-2.5 py-1 rounded bg-red-950/70 hover:bg-red-900 border border-red-800 text-red-200 text-xs flex items-center gap-1 transition-colors"
              >
                {pulsingId === zone.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3 text-red-400" />}
                <span>Pulse Hazard</span>
              </button>
              <span className="text-slate-500 text-[10px]">Vectors: {zone.spreadRate}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
