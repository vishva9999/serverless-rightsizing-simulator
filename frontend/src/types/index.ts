export * from './health';

export type Role =
  | 'ADMIN'
  | 'DISASTER_OPERATOR'
  | 'FIELD_OFFICER'
  | 'SHELTER_MANAGER'
  | 'RESOURCE_MANAGER'
  | 'VIEWER'
  | 'Incident Commander'
  | 'Logistics Coordinator'
  | 'Field Dispatcher'
  | 'Simulation Analyst';

export interface User {
  id: string | number;
  username: string;
  email: string;
  full_name: string;
  name?: string;
  callsign?: string;
  role: Role;
  token?: string;
  is_active?: boolean;
}

export interface MetricSummary {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  status: 'critical' | 'warning' | 'nominal' | 'info';
  subtext: string;
}

export interface DisasterIncident {
  id: string;
  type: 'EARTHQUAKE' | 'FLOOD' | 'WILDFIRE' | 'HAZMAT' | 'HURRICANE';
  severity: 1 | 2 | 3 | 4 | 5;
  location: string;
  coordinates: [number, number];
  affectedPopulation: number;
  evacuationStatus: 'ORDERED' | 'WARNING' | 'COMPLETED' | 'STANDBY';
  timestamp: string;
  isSimulated: true;
}

export interface ShelterUnit {
  id: string;
  name: string;
  coordinates: [number, number];
  capacityTotal: number;
  capacityOccupied: number;
  status: 'OPEN' | 'NEAR_CAPACITY' | 'FULL' | 'EVACUATED';
  medicalStaffPresent: boolean;
  waterSupplyDays: number;
  powerStatus: 'GRID' | 'GENERATOR' | 'BATTERY_CRITICAL';
}

export interface TelemetryFeedItem {
  id: string;
  timestamp: string;
  source: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  message: string;
  sector: string;
}
