import { useState, useEffect, useCallback } from 'react'
import dashboardService from '@/src/services/dashboardService'

export default function useRecentAids() {
  const [recentAids, setRecentAids] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRecentAids = useCallback(async () => {
    await Promise.resolve() // Defer rendering to avoid synchronous setState inside useEffect
    setLoading(true)
    setError(null)
    try {
      const res = await dashboardService.getRecentAids()
      setRecentAids(res)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchRecentAids()
  }, [fetchRecentAids])

  return { recentAids, loading, error, refresh: fetchRecentAids }
}
