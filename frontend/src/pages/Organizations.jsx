/**
 * Organizations & Team Management Page — Phase 6.
 * Admin: View/Edit Org details, invite members, change roles, activate/deactivate accounts.
 * Analyst: Read-only member list.
 */

import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import {
  fetchOrganization,
  updateOrganization,
  fetchUsers,
  createUserInOrg,
  updateUserRole,
  updateUserStatus
} from '../services/api'
import {
  Building2,
  Users,
  Shield,
  UserPlus,
  Edit2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  MoreVertical,
  Mail,
  Lock,
  User
} from 'lucide-react'

export const Organizations = () => {
  const { user, hasRole } = useAuth()
  const isAdmin = hasRole('admin')

  const [org, setOrg] = useState(null)
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  // Modals
  const [showEditOrgModal, setShowEditOrgModal] = useState(false)
  const [orgForm, setOrgForm] = useState({ name: '', description: '' })

  const [showAddUserModal, setShowAddUserModal] = useState(false)
  const [userForm, setUserForm] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'analyst'
  })

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [orgData, usersData] = await Promise.all([
        fetchOrganization(),
        fetchUsers()
      ])
      setOrg(orgData)
      setOrgForm({ name: orgData.name, description: orgData.description || '' })
      setMembers(usersData)
    } catch (err) {
      console.error('Failed to load organization data:', err)
      setError(err.response?.data?.detail || 'Failed to fetch organization and members.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleUpdateOrg = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      const updated = await updateOrganization(orgForm)
      setOrg(updated)
      setShowEditOrgModal(false)
      setSuccessMsg('Organization profile updated successfully.')
      setTimeout(() => setSuccessMsg(null), 4000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update organization.')
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      await createUserInOrg(userForm)
      setShowAddUserModal(false)
      setUserForm({ email: '', password: '', full_name: '', role: 'analyst' })
      setSuccessMsg('New team member added successfully.')
      setTimeout(() => setSuccessMsg(null), 4000)
      loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user.')
    }
  }

  const handleRoleChange = async (targetUserId, newRole) => {
    setError(null)
    try {
      await updateUserRole(targetUserId, newRole)
      setSuccessMsg(`Role updated to ${newRole.toUpperCase()}.`)
      setTimeout(() => setSuccessMsg(null), 4000)
      loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change role.')
    }
  }

  const handleStatusToggle = async (targetUserId, currentStatus) => {
    setError(null)
    try {
      await updateUserStatus(targetUserId, !currentStatus)
      setSuccessMsg(`Account ${!currentStatus ? 'activated' : 'deactivated'} successfully.`)
      setTimeout(() => setSuccessMsg(null), 4000)
      loadData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to toggle account status.')
    }
  }

  if (loading && !org) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 text-sm">Loading organization workspace...</p>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Building2 className="w-6 h-6 text-indigo-400" />
            <span>Organization & Team Management</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Manage multi-tenant workspace profile, access roles, and team members
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {isAdmin && (
            <button
              onClick={() => setShowAddUserModal(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-medium text-sm rounded-xl shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition-all"
            >
              <UserPlus className="w-4 h-4" />
              <span>Add Member</span>
            </button>
          )}
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-start space-x-3 text-red-400 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-start space-x-3 text-emerald-400 text-sm">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Organization Overview Card */}
      {org && (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl flex items-center justify-center text-indigo-400">
                  <Building2 className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">{org.name}</h2>
                  <p className="text-xs text-slate-400 font-mono">Workspace ID: {org.id}</p>
                </div>
              </div>
              <p className="text-slate-300 text-sm max-w-2xl mt-2">
                {org.description || 'No description provided for this organization.'}
              </p>
            </div>

            <div className="flex items-center space-x-6 border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-400">{members.length}</div>
                <div className="text-xs text-slate-400">Team Members</div>
              </div>
              {isAdmin && (
                <button
                  onClick={() => setShowEditOrgModal(true)}
                  className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 flex items-center space-x-1.5 transition-colors"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                  <span>Edit Profile</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Members Management Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">Team Members</h3>
          </div>
          <span className="text-xs text-slate-400">
            {isAdmin ? 'Full Role & Access Control' : 'Read-Only View'}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase tracking-wider">
              <tr>
                <th className="py-3.5 px-6">User</th>
                <th className="py-3.5 px-6">Role</th>
                <th className="py-3.5 px-6">Status</th>
                <th className="py-3.5 px-6">Joined Date</th>
                {isAdmin && <th className="py-3.5 px-6 text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {members.map((m) => (
                <tr key={m.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6">
                    <div className="font-semibold text-white flex items-center space-x-2">
                      <span>{m.full_name}</span>
                      {m.id === user?.id && (
                        <span className="px-1.5 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] rounded font-mono">YOU</span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400">{m.email}</div>
                  </td>
                  <td className="py-4 px-6">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                        m.role === 'admin'
                          ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                          : m.role === 'analyst'
                          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                          : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                      }`}
                    >
                      {m.role}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    {m.is_active ? (
                      <span className="inline-flex items-center text-xs text-emerald-400 space-x-1 font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Active</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center text-xs text-red-400 space-x-1 font-medium">
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Deactivated</span>
                      </span>
                    )}
                  </td>
                  <td className="py-4 px-6 text-xs text-slate-400">
                    {m.created_at ? new Date(m.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  {isAdmin && (
                    <td className="py-4 px-6 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {/* Role selector dropdown */}
                        <select
                          value={m.role}
                          onChange={(e) => handleRoleChange(m.id, e.target.value)}
                          className="bg-slate-800 border border-slate-700 text-xs text-white rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        >
                          <option value="admin">Admin</option>
                          <option value="analyst">Analyst</option>
                          <option value="viewer">Viewer</option>
                        </select>

                        {/* Status Toggle */}
                        <button
                          onClick={() => handleStatusToggle(m.id, m.is_active)}
                          className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
                            m.is_active
                              ? 'bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20'
                              : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20'
                          }`}
                        >
                          {m.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Organization Modal */}
      {showEditOrgModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4">Edit Organization</h3>
            <form onSubmit={handleUpdateOrg} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Organization Name</label>
                <input
                  type="text"
                  required
                  value={orgForm.name}
                  onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Description</label>
                <textarea
                  rows="3"
                  value={orgForm.description}
                  onChange={(e) => setOrgForm({ ...orgForm, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEditOrgModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
              <UserPlus className="w-5 h-5 text-indigo-400" />
              <span>Add Member to Organization</span>
            </h3>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={userForm.full_name}
                  onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
                  placeholder="Jane Doe"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={userForm.email}
                  onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                  placeholder="jane@example.com"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Temporary Password</label>
                <input
                  type="password"
                  required
                  value={userForm.password}
                  onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Role</label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                >
                  <option value="analyst">Analyst (Create/Edit scenarios, run simulations)</option>
                  <option value="viewer">Viewer (Read-only access)</option>
                  <option value="admin">Administrator (Full access)</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddUserModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  Create Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
