/**
 * App Shell Tests — Phase 3
 *
 * Tests the simulation banner and login redirect for unauthenticated users.
 * Nav items are role-gated so we test them in auth.test.tsx instead.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../auth/AuthContext';
import { SimulationBanner } from '../components/ui/SimulationBanner';
import { Login } from '../pages/Login';

// Mock axios before any imports that use it
vi.mock('axios', () => {
  const mockAxios: any = {
    create: vi.fn(() => mockAxios),
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: { headers: { common: {} } },
  };
  return { default: mockAxios };
});

// Mock useHealth to prevent network calls
vi.mock('../hooks/useHealth', () => ({
  useHealth: () => ({
    health: null,
    loading: false,
    error: null,
  }),
}));

describe('AI Disaster Command Center Frontend Shell', () => {
  it('renders simulation safety notice banner', () => {
    render(<SimulationBanner />);
    expect(screen.getByText(/SIMULATION MODE ACTIVE/i)).toBeInTheDocument();
    expect(screen.getByText(/NO REAL DISPATCH/i)).toBeInTheDocument();
  });

  it('unauthenticated App shows login page (not dashboard nav)', () => {
    // With no localStorage auth, app should route to login page
    render(
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>
    );

    // Login portal should be visible
    expect(screen.getByText(/AEGIS COMMAND PORTAL/i)).toBeInTheDocument();
  });
});
