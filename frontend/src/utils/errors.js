/**
 * Extrait un message d'erreur lisible depuis une erreur Axios.
 * Différencie les erreurs réseau, timeout, serveur et réponses API.
 */
export function getApiErrorMessage(error, fallback = 'Une erreur est survenue') {
  if (!error?.response) {
    if (error?.code === 'ECONNABORTED' || error?.message?.toLowerCase().includes('timeout')) {
      return 'La requête a expiré. Vérifiez votre connexion réseau.'
    }
    if (error?.request) {
      return 'Impossible de contacter le serveur. Vérifiez que le backend est lancé et accessible depuis votre appareil.'
    }
    return 'Erreur réseau. Vérifiez votre connexion.'
  }

  const { status, data } = error.response

  if (status >= 500) {
    return 'Erreur serveur. Réessayez ultérieurement.'
  }

  const detail = data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg ?? String(d)).join(', ')
  }

  return fallback
}
