import { useState, useEffect, useCallback } from 'react'
import adminService from '@/src/services/admin'

export default function useAdminSources() {
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [scrapingId, setScrapingId] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await adminService.getSources()
      setSources(result)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const runScraping = useCallback(async (sourceId) => {
    setScrapingId(sourceId)
    try {
      const result = await adminService.runScraping(sourceId)
      // Refresh sources to get updated dernier_scraping
      await fetch()
      return result
    } finally {
      setScrapingId(null)
    }
  }, [fetch])

  return { sources, loading, error, refresh: fetch, runScraping, scrapingId }
}
