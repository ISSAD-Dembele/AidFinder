import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import authService from '@/src/services/auth'
import userService from '@/src/services/user'
import { getDashboardBasePath } from '@/src/utils/navigation'

const AuthContext = createContext(null)

const TOKEN_KEY = 'access_token'
const USER_KEY = 'user'

function decodeToken(token) {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

/** Charge le profil pour récupérer le rôle après authentification */
async function fetchUserRole() {
  const profile = await userService.getProfile()
  return {
    email: profile.email,
    userId: profile.user_id,
    role: profile.role,
    nom: profile.nom,
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(USER_KEY)
    return stored ? JSON.parse(stored) : null
  })
  const [authLoading, setAuthLoading] = useState(Boolean(localStorage.getItem(TOKEN_KEY)))

  const isAuthenticated = Boolean(token)
  const role = user?.role ?? null

  // Recharge le rôle au démarrage si un JWT est présent
  useEffect(() => {
    if (!token) {
      setAuthLoading(false)
      return
    }
    fetchUserRole()
      .then((userData) => {
        setUser(userData)
        localStorage.setItem(USER_KEY, JSON.stringify(userData))
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
        setToken(null)
        setUser(null)
      })
      .finally(() => setAuthLoading(false))
  }, [token])

  const login = useCallback(async (credentials) => {
    const data = await authService.login(credentials)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setToken(data.access_token)

    const userData = await fetchUserRole()
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
    setUser(userData)

    return { ...data, role: userData.role }
  }, [])

  const register = useCallback(async (userData) => {
    return authService.register(userData)
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
      role,
      authLoading,
      isAuthenticated,
      login,
      register,
      logout,
      deactivateAccount,
      getDashboardBasePath: () => getDashboardBasePath(role),
    }),
    [token, user, role, authLoading, isAuthenticated, login, register, logout, deactivateAccount]
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
