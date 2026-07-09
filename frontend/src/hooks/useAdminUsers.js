import { useState, useEffect, useCallback } from 'react'
import adminService from '@/src/services/admin'

export default function useAdminUsers() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await adminService.getUsers()
      setUsers(result)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const activateUser = useCallback(async (userId) => {
    const updated = await adminService.activateUser(userId)
    setUsers((prev) => prev.map((u) => (u.user_id === userId ? updated : u)))
    return updated
  }, [])

  const deactivateUser = useCallback(async (userId) => {
    const updated = await adminService.deactivateUser(userId)
    setUsers((prev) => prev.map((u) => (u.user_id === userId ? updated : u)))
    return updated
  }, [])

  const deleteUser = useCallback(async (userId) => {
    await adminService.deleteUser(userId)
    setUsers((prev) => prev.filter((u) => u.user_id !== userId))
  }, [])

  const updateUser = useCallback(async (userId, payload) => {
    const updated = await adminService.updateUser(userId, payload)
    setUsers((prev) => prev.map((u) => (u.user_id === userId ? updated : u)))
    return updated
  }, [])

  return { users, loading, error, refresh: fetch, activateUser, deactivateUser, deleteUser, updateUser }
}
