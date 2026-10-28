import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const SIMULATED_HOURLY_DATA = [
  { time: '08:00', evacuees: 420, capacity: 1200, congestion: 18 },
  { time: '09:00', evacuees: 850, capacity: 1200, congestion: 32 },
  { time: '10:00', evacuees: 1640, capacity: 1800, congestion: 58 },
  { time: '11:00', evacuees: 2900, capacity: 2500, congestion: 79 },
  { time: '12:00', evacuees: 3820, capacity: 3200, congestion: 88 },
  { time: '13:00', evacuees: 4600, capacity: 4000, congestion: 72 },
  { time: '14:00', evacuees: 5120, capacity: 4800, congestion: 64 },
];

export const TelemetryCharts: React.FC = () => {
  return (
    <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
            Evacuation Flow & Intake Velocity
          </h3>
          <span className="text-[10px] font-mono text-cyan-400">
            Synthetic Scenario Time-Series
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span className="text-slate-300">Evacuees Processed</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span className="text-slate-300">Shelter Intake</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={SIMULATED_HOURLY_DATA}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorEvac" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorShelter" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="time"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              fontFamily="monospace"
            />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              fontFamily="monospace"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090e17',
                borderColor: '#334155',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
              }}
              itemStyle={{ color: '#e2e8f0' }}
            />
            <Area
              type="monotone"
              dataKey="evacuees"
              stroke="#06b6d4"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorEvac)"
            />
            <Area
              type="monotone"
              dataKey="capacity"
              stroke="#10b981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorShelter)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
