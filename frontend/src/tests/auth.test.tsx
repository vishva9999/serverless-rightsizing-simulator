/**
 * Phase 3 — Authentication & RBAC Frontend Tests
 *
 * Tests cover:
 * 1. Login page renders
 * 2. Successful login flow
 * 3. Failed login — invalid credentials (401)
 * 4. Failed login — network error
 * 5. Loading state on login
 * 6. Protected route redirects unauthenticated user
 * 7. Authenticated user can access protected route
 * 8. Wrong role shows access restricted
 * 9. ADMIN sees all navigation items
 * 10. FIELD_OFFICER sees limited navigation
 * 11. SHELTER_MANAGER, RESOURCE_MANAGER, VIEWER filtered nav
 * 12. DISASTER_OPERATOR sees correct nav
 * 13. TopNav shows user info and logout button
 * 14. Logout clears auth state
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import React from 'react';

// ─── Mock the entire services/api module ──────────────────────────────────────
// IMPORTANT: vi.mock is hoisted, so the factory must only use vi.fn() directly,
// not reference outer variables that aren't initialized yet.
vi.mock('../services/api', () => ({
  authService: {
    login: vi.fn(),
    getMe: vi.fn(),
    refreshToken: vi.fn(),
  },
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

// ─── Mock useHealth to avoid live network polling ─────────────────────────────
vi.mock('../hooks/useHealth', () => ({
  useHealth: () => ({
    health: {
      status: 'ok',
      database: { connected: true, engine: 'sqlite', is_fallback: true, message: 'ok' },
    },
    loading: false,
    error: null,
  }),
}));

// ─── Mock Leaflet (not available in jsdom) ────────────────────────────────────
vi.mock('react-leaflet', () => ({
  MapContainer: ({ children }: any) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => null,
  CircleMarker: () => null,
  Tooltip: () => null,
  Marker: () => null,
  Popup: () => null,
  useMap: () => ({ setView: vi.fn() }),
}));

// ─── Import after mocks ────────────────────────────────────────────────────────
import { authService } from '../services/api';
import { AuthProvider, useAuth } from '../auth/AuthContext';
import { Login } from '../pages/Login';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { Sidebar } from '../components/layout/Sidebar';
import { TopNav } from '../components/layout/TopNav';

// Cast to access mock methods
const mockAuthService = authService as {
  login: ReturnType<typeof vi.fn>;
  getMe: ReturnType<typeof vi.fn>;
  refreshToken: ReturnType<typeof vi.fn>;
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function renderWithAuth(
  ui: React.ReactElement,
  { initialEntries = ['/'] }: { initialEntries?: string[] } = {}
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>{ui}</AuthProvider>
    </MemoryRouter>
  );
}

function seedAuthStorage(role: string, username = 'test_operator') {
  const fakeUser = {
    id: 1,
    username,
    email: `${username}@command.simulated`,
    full_name: `Test ${role}`,
    name: `Test ${role}`,
    callsign: `TAC-${role.substring(0, 3).toUpperCase()}`,
    role,
    token: 'fake-jwt-token',
    is_active: true,
  };
  localStorage.setItem('disaster_command_user', JSON.stringify(fakeUser));
  localStorage.setItem('disaster_command_token', 'fake-jwt-token');
}

function clearAuthStorage() {
  localStorage.removeItem('disaster_command_user');
  localStorage.removeItem('disaster_command_token');
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('Phase 3 — Authentication & RBAC', () => {
  beforeEach(() => {
    clearAuthStorage();
    vi.clearAllMocks();
  });

  afterEach(() => {
    clearAuthStorage();
  });

  // ─── Login Page Tests ────────────────────────────────────────────────────────
  describe('Login Page', () => {
    // Test 1: Login page renders
    it('renders the login page with all required elements', () => {
      renderWithAuth(<Login />, { initialEntries: ['/login'] });

      expect(screen.getByText(/AEGIS COMMAND PORTAL/i)).toBeInTheDocument();
      expect(document.getElementById('login-username')).toBeInTheDocument();
      expect(document.getElementById('login-password')).toBeInTheDocument();
      expect(document.getElementById('login-submit-btn')).toBeInTheDocument();
      expect(screen.getByText(/SIMULATION TESTBED/i)).toBeInTheDocument();
    });

    // Test 2: Successful login
    it('shows success message on successful login', async () => {
      mockAuthService.login.mockResolvedValue({
        access_token: 'valid-jwt-token',
        token_type: 'bearer',
        expires_in: 3600,
        user: {
          id: 1,
          username: 'admin',
          email: 'admin@command.simulated',
          full_name: 'Commander Sarah Vance (DEMO)',
          role: 'ADMIN',
          is_active: true,
          created_at: new Date().toISOString(),
        },
      });

      renderWithAuth(<Login />, { initialEntries: ['/login'] });

      fireEvent.change(document.getElementById('login-username')!, {
        target: { value: 'admin' },
      });
      fireEvent.change(document.getElementById('login-password')!, {
        target: { value: 'DemoAdminPass123!' },
      });

      await act(async () => {
        fireEvent.click(document.getElementById('login-submit-btn')!);
      });

      await waitFor(() => {
        expect(screen.getByText(/Credentials verified/i)).toBeInTheDocument();
      });

      expect(mockAuthService.login).toHaveBeenCalledWith('admin', 'DemoAdminPass123!');
    });

    // Test 3: Failed login — invalid credentials (401)
    it('shows error message on invalid credentials (401)', async () => {
      const error = Object.assign(new Error('Unauthorized'), {
        response: { status: 401, data: { detail: 'Invalid credentials' } },
      });
      mockAuthService.login.mockRejectedValue(error);

      renderWithAuth(<Login />, { initialEntries: ['/login'] });

      fireEvent.change(document.getElementById('login-username')!, {
        target: { value: 'admin' },
      });
      fireEvent.change(document.getElementById('login-password')!, {
        target: { value: 'WrongPassword!' },
      });

      await act(async () => {
        fireEvent.click(document.getElementById('login-submit-btn')!);
      });

      await waitFor(() => {
        expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
      });
    });

    // Test 4: Failed login — network error
    it('shows network error message when backend is unreachable', async () => {
      const networkError = Object.assign(new Error('Network Error'), {
        code: 'ERR_NETWORK',
        response: undefined,
      });
      mockAuthService.login.mockRejectedValue(networkError);

      renderWithAuth(<Login />, { initialEntries: ['/login'] });

      fireEvent.change(document.getElementById('login-username')!, {
        target: { value: 'admin' },
      });
      fireEvent.change(document.getElementById('login-password')!, {
        target: { value: 'AnyPassword!' },
      });

      await act(async () => {
        fireEvent.click(document.getElementById('login-submit-btn')!);
      });

      await waitFor(() => {
        expect(screen.getByText(/Network connection failure/i)).toBeInTheDocument();
      });
    });

    // Test 5: Loading state
    it('shows loading state and disables submit button during login', async () => {
      let resolveLogin!: (val: any) => void;
      mockAuthService.login.mockReturnValue(
        new Promise((resolve) => { resolveLogin = resolve; })
      );

      renderWithAuth(<Login />, { initialEntries: ['/login'] });

      fireEvent.change(document.getElementById('login-username')!, {
        target: { value: 'admin' },
      });
      fireEvent.change(document.getElementById('login-password')!, {
        target: { value: 'SomePassword!' },
      });

      act(() => {
        fireEvent.click(document.getElementById('login-submit-btn')!);
      });

      await waitFor(() => {
        expect(screen.getByText(/VERIFYING CLEARANCE/i)).toBeInTheDocument();
      });

      const btn = document.getElementById('login-submit-btn') as HTMLButtonElement;
      expect(btn.disabled).toBe(true);

      // Clean up: resolve the pending promise
      await act(async () => {
        resolveLogin({
          access_token: 'tok',
          token_type: 'bearer',
          expires_in: 3600,
          user: { id: 1, username: 'a', email: 'a@b.com', full_name: 'A', role: 'VIEWER', is_active: true, created_at: '' },
        });
      });
    });
  });

  // ─── Protected Route Tests ───────────────────────────────────────────────────
  describe('Protected Route', () => {
    // Test 6: Unauthenticated user is NOT shown protected content and redirected to login
    it('does NOT render children for unauthenticated user and redirects to login', () => {
      clearAuthStorage();
      render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <div data-testid="secret-content">Secret Dashboard</div>
                  </ProtectedRoute>
                }
              />
              <Route path="/login" element={<div data-testid="login-page">Login Page Redirected</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      expect(screen.queryByTestId('secret-content')).not.toBeInTheDocument();
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    // Test 7: Authenticated user can access protected route
    it('renders children for authenticated user', () => {
      seedAuthStorage('ADMIN');
      renderWithAuth(
        <ProtectedRoute>
          <div data-testid="dashboard-content">Dashboard Loaded</div>
        </ProtectedRoute>,
        { initialEntries: ['/'] }
      );

      expect(screen.getByTestId('dashboard-content')).toBeInTheDocument();
    });

    // Test 8: Wrong role shows access restricted (403)
    it('shows ACCESS RESTRICTED for user without required role', () => {
      seedAuthStorage('FIELD_OFFICER');
      renderWithAuth(
        <ProtectedRoute allowedRoles={['ADMIN', 'DISASTER_OPERATOR'] as any}>
          <div data-testid="admin-content">Admin Only</div>
        </ProtectedRoute>,
        { initialEntries: ['/'] }
      );

      expect(screen.queryByTestId('admin-content')).not.toBeInTheDocument();
      expect(screen.getByText(/ACCESS RESTRICTED/i)).toBeInTheDocument();
    });
  });

  // ─── Role-Based Navigation ───────────────────────────────────────────────────
  describe('Role-Based Navigation (Sidebar)', () => {
    // Test 9: ADMIN sees all 9 navigation items
    it('ADMIN sees all navigation items', () => {
      seedAuthStorage('ADMIN');
      renderWithAuth(<Sidebar isOpen={true} />, { initialEntries: ['/'] });

      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Disaster Zones')).toBeInTheDocument();
      expect(screen.getByText('Evacuation')).toBeInTheDocument();
      expect(screen.getByText('Shelters')).toBeInTheDocument();
      expect(screen.getByText('Resources')).toBeInTheDocument();
      expect(screen.getByText('Simulation')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Audit Logs')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    // Test 10: FIELD_OFFICER sees limited navigation
    it('FIELD_OFFICER sees only Command Center and Evacuation', () => {
      seedAuthStorage('FIELD_OFFICER');
      renderWithAuth(<Sidebar isOpen={true} />, { initialEntries: ['/'] });

      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Evacuation')).toBeInTheDocument();

      expect(screen.queryByText('Disaster Zones')).not.toBeInTheDocument();
      expect(screen.queryByText('Shelters')).not.toBeInTheDocument();
      expect(screen.queryByText('Resources')).not.toBeInTheDocument();
      expect(screen.queryByText('Simulation')).not.toBeInTheDocument();
      expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
      expect(screen.queryByText('Settings')).not.toBeInTheDocument();
    });

    // Test 11a: SHELTER_MANAGER
    it('SHELTER_MANAGER sees Command Center and Shelters only', () => {
      seedAuthStorage('SHELTER_MANAGER');
      renderWithAuth(<Sidebar isOpen={true} />, { initialEntries: ['/'] });

      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Shelters')).toBeInTheDocument();
      expect(screen.queryByText('Evacuation')).not.toBeInTheDocument();
    });

    // Test 11b: RESOURCE_MANAGER
    it('RESOURCE_MANAGER sees Command Center and Resources only', () => {
      seedAuthStorage('RESOURCE_MANAGER');
      renderWithAuth(<Sidebar isOpen={true} />, { initialEntries: ['/'] });

      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Resources')).toBeInTheDocument();
      expect(screen.queryByText('Shelters')).not.toBeInTheDocument();
    });

    // Test 11c: VIEWER
    it('VIEWER sees Command Center and Analytics only (read-only)', () => {
      seedAuthStorage('VIEWER');
      renderWithAuth(<Sidebar isOpen={true} />, { initialEntries: ['/'] });

      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.queryByText('Evacuation')).not.toBeInTheDocument();
      expect(screen.queryByText('Shelters')).not.toBeInTheDocument();
    });

    // Test 12: DISASTER_OPERATOR
    it('DISASTER_OPERATOR sees Command Center, Zones, Evacuation, Simulation, Analytics', () => {
      seedAuthStorage('DISASTER_OPERATOR');
      renderWithAuth(<Sidebar isOpen={true} />, { initialEntries: ['/'] });

      expect(screen.getByText('Command Center')).toBeInTheDocument();
      expect(screen.getByText('Disaster Zones')).toBeInTheDocument();
      expect(screen.getByText('Evacuation')).toBeInTheDocument();
      expect(screen.getByText('Simulation')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();

      expect(screen.queryByText('Shelters')).not.toBeInTheDocument();
      expect(screen.queryByText('Resources')).not.toBeInTheDocument();
      expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
    });
  });

  // ─── User Menu & Logout ───────────────────────────────────────────────────────
  describe('User Menu & Logout', () => {
    // Test 13: TopNav shows user info and logout button
    it('renders username and logout button in TopNav when authenticated', () => {
      seedAuthStorage('ADMIN', 'cmd_admin');
      renderWithAuth(<TopNav onToggleSidebar={vi.fn()} />, { initialEntries: ['/'] });

      expect(document.getElementById('logout-btn')).toBeInTheDocument();
      expect(screen.getByText(/cmd_admin/i)).toBeInTheDocument();
    });

    // Test 14: Logout clears auth state
    it('clears authentication state and localStorage after logout', async () => {
      seedAuthStorage('ADMIN');

      const AuthStateDisplay: React.FC = () => {
        const { isAuthenticated, logout } = useAuth();
        return (
          <div>
            <span data-testid="auth-status">
              {isAuthenticated ? 'logged-in' : 'logged-out'}
            </span>
            <button data-testid="test-logout-btn" onClick={logout}>
              Logout
            </button>
          </div>
        );
      };

      renderWithAuth(<AuthStateDisplay />, { initialEntries: ['/'] });

      expect(screen.getByTestId('auth-status')).toHaveTextContent('logged-in');

      await act(async () => {
        fireEvent.click(screen.getByTestId('test-logout-btn'));
      });

      expect(screen.getByTestId('auth-status')).toHaveTextContent('logged-out');
      expect(localStorage.getItem('disaster_command_token')).toBeNull();
      expect(localStorage.getItem('disaster_command_user')).toBeNull();
    });
  });
});
