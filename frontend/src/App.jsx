import React, { useState } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Scenarios from './pages/Scenarios'
import Simulator from './pages/Simulator'
import Sensitivity from './pages/Sensitivity'
import History from './pages/History'
import Settings from './pages/Settings'
import { Organizations } from './pages/Organizations'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { ProtectedRoute } from './components/auth/ProtectedRoute'

/**
 * Main Application Router & State Manager — Phase 6.
 * Protected by AuthProvider and Role-Based Route Guards.
 */
function AppContent() {
  const { isAuthenticated, isLoading } = useAuth()
  const [activePage, setActivePage] = useState('dashboard')
  const [authView, setAuthView] = useState('login') // 'login' | 'register'

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm">Initializing Serverless Simulator...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
        {authView === 'login' ? (
          <Login
            onNavigateToRegister={() => setAuthView('register')}
            onLoginSuccess={() => setActivePage('dashboard')}
          />
        ) : (
          <Register
            onNavigateToLogin={() => setAuthView('login')}
            onRegisterSuccess={() => setActivePage('dashboard')}
          />
        )}
      </div>
    )
  }

  function renderPage() {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard onNavigate={setActivePage} />
      case 'scenarios':
        return <Scenarios />
      case 'simulator':
        return (
          <ProtectedRoute requiredRoles={['admin', 'analyst']}>
            <Simulator />
          </ProtectedRoute>
        )
      case 'sensitivity':
        return (
          <ProtectedRoute requiredRoles={['admin', 'analyst']}>
            <Sensitivity />
          </ProtectedRoute>
        )
      case 'history':
        return <History />
      case 'organizations':
        return (
          <ProtectedRoute requiredRoles={['admin', 'analyst']}>
            <Organizations />
          </ProtectedRoute>
        )
      case 'settings':
        return <Settings />
      default:
        return <Dashboard onNavigate={setActivePage} />
    }
  }

  return (
    <Layout activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </Layout>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
