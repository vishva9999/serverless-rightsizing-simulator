import { useState, useEffect } from 'react'
import {
  Settings as SettingsIcon,
  Database,
  Cloud,
  Shield,
  CheckCircle2,
  HardDrive,
  RefreshCw,
  Info,
  User,
  Building2,
  Lock,
  Key
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { fetchOrganization } from '../services/api'

export default function Settings() {
  const { user } = useAuth()
  const [storageStatus, setStorageStatus] = useState(null)
  const [org, setOrg] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadAllSettings = async () => {
    setLoading(true)
    try {
      const [storageRes, orgRes] = await Promise.all([
        fetch('/api/storage/status').then(r => r.json()).catch(() => null),
        fetchOrganization().catch(() => null)
      ])
      setStorageStatus(storageRes)
      setOrg(orgRes)
    } catch (err) {
      console.error('Failed to fetch settings status:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAllSettings()
  }, [])

  return (
    <div className="p-6 space-y-6 max-w-screen-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between animate-fade-in">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <SettingsIcon size={22} className="text-indigo-400" />
            System &amp; Workspace Settings
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Inspect active authentication layer, workspace organization, and persistence providers.
          </p>
        </div>

        <button
          onClick={loadAllSettings}
          className="p-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white flex items-center gap-1.5 text-xs font-semibold"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh Status
        </button>
      </div>

      {/* Authentication & User Context Row (Phase 6) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Auth Mode Card */}
        <div className="glass-card p-6 border-indigo-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
              <Key size={20} className="text-indigo-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Authentication Layer</h3>
              <p className="text-xs text-slate-400">Security Provider</p>
            </div>
          </div>
          <div className="space-y-3 text-xs pt-3 border-t border-slate-800">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Active Auth Mode:</span>
              <span className="font-bold text-indigo-400 uppercase bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                LOCAL (JWT + SQLite)
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Future Cloud Option:</span>
              <span className="font-bold text-slate-400">AWS Cognito</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Password Encryption:</span>
              <span className="font-bold text-emerald-400">Bcrypt Salt Hashing</span>
            </div>
          </div>
        </div>

        {/* Current User Profile Card */}
        <div className="glass-card p-6 border-cyan-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
              <User size={20} className="text-cyan-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Current User Profile</h3>
              <p className="text-xs text-slate-400">Session Account</p>
            </div>
          </div>
          <div className="space-y-3 text-xs pt-3 border-t border-slate-800">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Name:</span>
              <span className="font-bold text-white">{user?.full_name || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Email:</span>
              <span className="font-mono text-slate-300">{user?.email || 'N/A'}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Assigned Role:</span>
              <span className="font-bold text-cyan-300 uppercase bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                {user?.role || 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Current Organization Card */}
        <div className="glass-card p-6 border-purple-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center border border-purple-500/30">
              <Building2 size={20} className="text-purple-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Current Workspace</h3>
              <p className="text-xs text-slate-400">Multi-Tenant Organization</p>
            </div>
          </div>
          <div className="space-y-3 text-xs pt-3 border-t border-slate-800">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Organization:</span>
              <span className="font-bold text-white">{org?.name || 'Loading...'}</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Org ID:</span>
              <span className="font-mono text-[10px] text-slate-400 truncate max-w-[150px]">
                {org?.id || user?.organization_id || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Team Size:</span>
              <span className="font-bold text-purple-300">{org?.member_count || 1} Member(s)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Storage Architecture Overview (Phase 4) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Mode Status Card */}
        <div className="glass-card p-6 border-indigo-500/30">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                <HardDrive size={20} className="text-indigo-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Active Storage Mode</h3>
                <p className="text-xs text-slate-400">Environment Persistence</p>
              </div>
            </div>

            {storageStatus && (
              <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase ${
                storageStatus.mode === 'aws'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
              }`}>
                {storageStatus.mode} MODE
              </span>
            )}
          </div>

          <div className="space-y-3 text-xs pt-3 border-t border-slate-800">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">Database Engine:</span>
              <span className="font-bold text-white flex items-center gap-1">
                <Database size={13} className="text-cyan-400" />
                {storageStatus ? storageStatus.database : 'Loading...'}
              </span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">S3 Cloud Artifact Export:</span>
              <span className={`font-bold ${storageStatus?.s3_enabled ? 'text-emerald-400' : 'text-slate-400'}`}>
                {storageStatus?.s3_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>

            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400">AWS Configured:</span>
              <span className={`font-bold ${storageStatus?.aws_configured ? 'text-emerald-400' : 'text-slate-400'}`}>
                {storageStatus?.aws_configured ? 'True' : 'False'}
              </span>
            </div>
          </div>
        </div>

        {/* AWS Resource Targets Card */}
        <div className="glass-card p-6 border-cyan-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
              <Cloud size={20} className="text-cyan-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">AWS Resource Targets</h3>
              <p className="text-xs text-slate-400">DynamoDB &amp; S3 Identifiers</p>
            </div>
          </div>

          <div className="space-y-3 text-xs pt-3 border-t border-slate-800 font-mono">
            <div>
              <span className="text-slate-400 block font-sans text-[10px] uppercase font-semibold">AWS Region</span>
              <span className="text-slate-200">{storageStatus ? storageStatus.aws_region : 'ap-south-1'}</span>
            </div>

            <div>
              <span className="text-slate-400 block font-sans text-[10px] uppercase font-semibold">Scenarios Table</span>
              <span className="text-slate-200">{storageStatus ? storageStatus.scenarios_table : 'serverless-rightsizing-scenarios'}</span>
            </div>

            <div>
              <span className="text-slate-400 block font-sans text-[10px] uppercase font-semibold">History Table</span>
              <span className="text-slate-200">{storageStatus ? storageStatus.history_table : 'serverless-rightsizing-history'}</span>
            </div>

            <div>
              <span className="text-slate-400 block font-sans text-[10px] uppercase font-semibold">S3 Artifact Bucket</span>
              <span className="text-slate-200">{storageStatus ? storageStatus.s3_bucket : 'serverless-rightsizing-artifacts'}</span>
            </div>
          </div>
        </div>

        {/* Security & Architecture Card */}
        <div className="glass-card p-6 border-purple-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center border border-purple-500/30">
              <Shield size={20} className="text-purple-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Security &amp; Persistence</h3>
              <p className="text-xs text-slate-400">Repository Selector Pattern</p>
            </div>
          </div>

          <div className="space-y-2 text-xs text-slate-300 pt-3 border-t border-slate-800">
            <p className="flex items-start gap-2">
              <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Zero Hardcoded Credentials</strong>: Uses standard environment &amp; JWT secret resolution.</span>
            </p>
            <p className="flex items-start gap-2">
              <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Multi-Tenant Isolation</strong>: Scenarios and history are strictly partitioned by organization.</span>
            </p>
            <p className="flex items-start gap-2">
              <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Role-Based Access Control (RBAC)</strong>: Role verification enforced in backend FastAPI endpoints.</span>
            </p>
          </div>
        </div>

      </div>

      {/* Info Callout */}
      <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/20 text-xs text-indigo-300 flex items-start gap-3">
        <Info size={18} className="text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold text-white">Educational Architecture Note</p>
          <p className="mt-1 leading-relaxed text-slate-300">
            This project uses local JWT and SQLite authentication for seamless local execution. All endpoints enforce Organization Isolation and RBAC (Admin, Analyst, Viewer). AWS Cognito and DynamoDB integration can be activated via configuration without rewriting business logic.
          </p>
        </div>
      </div>
    </div>
  )
}
