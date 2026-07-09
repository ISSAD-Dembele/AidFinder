import { useState, useEffect, useCallback } from 'react'
import dashboardService from '@/src/services/dashboardService'

/**
 * Hook pour récupérer les données du dashboard utilisateur.
 * Appelle uniquement /dashboard qui retourne déjà toutes les stats
 * (nombre_conversations inclus).
 */
export default function useDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDashboard = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const dashData = await dashboardService.getDashboard()
      setData(dashData)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDashboard()
  }, [fetchDashboard])

  return { data, loading, error, refresh: fetchDashboard }
}
