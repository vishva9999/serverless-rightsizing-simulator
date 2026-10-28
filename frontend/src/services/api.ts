import axios from 'axios';
import { User } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Simulation-Client': 'CommandCenter-v1',
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('disaster_command_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle unauthenticated responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if expired or invalid
      if (localStorage.getItem('disaster_command_token')) {
        localStorage.removeItem('disaster_command_token');
        localStorage.removeItem('disaster_command_user');
      }
    }
    return Promise.reject(error);
  }
);

export interface LoginResponseData {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    username: string;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
    created_at: string;
  };
}

export const authService = {
  login: async (username_or_email: string, password: string): Promise<LoginResponseData> => {
    const response = await apiClient.post<LoginResponseData>('/api/v1/auth/login', {
      username_or_email,
      password,
    });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<{ access_token: string; expires_in: number }> => {
    const response = await apiClient.post<{ access_token: string; expires_in: number }>('/api/v1/auth/refresh');
    return response.data;
  },
};

export interface SimulationOutputData {
  risk_score: number;
  risk_level: string;
  affected_population: number;
  population_at_risk: number;
  road_accessibility: number;
  estimated_damage_level: string;
  evacuation_priority: string;
  estimated_evacuation_time: number;
  resource_shortage_count: number;
  shelter_utilization: number;
  zone_impacts: Array<{
    zone_id: number;
    zone_name: string;
    risk_score: number;
    risk_level: string;
    affected_population: number;
    evacuation_priority: string;
    road_accessibility_percent: number;
  }>;
  is_simulated: boolean;
  disclaimer: string;
}

export interface SimulationRunResponse {
  scenario_id: number;
  scenario_name: string;
  disaster_type: string;
  status: string;
  result: {
    id: number;
    scenario_id: number;
    average_risk_score: number;
    affected_population: number;
    population_at_risk: number;
    estimated_evacuation_time: number;
    shelter_utilization: number;
  };
  outputs: SimulationOutputData;
  is_simulated: boolean;
  disclaimer: string;
}

export interface SimulationScenarioItem {
  id: number;
  name: string;
  disaster_type: string;
  description?: string;
  random_seed?: number;
  parameters_json: Record<string, any>;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export const simulationService = {
  getScenarios: async (): Promise<SimulationScenarioItem[]> => {
    const response = await apiClient.get<SimulationScenarioItem[]>('/api/v1/simulation/scenarios');
    return response.data;
  },

  getScenario: async (id: number): Promise<SimulationScenarioItem> => {
    const response = await apiClient.get<SimulationScenarioItem>(`/api/v1/simulation/scenarios/${id}`);
    return response.data;
  },

  createScenario: async (data: any): Promise<SimulationScenarioItem> => {
    const response = await apiClient.post<SimulationScenarioItem>('/api/v1/simulation/scenarios', data);
    return response.data;
  },

  runScenario: async (id: number): Promise<SimulationRunResponse> => {
    const response = await apiClient.post<SimulationRunResponse>(`/api/v1/simulation/scenarios/${id}/run`);
    return response.data;
  },

  getResults: async (id: number): Promise<any[]> => {
    const response = await apiClient.get<any[]>(`/api/v1/simulation/scenarios/${id}/results`);
    return response.data;
  },
};

export interface ShelterItem {
  id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  total_capacity: number;
  current_occupancy: number;
  accessibility: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const shelterService = {
  getShelters: async (): Promise<ShelterItem[]> => {
    const response = await apiClient.get<ShelterItem[]>('/api/v1/shelters');
    return response.data;
  },
  toggleIntake: async (id: number): Promise<ShelterItem> => {
    const response = await apiClient.post<ShelterItem>(`/api/v1/shelters/${id}/toggle-intake`);
    return response.data;
  },
};

export interface ZoneItem {
  id: number;
  disaster_event_id: number;
  zone_code: string;
  zone_name: string;
  latitude: number;
  longitude: number;
  population: number;
  population_density: number;
  building_density: number;
  risk_score: number;
  risk_level: string;
  road_accessibility: number;
  evacuation_priority: string;
  status: string;
}

export const zoneService = {
  getZones: async (): Promise<ZoneItem[]> => {
    const response = await apiClient.get<ZoneItem[]>('/api/v1/zones');
    return response.data;
  },
  triggerHazardPulse: async (id: number, riskDelta: number = 10.0): Promise<ZoneItem> => {
    const response = await apiClient.post<ZoneItem>(`/api/v1/zones/${id}/pulse?risk_delta=${riskDelta}`);
    return response.data;
  },
};

export interface EvacuationRouteItem {
  id: number;
  disaster_event_id: number;
  source_zone_id: number;
  destination_shelter_id: number;
  distance_km: number;
  estimated_time_minutes: number;
  safety_score: number;
  risk_score: number;
  congestion_score: number;
  route_status: string;
}

export const evacuationService = {
  getRoutes: async (): Promise<EvacuationRouteItem[]> => {
    const response = await apiClient.get<EvacuationRouteItem[]>('/api/v1/evacuation/routes');
    return response.data;
  },
  toggleContraflow: async (id: number): Promise<EvacuationRouteItem> => {
    const response = await apiClient.post<EvacuationRouteItem>(`/api/v1/evacuation/routes/${id}/contraflow`);
    return response.data;
  },
  updateStatus: async (id: number, newStatus: string): Promise<EvacuationRouteItem> => {
    const response = await apiClient.patch<EvacuationRouteItem>(`/api/v1/evacuation/routes/${id}/status?new_status=${newStatus}`);
    return response.data;
  },
};

export interface VehicleItem {
  id: number;
  vehicle_code: string;
  vehicle_type: string;
  capacity: number;
  current_latitude: number;
  current_longitude: number;
  status: string;
}

export interface SupplyItem {
  id: number;
  resource_id: number;
  resource_name: string;
  resource_type: string;
  quantity: number;
  total_quantity: number;
  status: string;
  location: string;
}

export const resourceService = {
  getFleet: async (): Promise<VehicleItem[]> => {
    const response = await apiClient.get<VehicleItem[]>('/api/v1/resources/fleet');
    return response.data;
  },
  getSupplies: async (): Promise<SupplyItem[]> => {
    const response = await apiClient.get<SupplyItem[]>('/api/v1/resources/supplies');
    return response.data;
  },
  dispatch: async (vehicleId: number, destination: string): Promise<any> => {
    const response = await apiClient.post(`/api/v1/resources/dispatch?vehicle_id=${vehicleId}&destination=${destination}`);
    return response.data;
  },
};

export interface AuditLogItem {
  id: number;
  user_id?: number;
  action: string;
  entity_type: string;
  entity_id?: string;
  previous_value?: Record<string, any>;
  new_value?: Record<string, any>;
  ip_address?: string;
  created_at: string;
}

export const auditLogService = {
  getLogs: async (limit: number = 50): Promise<AuditLogItem[]> => {
    const response = await apiClient.get<AuditLogItem[]>(`/api/v1/audit-logs?limit=${limit}`);
    return response.data;
  },
  recordLog: async (data: any): Promise<AuditLogItem> => {
    const response = await apiClient.post<AuditLogItem>('/api/v1/audit-logs', data);
    return response.data;
  },
};

export const analyticsService = {
  getSummary: async (): Promise<any> => {
    const response = await apiClient.get('/api/v1/analytics/summary');
    return response.data;
  },
};


