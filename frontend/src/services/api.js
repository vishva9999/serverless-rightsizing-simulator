/**
 * API service — wraps Axios calls to the FastAPI backend.
 * Phase 1: /health, /api/info, /api/metrics/summary.
 * Phase 2: POST /api/simulate for Rightsizing Simulation Engine.
 * Phase 3: /api/scenarios CRUD + /api/history tracking & run comparison.
 * Phase 4: /api/storage/status.
 * Phase 5: /api/sensitivity/variables + POST /api/sensitivity/analyze.
 * Phase 6: /api/auth/*, /api/organizations/*, /api/users/* with Bearer JWT interceptor.
 */

import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor: Attach JWT Bearer Token if logged in
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Response Interceptor: Handle 401 Globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and trigger auth state reset if 401 received
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.dispatchEvent(new Event('auth:unauthorized'))
      }
    }
    return Promise.reject(error)
  }
)

// ── Authentication (Phase 6) ─────────────────────────────────────────────────
export const loginUser = async (credentials) => {
  const response = await apiClient.post('/api/auth/login', credentials)
  return response.data
}

export const registerUser = async (registrationData) => {
  const response = await apiClient.post('/api/auth/register', registrationData)
  return response.data
}

export const fetchCurrentUser = async () => {
  const response = await apiClient.get('/api/auth/me')
  return response.data
}

// ── Organizations (Phase 6) ──────────────────────────────────────────────────
export const fetchOrganization = async () => {
  const response = await apiClient.get('/api/organizations/me')
  return response.data
}

export const updateOrganization = async (orgData) => {
  const response = await apiClient.put('/api/organizations/me', orgData)
  return response.data
}

// ── User Management (Phase 6) ────────────────────────────────────────────────
export const fetchUsers = async () => {
  const response = await apiClient.get('/api/users')
  return response.data
}

export const fetchUserById = async (userId) => {
  const response = await apiClient.get(`/api/users/${userId}`)
  return response.data
}

export const createUserInOrg = async (userData) => {
  const response = await apiClient.post('/api/users', userData)
  return response.data
}

export const updateUserRole = async (userId, role) => {
  const response = await apiClient.put(`/api/users/${userId}/role`, { role })
  return response.data
}

export const updateUserStatus = async (userId, isActive) => {
  const response = await apiClient.put(`/api/users/${userId}/status`, { is_active: isActive })
  return response.data
}

// ── Health & Info (Phase 1) ──────────────────────────────────────────────────
export const fetchHealth = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

export const fetchInfo = async () => {
  const response = await apiClient.get('/api/info')
  return response.data
}

export const fetchMetricsSummary = async () => {
  const response = await apiClient.get('/api/metrics/summary')
  return response.data
}

// ── Storage Status (Phase 4) ─────────────────────────────────────────────────
export const fetchStorageStatus = async () => {
  const response = await apiClient.get('/api/storage/status')
  return response.data
}

// ── Rightsizing Simulation (Phase 2) ──────────────────────────────────────────
export const runSimulation = async (simulationRequestData) => {
  const response = await apiClient.post('/api/simulate', simulationRequestData)
  return response.data
}

// ── Scenario Management (Phase 3 & 6) ────────────────────────────────────────
export const fetchScenarios = async () => {
  const response = await apiClient.get('/api/scenarios')
  return response.data
}

export const fetchScenarioById = async (id) => {
  const response = await apiClient.get(`/api/scenarios/${id}`)
  return response.data
}

export const createScenario = async (scenarioData) => {
  const response = await apiClient.post('/api/scenarios', scenarioData)
  return response.data
}

export const updateScenario = async (id, scenarioData) => {
  const response = await apiClient.put(`/api/scenarios/${id}`, scenarioData)
  return response.data
}

export const deleteScenario = async (id) => {
  const response = await apiClient.delete(`/api/scenarios/${id}`)
  return response.data
}

export const simulateScenario = async (id) => {
  const response = await apiClient.post(`/api/scenarios/${id}/simulate`)
  return response.data
}

// ── Simulation History (Phase 3 & 6) ─────────────────────────────────────────
export const fetchHistory = async (scenarioId = null) => {
  const url = scenarioId ? `/api/history?scenario_id=${scenarioId}` : '/api/history'
  const response = await apiClient.get(url)
  return response.data
}

export const fetchHistoryById = async (id) => {
  const response = await apiClient.get(`/api/history/${id}`)
  return response.data
}

export const deleteHistoryItem = async (id) => {
  const response = await apiClient.delete(`/api/history/${id}`)
  return response.data
}

export const compareHistoryRuns = async (id1, id2) => {
  const response = await apiClient.get(`/api/history/compare/${id1}/${id2}`)
  return response.data
}

// ── Sensitivity Analysis (Phase 5 & 6) ───────────────────────────────────────
export const fetchSensitivityVariables = async () => {
  const response = await apiClient.get('/api/sensitivity/variables')
  return response.data
}

export const runSensitivityAnalysis = async (payload) => {
  const response = await apiClient.post('/api/sensitivity/analyze', payload)
  return response.data
}

export default apiClient
