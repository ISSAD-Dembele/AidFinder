import api from './api'

/**
 * Service Dashboard — communique avec les routes FastAPI /dashboard, /history, /recommendations, /recent-aids, /stats
 */
export const dashboardService = {
  /** Récupère les données consolidées de la page d'accueil du dashboard */
  getDashboard: async () => {
    const { data } = await api.get('/dashboard')
    return data
  },

  /** Récupère l'historique complet des conversations */
  getHistory: async () => {
    const { data } = await api.get('/history')
    return data
  },

  /** Récupère la liste des recommandations d'aides adaptées à l'utilisateur */
  getRecommendations: async () => {
    const { data } = await api.get('/recommendations')
    return data
  },

  /** Récupère les dernières aides consultées */
  getRecentAids: async () => {
    const { data } = await api.get('/recent-aids')
    return data
  },

  /** Récupère les statistiques détaillées de l'utilisateur */
  getStats: async () => {
    const { data } = await api.get('/stats')
    return data
  },
}

export default dashboardService
