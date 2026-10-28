import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { Role } from '../../types';
import { ShieldAlert } from 'lucide-react';

interface ProtectedRouteProps {
  allowedRoles?: Role[];
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles, children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#070b13] flex items-center justify-center font-mono text-cyan-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs uppercase tracking-wider">Verifying Security Clearance...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <div className="p-8 max-w-lg mx-auto mt-12 bg-red-950/40 border border-red-800 rounded-xl font-mono text-center">
        <ShieldAlert className="w-12 h-12 text-red-400 mx-auto mb-4 animate-bounce" />
        <h2 className="text-lg font-bold text-red-200 mb-2">ACCESS RESTRICTED (HTTP 403)</h2>
        <p className="text-xs text-slate-300 mb-4">
          Your current security role ({user.role}) does not possess clearance for this operational view.
        </p>
        <span className="text-[11px] text-slate-500">Contact System Administrator for credential elevation.</span>
      </div>
    );
  }

  return children ? <>{children}</> : <Outlet />;
};
