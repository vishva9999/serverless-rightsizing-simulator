import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, Role } from '../types';
import { authService } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  mockLogin: (role: Role, name?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('disaster_command_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('disaster_command_token');
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (user && token) {
      localStorage.setItem('disaster_command_user', JSON.stringify(user));
      localStorage.setItem('disaster_command_token', token);
    } else {
      localStorage.removeItem('disaster_command_user');
      localStorage.removeItem('disaster_command_token');
    }
  }, [user, token]);

  const login = async (usernameOrEmail: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const data = await authService.login(usernameOrEmail, password);
      const authenticatedUser: User = {
        id: data.user.id,
        username: data.user.username,
        email: data.user.email,
        full_name: data.user.full_name,
        name: data.user.full_name,
        callsign: `TAC-${data.user.role.substring(0, 3).toUpperCase()}`,
        role: data.user.role as Role,
        token: data.access_token,
        is_active: data.user.is_active,
      };

      setToken(data.access_token);
      setUser(authenticatedUser);
      localStorage.setItem('disaster_command_token', data.access_token);
      localStorage.setItem('disaster_command_user', JSON.stringify(authenticatedUser));
    } finally {
      setIsLoading(false);
    }
  };

  const mockLogin = (role: Role, name?: string) => {
    const mockUser: User = {
      id: `usr-${Date.now().toString().slice(-4)}`,
      username: (name || role).toLowerCase().replace(/\s+/g, '_'),
      email: `${(name || role).toLowerCase().replace(/\s+/g, '_')}@command.simulated`,
      full_name: name || `Officer ${role}`,
      name: name || `Officer ${role}`,
      callsign: `TAC-${role.substring(0, 3).toUpperCase()}`,
      role,
      token: `sim-token-${Date.now()}`,
      is_active: true,
    };
    setToken(mockUser.token || 'sim-token');
    setUser(mockUser);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('disaster_command_user');
    localStorage.removeItem('disaster_command_token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        mockLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
