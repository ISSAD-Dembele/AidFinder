import api from './api'

/**
 * Service Dashboard — communique avec les routes FastAPI /dashboard/*
 */
export const dashboardService = {
  /** Récupère les données consolidées de la page d'accueil du dashboard */
  getDashboard: async () => {
    const { data } = await api.get('/dashboard')
    return data
  },

  /** Récupère l'historique complet des conversations */
  getHistory: async () => {
    const { data } = await api.get('/dashboard/history')
    return data
  },

  /** Récupère la liste des recommandations d'aides adaptées à l'utilisateur */
  getRecommendations: async () => {
    const { data } = await api.get('/dashboard/recommendations')
    return data
  },

  /** Récupère les dernières aides consultées */
  getRecentAids: async () => {
    const { data } = await api.get('/dashboard/recent-aids')
    return data
  },

  /** Récupère les statistiques détaillées de l'utilisateur */
  getStats: async () => {
    const { data } = await api.get('/dashboard/stats')
    return data
  },

  /** Récupère les détails (messages) d'une discussion */
  getHistoryDetail: async (historyId) => {
    const { data } = await api.get(`/dashboard/history/${historyId}`)
    return data
  },

  /** Supprime une discussion par son ID */
  deleteHistory: async (historyId) => {
    const { data } = await api.delete(`/dashboard/history/${historyId}`)
    return data
  },

  /** Envoie un message de discussion (crée ou continue) */
  sendChatMessage: async (message, historiqueId = null) => {
    const { data } = await api.post('/dashboard/chat', {
      message,
      historique_id: historiqueId,
    })
    return data
  },

  recordAidConsultation: async (aideId) => {
    const { data } = await api.post(`/api/home/aids/${aideId}/consultation`)
    return data
  },

  recordChatConsultation: async (historiqueId, aideId) => {
    const { data } = await api.post(`/dashboard/chat/${historiqueId}/consultation/${aideId}`)
    return data
  },
}

export default dashboardService
