import axios from 'axios'
import { getApiBaseUrl } from '@/src/config/env'

/**
 * Instance Axios centralisée pour toutes les requêtes HTTP.
 * Le token JWT est injecté automatiquement via un intercepteur.
 */
const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
