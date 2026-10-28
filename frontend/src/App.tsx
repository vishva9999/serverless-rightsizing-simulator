import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { RootLayout } from './layouts/RootLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { DisasterZones } from './pages/DisasterZones';
import { Evacuation } from './pages/Evacuation';
import { Shelters } from './pages/Shelters';
import { Resources } from './pages/Resources';
import { Simulation } from './pages/Simulation';
import { Analytics } from './pages/Analytics';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <RootLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="zones" element={<DisasterZones />} />
            <Route path="evacuation" element={<Evacuation />} />
            <Route path="shelters" element={<Shelters />} />
            <Route path="resources" element={<Resources />} />
            <Route path="simulation" element={<Simulation />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="audit-logs" element={<AuditLogs />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
