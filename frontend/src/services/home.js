import api from './api'

/**
 * Service page d'accueil — communique avec les routes FastAPI /api/home/*
 */
export const homeService = {
  getLatestAids: async () => {
    const { data } = await api.get('/api/home/latest-aids')
    return data
  },

  getStats: async () => {
    const { data } = await api.get('/api/home/stats')
    return data
  },

  getCategories: async () => {
    const { data } = await api.get('/api/home/categories')
    return data
  },

  searchAids: async (query) => {
    const { data } = await api.get('/api/home/search', { params: { q: query } })
    return data
  },
}

export default homeService
