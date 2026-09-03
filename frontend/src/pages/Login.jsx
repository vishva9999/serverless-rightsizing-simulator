/**
 * Login Page — Phase 6 Authentication.
 * Includes user credentials form, demo account quick-fill buttons, error notifications.
 */

import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { LogIn, Lock, Mail, AlertCircle, Sparkles, Shield, UserCheck, Eye } from 'lucide-react'

export const Login = ({ onNavigateToRegister, onLoginSuccess }) => {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      await login(email, password)
      if (onLoginSuccess) {
        onLoginSuccess()
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid email or password. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleQuickFill = (demoEmail, demoPass) => {
    setEmail(demoEmail)
    setPassword(demoPass)
    setError(null)
  }

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 py-8">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        {/* Subtle Background Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-60 h-24 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

        {/* Header */}
        <div className="text-center mb-8 relative z-10">
          <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/20">
            <LogIn className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Sign In to Simulator</h2>
          <p className="text-slate-400 text-sm mt-1.5">
            Serverless Cost & Performance Rightsizing Platform
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-start space-x-3 text-red-400 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                <Mail className="w-4 h-4" />
              </div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 px-4 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-medium text-sm rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Signing In...</span>
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </>
            )}
          </button>
        </form>

        {/* Development Quick Fill Presets */}
        <div className="mt-8 pt-6 border-t border-slate-800">
          <p className="text-xs font-semibold text-slate-400 mb-3 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Development Demo Accounts (One-Click):</span>
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleQuickFill('admin@example.com', 'AdminPass123!')}
              className="px-2 py-2 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-lg text-xs font-medium text-indigo-300 transition-colors text-center"
            >
              <div className="font-semibold text-white">Admin</div>
              <div className="text-[10px] text-slate-400">Full Access</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('analyst@example.com', 'AnalystPass123!')}
              className="px-2 py-2 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-lg text-xs font-medium text-cyan-300 transition-colors text-center"
            >
              <div className="font-semibold text-white">Analyst</div>
              <div className="text-[10px] text-slate-400">Run & Edit</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('viewer@example.com', 'ViewerPass123!')}
              className="px-2 py-2 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-lg text-xs font-medium text-slate-300 transition-colors text-center"
            >
              <div className="font-semibold text-white">Viewer</div>
              <div className="text-[10px] text-slate-400">Read-Only</div>
            </button>
          </div>
        </div>

        {/* Switch to Register */}
        <div className="mt-6 text-center text-xs text-slate-400">
          Need a new workspace organization?{' '}
          <button
            type="button"
            onClick={onNavigateToRegister}
            className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2 ml-1"
          >
            Create an Account
          </button>
        </div>
      </div>
    </div>
  )
}
