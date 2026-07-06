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

export default api
