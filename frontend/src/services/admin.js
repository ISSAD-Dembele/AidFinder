import api from './api'

export const adminService = {
  getDashboard: async () => {
    const { data } = await api.get('/admin/dashboard')
    return data
  },

  getAides: async () => {
    const { data } = await api.get('/admin/aides')
    return data
  },

  getStatistics: async () => {
    const { data } = await api.get('/admin/statistiques')
    return data
  },
}

export default adminService
