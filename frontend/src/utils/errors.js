/** Extrait le message d'erreur renvoyé par FastAPI depuis une erreur Axios */
export function getApiErrorMessage(error, fallback = 'Une erreur est survenue') {
  const detail = error?.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg).join(', ')
  }
  return fallback
}
