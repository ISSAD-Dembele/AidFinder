import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import userService from '@/src/services/user'
import { isProfileComplete } from '@/src/utils/profile'

const ProfileContext = createContext(null)

/**
 * Contexte profil — centralise les données utilisateur et la complétion du profil.
 * Utilisé par le Dashboard, la page Profil et la fenêtre de complétion obligatoire.
 */
export function ProfileProvider({ children }) {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchProfile = useCallback(async () => {
    setLoading(true)
    try {
      const data = await userService.getProfile()
      setProfile(data)
      return data
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  const updateProfile = useCallback(async (data) => {
    const updated = await userService.updateProfile(data)
    setProfile(updated)
    return updated
  }, [])

  const uploadPhoto = useCallback(async (file) => {
    await userService.uploadPhoto(file)
    return fetchProfile()
  }, [fetchProfile])

  const deletePhoto = useCallback(async () => {
    const updated = await userService.deletePhoto()
    setProfile(updated)
    return updated
  }, [])

  const value = useMemo(
    () => ({
      profile,
      loading,
      isProfileComplete: isProfileComplete(profile),
      updateProfile,
      uploadPhoto,
      deletePhoto,
      refreshProfile: fetchProfile,
    }),
    [profile, loading, updateProfile, uploadPhoto, deletePhoto, fetchProfile]
  )

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>
}

export function useProfile() {
  const context = useContext(ProfileContext)
  if (!context) {
    throw new Error('useProfile doit être utilisé dans un ProfileProvider')
  }
  return context
}
