import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Play,
  RotateCcw,
  Sliders,
  AlertTriangle,
  Flame,
  Wind,
  Droplets,
  Activity,
  Mountain,
  Users,
  Route,
  Clock,
  ShieldCheck,
  AlertCircle,
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { simulationService, SimulationScenarioItem, SimulationOutputData } from '../services/api';

const DISASTER_TYPES = [
  { id: 'FLOOD', name: 'Flood Hazard', icon: Droplets, color: 'text-cyan-400' },
  { id: 'CYCLONE', name: 'Cyclone / Storm', icon: Wind, color: 'text-teal-400' },
  { id: 'EARTHQUAKE', name: 'Earthquake', icon: Activity, color: 'text-amber-400' },
  { id: 'URBAN_FIRE', name: 'Urban Wildfire', icon: Flame, color: 'text-red-400' },
  { id: 'LANDSLIDE', name: 'Landslide', icon: Mountain, color: 'text-orange-400' },
];

export const Simulation: React.FC = () => {
  const [scenarios, setScenarios] = useState<SimulationScenarioItem[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | null>(null);
  const [disasterType, setDisasterType] = useState<string>('FLOOD');
  const [rainfall, setRainfall] = useState<number>(210);
  const [waterLevel, setWaterLevel] = useState<number>(4.8);
  const [windSpeed, setWindSpeed] = useState<number>(45);
  const [earthquakeIntensity, setEarthquakeIntensity] = useState<number>(0.0);
  const [temperature, setTemperature] = useState<number>(28);
  const [roadCondition, setRoadCondition] = useState<number>(0.7);
  const [populationDensity, setPopulationDensity] = useState<number>(3200);
  const [randomSeed, setRandomSeed] = useState<number>(42);

  const [loading, setLoading] = useState<boolean>(false);
  const [running, setRunning] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [outputData, setOutputData] = useState<SimulationOutputData | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const list = await simulationService.getScenarios();
      setScenarios(list);
      if (list.length > 0) {
        const demo = list.find((s) => s.name.includes('DEMO')) || list[0];
        setSelectedScenarioId(demo.id);
        // Load initial results for demo if available
        try {
          const results = await simulationService.getResults(demo.id);
          if (results.length > 0 && results[0].result_json) {
            setOutputData(results[0].result_json);
          }
        } catch {
          // initial results load non-fatal
        }
      }
    } catch (err: any) {
      setErrorMessage('Could not load simulation scenarios: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    setRunning(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      // 1. If scenario exists, update it or create a new test scenario
      let targetId = selectedScenarioId;
      if (!targetId) {
        const created = await simulationService.createScenario({
          name: `Sim-${disasterType}-${Date.now().toString().slice(-4)}`,
          disaster_type: disasterType,
          description: `Custom ${disasterType} simulation run with seed ${randomSeed}`,
          random_seed: randomSeed,
          parameters: {
            disaster_type: disasterType,
            rainfall,
            water_level: waterLevel,
            wind_speed: windSpeed,
            earthquake_intensity: earthquakeIntensity,
            temperature,
            road_condition: roadCondition,
            population_density: populationDensity,
            building_density: 900,
            historical_risk: 0.65,
            time_of_day: 'day',
            random_seed: randomSeed,
          },
        });
        targetId = created.id;
        setSelectedScenarioId(created.id);
        await loadScenarios();
      }

      // 2. Execute run
      const runRes = await simulationService.runScenario(targetId);
      setOutputData(runRes.outputs);
      setSuccessMessage(`Simulation #${targetId} completed. Output computed deterministically.`);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Simulation execution failed: ' + err.message);
    } finally {
      setRunning(false);
    }
  };

  const handleResetDefaults = () => {
    setRainfall(210);
    setWaterLevel(4.8);
    setWindSpeed(45);
    setEarthquakeIntensity(0);
    setTemperature(28);
    setRoadCondition(0.7);
    setPopulationDensity(3200);
    setRandomSeed(42);
  };

  return (
    <div className="space-y-6 font-mono text-slate-200">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              DISASTER SCENARIO SIMULATION ENGINE
            </h1>
            <StatusBadge status="simulated" label="SYNTHETIC PHYSICS & AGENTS" />
          </div>
          <p className="text-xs text-slate-400">
            Deterministic computational model for multi-hazard perimeter progression, population impact, and evacuation urgency.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            id="run-simulation-btn"
            onClick={handleRunSimulation}
            disabled={running || loading}
            className="px-4 py-2 rounded text-xs flex items-center gap-2 font-bold bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 transition-all shadow-glow-cyan"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                <span>COMPUTING MODEL...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 text-slate-950 fill-current" />
                <span>RUN SIMULATION</span>
              </>
            )}
          </button>

          <button
            onClick={handleResetDefaults}
            disabled={running}
            className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Reset Default Parameters"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      {errorMessage && (
        <div className="p-3 rounded bg-red-950/70 border border-red-800 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
      {successMessage && (
        <div className="p-3 rounded bg-emerald-950/70 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Top Disclaimer Banner */}
      <div className="p-3 rounded bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        <span>
          <strong>DISCLAIMER:</strong> All hazard footprints, casualty projections, and zone evaluations are synthetically simulated for training & software evaluation. No real 911 or emergency response integration.
        </span>
      </div>

      {/* Main Grid: Parameters on Left, Results on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Parameter Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Disaster Type Selector */}
          <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3">
            <label className="text-xs uppercase font-bold text-slate-300 tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span>Select Disaster Vector</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {DISASTER_TYPES.map((dt) => {
                const Icon = dt.icon;
                const isSelected = disasterType === dt.id;
                return (
                  <button
                    key={dt.id}
                    id={`disaster-type-${dt.id.toLowerCase()}`}
                    type="button"
                    onClick={() => setDisasterType(dt.id)}
                    className={`p-2.5 rounded border text-left flex flex-col gap-1 transition-all ${
                      isSelected
                        ? 'bg-cyan-950/80 border-cyan-500 text-white shadow-sm'
                        : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${dt.color}`} />
                    <span className="text-[11px] font-bold">{dt.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Scenario Selection */}
          <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-bold uppercase">Preloaded Scenario</span>
              <span className="text-slate-500 text-[10px]">{scenarios.length} available</span>
            </div>
            <select
              value={selectedScenarioId || ''}
              onChange={(e) => setSelectedScenarioId(Number(e.target.value) || null)}
              className="w-full bg-[#080c14] border border-slate-700 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="">-- Custom Simulation Run --</option>
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>
                  #{s.id} - {s.name} ({s.disaster_type})
                </option>
              ))}
            </select>
          </div>

          {/* Hazard Environmental Sliders */}
          <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4 space-y-3.5 text-xs">
            <div className="text-slate-300 font-bold uppercase pb-2 border-b border-slate-800 flex justify-between items-center">
              <span>Hazard Physical Inputs</span>
              <span className="text-[10px] text-cyan-400 font-normal">Seed: #{randomSeed}</span>
            </div>

            {/* Rainfall */}
            <div>
              <div className="flex justify-between text-slate-400 mb-1">
                <span>Rainfall Volume</span>
                <span className="text-cyan-400 font-bold">{rainfall} mm</span>
              </div>
              <input
                id="param-rainfall"
                type="range"
                min="0"
                max="500"
                step="5"
                value={rainfall}
                onChange={(e) => setRainfall(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 bg-slate-800"
              />
            </div>

            {/* Water Level */}
            <div>
              <div className="flex justify-between text-slate-400 mb-1">
                <span>River / Water Surge Level</span>
                <span className="text-cyan-400 font-bold">{waterLevel} m</span>
              </div>
              <input
                id="param-water-level"
                type="range"
                min="0"
                max="15"
                step="0.2"
                value={waterLevel}
                onChange={(e) => setWaterLevel(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 bg-slate-800"
              />
            </div>

            {/* Wind Speed */}
            <div>
              <div className="flex justify-between text-slate-400 mb-1">
                <span>Wind Velocity</span>
                <span className="text-teal-400 font-bold">{windSpeed} km/h</span>
              </div>
              <input
                id="param-wind-speed"
                type="range"
                min="0"
                max="250"
                step="5"
                value={windSpeed}
                onChange={(e) => setWindSpeed(parseFloat(e.target.value))}
                className="w-full accent-teal-500 bg-slate-800"
              />
            </div>

            {/* Earthquake intensity (if seismic) */}
            <div>
              <div className="flex justify-between text-slate-400 mb-1">
                <span>Earthquake Intensity (Richter)</span>
                <span className="text-amber-400 font-bold">{earthquakeIntensity.toFixed(1)}</span>
              </div>
              <input
                id="param-earthquake"
                type="range"
                min="0"
                max="9.0"
                step="0.1"
                value={earthquakeIntensity}
                onChange={(e) => setEarthquakeIntensity(parseFloat(e.target.value))}
                className="w-full accent-amber-500 bg-slate-800"
              />
            </div>

            {/* Road Condition & Population */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase mb-1">Road Condition (0-1)</label>
                <input
                  type="number"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={roadCondition}
                  onChange={(e) => setRoadCondition(parseFloat(e.target.value))}
                  className="w-full bg-[#080c14] border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-400 uppercase mb-1">Pop Density / km²</label>
                <input
                  type="number"
                  min="500"
                  max="10000"
                  step="100"
                  value={populationDensity}
                  onChange={(e) => setPopulationDensity(parseInt(e.target.value))}
                  className="w-full bg-[#080c14] border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white"
                />
              </div>
            </div>

            {/* Random seed */}
            <div className="pt-1">
              <label className="block text-[10px] text-slate-400 uppercase mb-1">Deterministic Seed Value</label>
              <input
                id="param-random-seed"
                type="number"
                value={randomSeed}
                onChange={(e) => setRandomSeed(parseInt(e.target.value) || 0)}
                className="w-full bg-[#080c14] border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Simulation Output Dashboard (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {outputData ? (
            <>
              {/* Top 4 KPI Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {/* Composite Risk Score */}
                <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase">
                    <span>Risk Score</span>
                    <Activity className="w-3.5 h-3.5 text-cyan-400" />
                  </div>
                  <div className="my-1">
                    <span className="text-2xl font-bold text-white tracking-tight">
                      {outputData.risk_score}
                    </span>
                    <span className="text-xs text-slate-500"> /100</span>
                  </div>
                  <span
                    className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded text-center ${
                      outputData.risk_level === 'CRITICAL'
                        ? 'bg-red-950 border border-red-600 text-red-300'
                        : outputData.risk_level === 'HIGH'
                        ? 'bg-orange-950 border border-orange-600 text-orange-300'
                        : outputData.risk_level === 'MEDIUM'
                        ? 'bg-amber-950 border border-amber-600 text-amber-300'
                        : 'bg-emerald-950 border border-emerald-600 text-emerald-300'
                    }`}
                  >
                    {outputData.risk_level}
                  </span>
                </div>

                {/* Affected Population */}
                <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase">
                    <span>Affected Pop.</span>
                    <Users className="w-3.5 h-3.5 text-amber-400" />
                  </div>
                  <div className="my-1">
                    <span className="text-2xl font-bold text-amber-400 tracking-tight">
                      {outputData.affected_population.toLocaleString()}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400">
                    At Risk: {outputData.population_at_risk.toLocaleString()}
                  </span>
                </div>

                {/* Road Accessibility */}
                <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase">
                    <span>Road Access</span>
                    <Route className="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                  <div className="my-1">
                    <span className="text-2xl font-bold text-emerald-400 tracking-tight">
                      {outputData.road_accessibility}%
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400">
                    Damage: {outputData.estimated_damage_level}
                  </span>
                </div>

                {/* Evacuation Priority */}
                <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase">
                    <span>Evac Priority</span>
                    <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  </div>
                  <div className="my-1">
                    <span className="text-sm font-bold text-cyan-300 tracking-tight">
                      {outputData.evacuation_priority}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400">
                    ETA: ~{outputData.estimated_evacuation_time}h
                  </span>
                </div>
              </div>

              {/* Secondary Detail Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4">
                  <div className="text-slate-400 text-[10px] uppercase tracking-wider mb-1">
                    Shelter Utilization Model
                  </div>
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-lg font-bold text-white">
                      {outputData.shelter_utilization}%
                    </span>
                    <span className="text-slate-500 text-[11px]">Demand vs Municipal Cap</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full ${
                        outputData.shelter_utilization > 85 ? 'bg-red-500' : 'bg-cyan-500'
                      }`}
                      style={{ width: `${Math.min(100, outputData.shelter_utilization)}%` }}
                    />
                  </div>
                </div>

                <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-4">
                  <div className="text-slate-400 text-[10px] uppercase tracking-wider mb-1">
                    Resource Shortage Index
                  </div>
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-lg font-bold text-amber-400">
                      {outputData.resource_shortage_count} Shortages
                    </span>
                    <span className="text-slate-500 text-[11px]">Asset deficit</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-amber-500"
                      style={{ width: `${Math.min(100, outputData.resource_shortage_count * 20)}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Municipal Zone Breakdown Table */}
              <div className="bg-[#0d131f] border border-slate-800 rounded-lg overflow-hidden">
                <div className="p-3.5 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
                    <ShieldCheck className="w-4 h-4 text-cyan-400" />
                    <span>Simulated Municipal Zone Impact Matrix</span>
                  </div>
                  <span className="text-[10px] text-slate-500">6 Sectors Evaluated</span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#080d16] text-[10px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
                      <tr>
                        <th className="px-3.5 py-2.5">Sector</th>
                        <th className="px-3.5 py-2.5">Risk Score</th>
                        <th className="px-3.5 py-2.5">Level</th>
                        <th className="px-3.5 py-2.5">Affected</th>
                        <th className="px-3.5 py-2.5">Road Access</th>
                        <th className="px-3.5 py-2.5">Priority</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                      {outputData.zone_impacts.map((z) => (
                        <tr key={z.zone_id} className="hover:bg-slate-900/60 transition-colors">
                          <td className="px-3.5 py-2.5 font-medium text-slate-200">{z.zone_name}</td>
                          <td className="px-3.5 py-2.5 text-cyan-400 font-bold">{z.risk_score}</td>
                          <td className="px-3.5 py-2.5">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                                z.risk_level === 'CRITICAL'
                                  ? 'bg-red-950 text-red-300'
                                  : z.risk_level === 'HIGH'
                                  ? 'bg-orange-950 text-orange-300'
                                  : z.risk_level === 'MEDIUM'
                                  ? 'bg-amber-950 text-amber-300'
                                  : 'bg-emerald-950 text-emerald-300'
                              }`}
                            >
                              {z.risk_level}
                            </span>
                          </td>
                          <td className="px-3.5 py-2.5 text-slate-300">{z.affected_population.toLocaleString()}</td>
                          <td className="px-3.5 py-2.5 text-slate-300">{z.road_accessibility_percent}%</td>
                          <td className="px-3.5 py-2.5">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[9px] ${
                                z.evacuation_priority === 'IMMEDIATE'
                                  ? 'text-red-400 font-bold'
                                  : 'text-slate-400'
                              }`}
                            >
                              {z.evacuation_priority}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-[#0d131f] border border-slate-800 rounded-lg p-12 text-center text-slate-500 space-y-3">
              <Cpu className="w-10 h-10 mx-auto text-slate-600 animate-pulse" />
              <div className="text-sm font-bold text-slate-400">NO ACTIVE SIMULATION OUTPUT</div>
              <p className="text-xs max-w-sm mx-auto">
                Configure environmental parameters on the left and click "RUN SIMULATION" to calculate hazard propagation and zone evacuation impact.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
