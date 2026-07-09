import { useState, useEffect, useCallback } from 'react'
import dashboardService from '@/src/services/dashboardService'

export default function useRecommendations() {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRecommendations = useCallback(async () => {
    await Promise.resolve() // Defer rendering to avoid synchronous setState inside useEffect
    setLoading(true)
    setError(null)
    try {
      const res = await dashboardService.getRecommendations()
      setRecommendations(res)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchRecommendations()
  }, [fetchRecommendations])

  return { recommendations, loading, error, refresh: fetchRecommendations }
}
