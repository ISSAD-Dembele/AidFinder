import { getApiBaseUrl } from '@/src/config/env'

/** Résout l'URL d'image d'une aide (absolue ou relative au backend). */
export function getAidImageUrl(imageUrl) {
  if (!imageUrl) return null
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }
  const base = getApiBaseUrl().replace(/\/$/, '')
  const path = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`
  return `${base}${path}`
}

/** Formate une date ISO en affichage français. */
export function formatFrenchDate(isoDate) {
  if (!isoDate) return '—'
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(isoDate))
}
