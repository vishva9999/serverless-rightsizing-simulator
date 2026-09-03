/**
 * Protected Route Wrapper Component — Phase 6.
 * Ensures user is authenticated before viewing protected pages.
 */

import React from 'react'
import { useAuth } from '../../context/AuthContext'
import { ShieldAlert } from 'lucide-react'

export const ProtectedRoute = ({ children, requiredRoles, onNavigateToLogin }) => {
  const { isAuthenticated, isLoading, hasRole, user } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm">Verifying authentication...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    if (onNavigateToLogin) {
      onNavigateToLogin()
      return null
    }
    return null
  }

  if (requiredRoles && !hasRole(requiredRoles)) {
    return (
      <div className="bg-slate-900 border border-red-500/20 rounded-2xl p-8 max-w-xl mx-auto my-12 text-center shadow-xl">
        <div className="w-14 h-14 bg-red-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-red-400">
          <ShieldAlert className="w-7 h-7" />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">Access Restricted</h3>
        <p className="text-slate-300 text-sm leading-relaxed mb-4">
          Your current role (<span className="font-semibold text-indigo-400 uppercase">{user?.role}</span>) does not have sufficient permissions to access this feature.
        </p>
        <p className="text-slate-500 text-xs">
          Required Role: {Array.isArray(requiredRoles) ? requiredRoles.join(' or ') : requiredRoles}
        </p>
      </div>
    )
  }

  return children
}
