import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import authService from '@/src/services/auth'

const AuthContext = createContext(null)

const TOKEN_KEY = 'access_token'
const USER_KEY = 'user'

/** Décode le payload du JWT sans bibliothèque externe */
function decodeToken(token) {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(USER_KEY)
    return stored ? JSON.parse(stored) : null
  })

  const isAuthenticated = Boolean(token)

  const login = useCallback(async (credentials) => {
    const data = await authService.login(credentials)
    localStorage.setItem(TOKEN_KEY, data.access_token)

    const payload = decodeToken(data.access_token)
    const userData = { email: credentials.email, userId: payload?.sub }

    localStorage.setItem(USER_KEY, JSON.stringify(userData))
    setToken(data.access_token)
    setUser(userData)
    return data
  }, [])

  const register = useCallback(async (userData) => {
    const data = await authService.register(userData)
    return data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const deactivateAccount = useCallback(async () => {
    await authService.deactivate()
    logout()
  }, [logout])

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated,
      login,
      register,
      logout,
      deactivateAccount,
    }),
    [token, user, isAuthenticated, login, register, logout, deactivateAccount]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider')
  }
  return context
}
