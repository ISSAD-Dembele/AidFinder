import { useState, useEffect, useCallback } from 'react'
import dashboardService from '@/src/services/dashboardService'

export default function useDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDashboard = useCallback(async () => {
    await Promise.resolve() // Defer rendering to avoid synchronous setState inside useEffect
    setLoading(true)
    setError(null)
    try {
      const [dashData, statsData] = await Promise.all([
        dashboardService.getDashboard(),
        dashboardService.getStats(),
      ])
      setData({
        ...dashData,
        nombre_conversations: statsData.nombre_conversations,
      })
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchDashboard()
  }, [fetchDashboard])

  return { data, loading, error, refresh: fetchDashboard }
}
