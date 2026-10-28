import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Simulation } from '../pages/Simulation';
import { simulationService } from '../services/api';

vi.mock('../services/api', () => ({
  simulationService: {
    getScenarios: vi.fn(),
    getScenario: vi.fn(),
    createScenario: vi.fn(),
    runScenario: vi.fn(),
    getResults: vi.fn(),
  },
  authService: {
    login: vi.fn(),
    getMe: vi.fn(),
  },
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockSimulationService = simulationService as {
  getScenarios: ReturnType<typeof vi.fn>;
  getScenario: ReturnType<typeof vi.fn>;
  createScenario: ReturnType<typeof vi.fn>;
  runScenario: ReturnType<typeof vi.fn>;
  getResults: ReturnType<typeof vi.fn>;
};

const fakeDemoScenario = {
  id: 1,
  name: 'Coimbatore Flood Simulation - DEMO',
  disaster_type: 'FLOOD',
  description: 'Noyyal river basin flood drill',
  random_seed: 42,
  parameters_json: { rainfall: 210, water_level: 4.8 },
  status: 'COMPLETED',
  created_by: 1,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const fakeOutputs = {
  risk_score: 72.5,
  risk_level: 'HIGH',
  affected_population: 14800,
  population_at_risk: 19200,
  road_accessibility: 58.0,
  estimated_damage_level: 'SEVERE',
  evacuation_priority: 'HIGH',
  estimated_evacuation_time: 3.8,
  resource_shortage_count: 3,
  shelter_utilization: 65.4,
  zone_impacts: [
    {
      zone_id: 1,
      zone_name: 'Zone 1 - Gandhipuram Central',
      risk_score: 68.2,
      risk_level: 'HIGH',
      affected_population: 3200,
      evacuation_priority: 'HIGH',
      road_accessibility_percent: 62.0,
    },
  ],
  is_simulated: true,
  disclaimer: 'SYNTHETIC SIMULATION DATA ONLY.',
};

describe('Phase 4 — Disaster Simulation Frontend', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockSimulationService.getScenarios.mockResolvedValue([fakeDemoScenario]);
    mockSimulationService.getResults.mockResolvedValue([
      { id: 10, scenario_id: 1, result_json: fakeOutputs },
    ]);
  });

  it('renders simulation engine page and parameter controls', async () => {
    render(
      <MemoryRouter>
        <Simulation />
      </MemoryRouter>
    );

    expect(screen.getByText(/DISASTER SCENARIO SIMULATION ENGINE/i)).toBeInTheDocument();
    expect(screen.getByText(/Select Disaster Vector/i)).toBeInTheDocument();
    expect(document.getElementById('run-simulation-btn')).toBeInTheDocument();
    expect(document.getElementById('param-rainfall')).toBeInTheDocument();
    expect(document.getElementById('param-water-level')).toBeInTheDocument();
    expect(document.getElementById('param-wind-speed')).toBeInTheDocument();
  });

  it('allows disaster type selection', async () => {
    render(
      <MemoryRouter>
        <Simulation />
      </MemoryRouter>
    );

    const cycloneBtn = document.getElementById('disaster-type-cyclone');
    expect(cycloneBtn).toBeInTheDocument();
    fireEvent.click(cycloneBtn!);
    expect(screen.getByText('Cyclone / Storm')).toBeInTheDocument();
  });

  it('runs simulation and updates output KPI metrics and zone table', async () => {
    mockSimulationService.runScenario.mockResolvedValue({
      scenario_id: 1,
      scenario_name: 'Coimbatore Flood Simulation - DEMO',
      disaster_type: 'FLOOD',
      status: 'COMPLETED',
      result: { id: 1, average_risk_score: 72.5 },
      outputs: fakeOutputs,
      is_simulated: true,
      disclaimer: 'SYNTHETIC SIMULATION DATA ONLY.',
    });

    render(
      <MemoryRouter>
        <Simulation />
      </MemoryRouter>
    );

    const runBtn = document.getElementById('run-simulation-btn')!;
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(screen.getByText('72.5')).toBeInTheDocument();
      expect(screen.getByText('14,800')).toBeInTheDocument();
      expect(screen.getByText('58%')).toBeInTheDocument();
      expect(screen.getByText(/Gandhipuram Central/i)).toBeInTheDocument();
    });
  });
});
