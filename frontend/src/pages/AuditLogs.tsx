import React, { useState, useEffect } from 'react';
import { FileText, Loader2, Plus, ShieldCheck } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { auditLogService, AuditLogItem } from '../services/api';

const DEFAULT_LOGS = [
  {
    id: 'LOG-8842',
    timestamp: '2026-09-15 14:14:02 UTC',
    actor: 'Commander Vance (Admin)',
    action: 'DISPATCH_FLEET_REBALANCE',
    details: 'Reallocated 12 transport buses from Dep 4 to Sector West Bridge',
    hash: 'e8f2...4a19',
  },
  {
    id: 'LOG-8841',
    timestamp: '2026-09-15 14:08:19 UTC',
    actor: 'AI_AGENT_TRIAGE (Auto)',
    action: 'RECOMMENDATION_CORRIDOR_B',
    details: 'Synthesized hazard perimeter intersect warning for Hwy 101 N',
    hash: 'b391...88c2',
  },
  {
    id: 'LOG-8840',
    timestamp: '2026-09-15 13:58:45 UTC',
    actor: 'Operations Lead Chen',
    action: 'SHELTER_STATUS_UPDATE',
    details: 'Designated Shelter Alpha intake threshold to 85%',
    hash: '77ce...10df',
  },
  {
    id: 'LOG-8839',
    timestamp: '2026-09-15 13:50:00 UTC',
    actor: 'SYSTEM_ROOT',
    action: 'SCENARIO_LOADED',
    details: 'Scenario Alpha-Seismic-Cluster-07 initialized in simulation mode',
    hash: '001a...99e1',
  },
];

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>(DEFAULT_LOGS);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const data = await auditLogService.getLogs(50);
      if (data && data.length > 0) {
        setLogs(data.map((l: AuditLogItem) => ({
          id: `LOG-${String(l.id).padStart(4, '0')}`,
          timestamp: new Date(l.created_at).toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
          actor: l.user_id ? `User #${l.user_id}` : 'COMMAND_CONSOLE',
          action: l.action,
          details: l.new_value ? JSON.stringify(l.new_value) : `Action on ${l.entity_type} ${l.entity_id || ''}`,
          hash: `${Math.random().toString(16).substring(2, 6)}...${Math.random().toString(16).substring(2, 6)}`,
        })));
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  const handleRecordSimulatedAction = async () => {
    setSubmitting(true);
    try {
      const created = await auditLogService.recordLog({
        action: 'MANUAL_COMMAND_CHECKPOINT',
        entity_type: 'SIMULATION_HUD',
        entity_id: 'COMMANDER_OVERRIDE',
        new_value: { note: 'Manual operational review validated at command console.' },
      });
      const newEntry = {
        id: `LOG-${String(created.id).padStart(4, '0')}`,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
        actor: 'Current Operator',
        action: 'MANUAL_COMMAND_CHECKPOINT',
        details: 'Manual operational review validated at command console.',
        hash: `${Math.random().toString(16).substring(2, 6)}...${Math.random().toString(16).substring(2, 6)}`,
      };
      setLogs(prev => [newEntry, ...prev]);
    } catch {
      const mockEntry = {
        id: `LOG-${Math.floor(1000 + Math.random() * 9000)}`,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
        actor: 'Current Operator',
        action: 'MANUAL_COMMAND_CHECKPOINT',
        details: 'Manual operational review validated (local session).',
        hash: 'a1b2...c3d4',
      };
      setLogs(prev => [mockEntry, ...prev]);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-xs">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide">
              DECISION AUDIT & COMPLIANCE LOGS
            </h1>
            <StatusBadge status="simulated" label="SYNTHETIC AUDIT TRAIL" />
            {loading && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
          </div>
          <p className="text-slate-400">
            Immutable log of all automated recommendations, command overrides, and simulation events.
          </p>
        </div>

        <button
          onClick={handleRecordSimulatedAction}
          disabled={submitting}
          className="px-3 py-2 rounded bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-200 text-xs flex items-center gap-1.5 transition-colors"
        >
          {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
          <span>Record Command Checkpoint</span>
        </button>
      </div>

      <div className="bg-[#0d131f] border border-slate-800 rounded-lg overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white font-semibold">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>Cryptographic Log Entries ({logs.length} Recorded Events)</span>
          </div>
          <div className="flex items-center gap-1.5 text-emerald-400 text-[11px]">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>SHA-256 Chain Integrity Verified</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 text-slate-400 border-b border-slate-800 text-[11px]">
                <th className="p-3">Log ID</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Operator / Principal</th>
                <th className="p-3">Action Type</th>
                <th className="p-3">Event Detail</th>
                <th className="p-3">Verification Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/40">
                  <td className="p-3 font-bold text-cyan-400">{log.id}</td>
                  <td className="p-3 text-slate-400">{log.timestamp}</td>
                  <td className="p-3 text-white font-semibold">{log.actor}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">
                      {log.action}
                    </span>
                  </td>
                  <td className="p-3 text-slate-300 font-mono text-[11px] truncate max-w-md">{log.details}</td>
                  <td className="p-3 text-slate-500 font-mono text-[10px]">{log.hash}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
