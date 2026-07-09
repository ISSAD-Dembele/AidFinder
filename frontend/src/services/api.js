import axios from 'axios'
import { getApiBaseUrl } from '@/src/config/env'

/**
 * Instance Axios centralisée pour toutes les requêtes HTTP.
 * Le token JWT est injecté automatiquement via un intercepteur.
 * L'URL de base est recalculée à chaque requête pour rester cohérente
 * avec l'hôte du navigateur (PC, téléphone, tablette).
 */
const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl()

  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** Intercepteur de réponse — gère les 401 (token expiré/invalide) */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      // Redirection vers la page de connexion si on n'y est pas déjà
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
