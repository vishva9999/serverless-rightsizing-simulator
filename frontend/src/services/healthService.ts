import { apiClient } from './api';
import { HealthResponse, VersionResponse } from '../types/health';

export const healthService = {
  async getHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  },

  async getVersion(): Promise<VersionResponse> {
    const response = await apiClient.get<VersionResponse>('/api/version');
    return response.data;
  },
};
