export interface DatabaseHealth {
  connected: boolean;
  engine: string;
  is_fallback: boolean;
  message: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'offline';
  app_name: string;
  environment: string;
  timestamp: string;
  uptime_seconds: number;
  database: DatabaseHealth;
  is_simulated: boolean;
  emergency_services_integrated: boolean;
  simulation_disclaimer: string;
}

export interface VersionResponse {
  app_name: string;
  version: string;
  api_version: string;
  environment: string;
  is_simulated: boolean;
  build_target: string;
}
