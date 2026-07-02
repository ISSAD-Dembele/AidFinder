import api from './api'

/**
 * Service d'authentification — communique avec les routes FastAPI /auth/*
 */
export const authService = {
  /** Inscription d'un nouvel utilisateur */
  register: async ({ nom, email, password }) => {
    const { data } = await api.post('/auth/register', { nom, email, password })
    return data
  },

  /** Connexion et récupération du JWT */
  login: async ({ email, password }) => {
    const { data } = await api.post('/auth/login', { email, password })
    return data
  },

  /** Désactivation du compte utilisateur (route protégée) */
  deactivate: async () => {
    const { data } = await api.patch('/auth/deactivate')
    return data
  },
}

export default authService
