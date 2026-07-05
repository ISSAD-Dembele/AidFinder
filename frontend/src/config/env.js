/**
 * Configuration centralisée de l'environnement frontend.
 *
 * Par défaut, l'URL de l'API utilise le même hôte que le navigateur
 * (localhost sur PC, IP locale sur téléphone). Surcharge possible via VITE_API_URL.
 */
export function getApiBaseUrl() {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/$/, '')
  }

  const port = import.meta.env.VITE_API_PORT || '8000'
  return `http://${window.location.hostname}:${port}`
}
