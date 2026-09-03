/**
 * Authentication Context — Phase 6 Frontend Auth Store.
 * Manages JWT tokens, authenticated user profile, login, registration, and role checks.
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import { loginUser, registerUser, fetchCurrentUser } from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [token, setToken] = useState(() => localStorage.getItem('access_token') || null)
  const [isLoading, setIsLoading] = useState(true)

  // Verify stored token on initial app load
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('access_token')
      if (storedToken) {
        try {
          const profile = await fetchCurrentUser()
          setUser(profile)
          localStorage.setItem('user', JSON.stringify(profile))
        } catch (err) {
          console.warn('Stored token is invalid or expired:', err)
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          setUser(null)
          setToken(null)
        }
      }
      setIsLoading(false)
    }

    initAuth()

    const handleUnauthorized = () => {
      setUser(null)
      setToken(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  const login = async (email, password) => {
    const data = await loginUser({ email, password })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  const register = async (registrationData) => {
    const data = await registerUser(registrationData)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
    setToken(null)
  }

  const hasRole = (allowedRoles) => {
    if (!user || !user.role) return false
    if (typeof allowedRoles === 'string') return user.role.toLowerCase() === allowedRoles.toLowerCase()
    if (Array.isArray(allowedRoles)) return allowedRoles.map(r => r.toLowerCase()).includes(user.role.toLowerCase())
    return false
  }

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
    hasRole,
    setUser
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
