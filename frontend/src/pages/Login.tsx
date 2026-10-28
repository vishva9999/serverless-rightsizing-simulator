import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Shield, Lock, UserCheck, AlertTriangle, AlertCircle, CheckCircle2, Loader2, Key } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!usernameOrEmail.trim() || !password) {
      setErrorMessage('Please enter both username/email and password.');
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    try {
      await login(usernameOrEmail.trim(), password);
      setSuccessMessage('Credentials verified. Entering command console...');
      setTimeout(() => {
        navigate(from, { replace: true });
      }, 500);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setErrorMessage('Invalid credentials: username/email or password incorrect.');
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        setErrorMessage('Network connection failure. Backend command server unreachable.');
      } else {
        setErrorMessage(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (user: string, pass: string) => {
    setUsernameOrEmail(user);
    setPassword(pass);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-[#070b13] flex flex-col justify-center items-center p-4 relative overflow-hidden tactical-grid font-mono">
      {/* Background glow accents */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-red-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Top Disclaimer Badge */}
      <div className="mb-6 flex items-center gap-2 bg-amber-950/60 border border-amber-600/40 text-amber-300 px-3.5 py-1.5 rounded-full text-xs">
        <AlertTriangle className="w-4 h-4 text-amber-400" />
        <span>SIMULATION TESTBED — AUTHORIZED DRILL PERSONNEL ONLY</span>
      </div>

      <div className="w-full max-w-md bg-[#0d1424] border border-slate-800 rounded-xl p-6 md:p-8 shadow-2xl relative z-10 backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800/80">
          <div className="p-2.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-wider">
              AEGIS COMMAND PORTAL
            </h1>
            <p className="text-xs text-cyan-400 uppercase tracking-widest">
              Role-Based Access Control
            </p>
          </div>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-4 p-3 rounded-md bg-red-950/70 border border-red-800/80 text-red-300 text-xs flex items-center gap-2 animate-fadeIn">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Success Alert */}
        {successMessage && (
          <div className="mb-4 p-3 rounded-md bg-emerald-950/70 border border-emerald-800/80 text-emerald-300 text-xs flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs uppercase tracking-wider text-slate-300 mb-1.5">
              Operator Username / Email
            </label>
            <input
              id="login-username"
              type="text"
              required
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              placeholder="e.g. admin or admin@command.simulated"
              disabled={loading}
              className="w-full bg-[#080c14] border border-slate-700 rounded-md px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs uppercase tracking-wider text-slate-300 mb-1.5">
              Secure Passkey
            </label>
            <div className="relative">
              <input
                id="login-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                disabled={loading}
                className="w-full bg-[#080c14] border border-slate-700 rounded-md px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <Key className="w-4 h-4 text-slate-500 absolute right-3 top-3 pointer-events-none" />
            </div>
          </div>

          <div className="pt-2">
            <button
              id="login-submit-btn"
              type="submit"
              disabled={loading}
              className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:opacity-60 text-slate-950 font-bold py-2.5 px-4 rounded-md flex items-center justify-center gap-2 transition-all shadow-glow-cyan"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                  <span>VERIFYING CLEARANCE...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>INITIALIZE SECURE CONSOLE</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Demo Fast-Fill Accounts */}
        <div className="mt-6 pt-5 border-t border-slate-800">
          <div className="text-[11px] text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Preset Simulated Profiles</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickFill('admin', 'DemoAdminPass123!')}
              className="px-2.5 py-1.5 rounded bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-cyan-500 hover:text-white transition-all text-left"
            >
              ★ Admin (Full)
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('op_chen', 'DemoOperator123!')}
              className="px-2.5 py-1.5 rounded bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-cyan-500 hover:text-white transition-all text-left"
            >
              ❖ Operator (Disaster)
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('field_rodriguez', 'DemoField123!')}
              className="px-2.5 py-1.5 rounded bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-cyan-500 hover:text-white transition-all text-left"
            >
              ➔ Field (Evac)
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('shelter_kumar', 'DemoShelter123!')}
              className="px-2.5 py-1.5 rounded bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-cyan-500 hover:text-white transition-all text-left"
            >
              ▲ Shelter (Housing)
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('log_smith', 'DemoLogistics123!')}
              className="px-2.5 py-1.5 rounded bg-slate-900/90 border border-slate-800 text-slate-300 hover:border-cyan-500 hover:text-white transition-all text-left col-span-2"
            >
              ◆ Logistics (Resources)
            </button>
          </div>
        </div>
      </div>

      <footer className="mt-6 text-center text-xs text-slate-500 max-w-md">
        DISCLAIMER: This system is a simulated exercise platform for testing AI-assisted
        evacuation routing and resource allocation. It does NOT dispatch real municipal emergency services.
      </footer>
    </div>
  );
};
