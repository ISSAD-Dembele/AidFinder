import { useState, useEffect, useCallback } from 'react'
import adminService from '@/src/services/admin'

export default function useAdminLogs() {
  const [logs, setLogs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await adminService.getLogs()
      setLogs(result)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  return { logs, loading, error, refresh: fetch }
}
