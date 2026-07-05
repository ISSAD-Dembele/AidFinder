import api from './api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Service utilisateur — communique avec les routes FastAPI /users/*
 */
export const userService = {
  getProfile: async () => {
    const { data } = await api.get('/users/me')
    return data
  },

  updateProfile: async (profileData) => {
    const { data } = await api.patch('/users/me', profileData)
    return data
  },

  changePassword: async ({ current_password, new_password, confirm_new_password }) => {
    const { data } = await api.patch('/users/change-password', {
      current_password,
      new_password,
      confirm_new_password,
    })
    return data
  },

  uploadPhoto: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.patch('/users/photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  /** Supprime la photo via PATCH /users/me (photo_profil: null) */
  deletePhoto: async () => {
    const { data } = await api.patch('/users/me', { photo_profil: null })
    return data
  },
}

/** Construit l'URL complète d'une photo de profil servie par FastAPI */
export function getProfilePhotoUrl(photoPath) {
  if (!photoPath) return null
  return `${API_URL}${photoPath}`
}

export default userService
