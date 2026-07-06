const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1', '::1'])

function isLocalHost(hostname) {
  return LOCAL_HOSTS.has(hostname?.toLowerCase())
}

function isLocalApiUrl(url) {
  try {
    return isLocalHost(new URL(url).hostname)
  } catch {
    return false
  }
}

/**
 * Configuration centralisée de l'environnement frontend.
 *
 * Par défaut, l'URL de l'API utilise le même hôte que le navigateur
 * (localhost sur PC, IP locale sur téléphone). Surcharge possible via VITE_API_URL.
 *
 * Si VITE_API_URL pointe vers localhost/127.0.0.1 alors que la page est ouverte
 * depuis une IP réseau (téléphone, tablette), la surcharge est ignorée pour
 * éviter d'appeler localhost sur l'appareil mobile au lieu du PC serveur.
 */
export function getApiBaseUrl() {
  const port = import.meta.env.VITE_API_PORT || '8000'
  const browserHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost'

  const viteApiUrl = import.meta.env.VITE_API_URL?.replace(/\/$/, '')
  if (viteApiUrl) {
    if (isLocalApiUrl(viteApiUrl) && !isLocalHost(browserHost)) {
      return `http://${browserHost}:${port}`
    }
    return viteApiUrl
  }

  return `http://${browserHost}:${port}`
}
