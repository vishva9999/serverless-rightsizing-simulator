import React, { useState, useEffect } from 'react';
import { Truck, Package, Send, Loader2, CheckCircle2 } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { resourceService, VehicleItem } from '../services/api';

const DEFAULT_FLEETS = [
  { id: 1, vehicle_code: 'FLEET-BUS-01', vehicle_type: 'Evacuation Transit Bus', capacity: 45, status: 'AVAILABLE', fuelAvg: '82%' },
  { id: 2, vehicle_code: 'FLEET-MED-02', vehicle_type: 'Mobile Medical Van', capacity: 6, status: 'DEPLOYED', fuelAvg: '90%' },
  { id: 3, vehicle_code: 'FLEET-SUPPLY-03', vehicle_type: 'Supply Cargo Hauler', capacity: 12, status: 'AVAILABLE', fuelAvg: '75%' },
  { id: 4, vehicle_code: 'FLEET-HELO-04', vehicle_type: 'Air Recon Helo', capacity: 4, status: 'AVAILABLE', fuelAvg: '94%' },
];

const DEFAULT_SUPPLIES = [
  { id: 1, resource_name: 'Bottled Water Pallets', resource_type: 'WATER', quantity: 2400, total_quantity: 3000, status: 'AVAILABLE', location: 'Depot Alpha' },
  { id: 2, resource_name: 'Trauma Medical Kits', resource_type: 'MEDICAL_KIT', quantity: 380, total_quantity: 500, status: 'AVAILABLE', location: 'Fieldhouse Clinic' },
  { id: 3, resource_name: 'MRE Ration Packs', resource_type: 'FOOD', quantity: 5100, total_quantity: 6000, status: 'AVAILABLE', location: 'Civic Center Hub' },
];

export const Resources: React.FC = () => {
  const [fleet, setFleet] = useState<any[]>(DEFAULT_FLEETS);
  const [supplies, setSupplies] = useState<any[]>(DEFAULT_SUPPLIES);
  const [loading, setLoading] = useState<boolean>(true);
  const [dispatchingId, setDispatchingId] = useState<number | null>(null);
  const [dispatchNotice, setDispatchNotice] = useState<string | null>(null);

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      const [fleetData, supplyData] = await Promise.all([
        resourceService.getFleet(),
        resourceService.getSupplies(),
      ]);
      if (fleetData && fleetData.length > 0) {
        setFleet(fleetData.map((v: VehicleItem) => ({
          id: v.id,
          vehicle_code: v.vehicle_code,
          vehicle_type: v.vehicle_type,
          capacity: v.capacity,
          status: v.status,
          fuelAvg: `${75 + (v.id * 3 % 20)}%`,
        })));
      }
      if (supplyData && supplyData.length > 0) {
        setSupplies(supplyData);
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  const handleDispatch = async (vehicleId: number, code: string) => {
    setDispatchingId(vehicleId);
    try {
      await resourceService.dispatch(vehicleId, 'Sector North Ridge');
      setFleet(prev => prev.map(v => v.id === vehicleId ? { ...v, status: 'DEPLOYED' } : v));
      setDispatchNotice(`Dispatched ${code} to Sector North Ridge`);
    } catch {
      setFleet(prev => prev.map(v => v.id === vehicleId ? { ...v, status: 'DEPLOYED' } : v));
      setDispatchNotice(`Simulated local dispatch: ${code}`);
    } finally {
      setDispatchingId(null);
      setTimeout(() => setDispatchNotice(null), 4000);
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide">
              RESOURCE ALLOCATION & FLEET LOGISTICS
            </h1>
            <StatusBadge status="simulated" label="SYNTHETIC ASSETS" />
            {loading && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
          </div>
          <p className="text-xs text-slate-400">
            Automated fleet dispatch, medical payload positioning, and supply chain telemetry.
          </p>
        </div>
      </div>

      {dispatchNotice && (
        <div className="bg-emerald-950 border border-emerald-500/60 text-emerald-200 px-4 py-2.5 rounded-lg text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{dispatchNotice}</span>
        </div>
      )}

      {/* Fleet Table */}
      <div className="bg-[#0d131f] border border-slate-800 rounded-lg overflow-hidden text-xs">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Truck className="w-4 h-4 text-cyan-400" />
            <span>Simulated Fleet Readiness Matrix ({fleet.length} Units)</span>
          </div>
          <span className="text-slate-500">Real-Time Dispatch Engine</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 text-slate-400 border-b border-slate-800 text-[11px]">
                <th className="p-3">Vehicle Code</th>
                <th className="p-3">Classification</th>
                <th className="p-3">Capacity</th>
                <th className="p-3">Fuel Status</th>
                <th className="p-3">State</th>
                <th className="p-3 text-right">Quick Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {fleet.map((f) => (
                <tr key={f.id} className="hover:bg-slate-900/40">
                  <td className="p-3 font-bold text-cyan-400">{f.vehicle_code}</td>
                  <td className="p-3 text-white">{f.vehicle_type}</td>
                  <td className="p-3 text-slate-300">{f.capacity} Pax/Payload</td>
                  <td className="p-3 text-slate-300">{f.fuelAvg}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        f.status === 'AVAILABLE'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}
                    >
                      {f.status}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => handleDispatch(f.id, f.vehicle_code)}
                      disabled={f.status === 'DEPLOYED' || dispatchingId === f.id}
                      className="px-2.5 py-1 rounded bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-200 text-xs disabled:opacity-40 transition-colors inline-flex items-center gap-1"
                    >
                      {dispatchingId === f.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                      <span>{f.status === 'DEPLOYED' ? 'Deployed' : 'Dispatch'}</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Supplies Grid */}
      <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-4">
        <div className="flex items-center gap-2 text-white font-semibold text-xs">
          <Package className="w-4 h-4 text-emerald-400" />
          <span>Vital Supply Reserves & Strategic Warehouses</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {supplies.map((s) => (
            <div key={s.id} className="bg-slate-900/70 border border-slate-800 p-3.5 rounded-lg space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-[11px] text-cyan-400 font-bold">{s.resource_name}</span>
                <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-300">{s.status}</span>
              </div>
              <div className="text-xl font-bold text-white">
                {s.quantity.toLocaleString()} <span className="text-xs font-normal text-slate-400">/ {s.total_quantity}</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full"
                  style={{ width: `${Math.min(100, Math.round((s.quantity / Math.max(1, s.total_quantity)) * 100))}%` }}
                />
              </div>
              <div className="text-[10px] text-slate-500">Storage Location: {s.location}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
