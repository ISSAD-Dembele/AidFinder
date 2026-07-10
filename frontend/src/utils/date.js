/**
 * Utilitaires de formatage de dates pour AidFinder.
 *
 * FastAPI sérialise toujours les datetime en UTC (avec suffixe 'Z' ou '+00:00').
 * Ces fonctions forcent la conversion vers le fuseau horaire local du navigateur
 * afin d'éviter tout décalage d'affichage.
 */

/**
 * Force une chaîne de date à être interprétée comme UTC.
 * Si la chaîne ne contient pas d'indicateur de timezone, on ajoute 'Z'.
 *
 * @param {string|null|undefined} dateStr
 * @returns {Date|null}
 */
function toUTCDate(dateStr) {
  if (!dateStr) return null
  try {
    // Si la date n'a pas de suffix timezone, elle est UTC → on ajoute 'Z'
    const normalized =
      /[Zz]$|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : dateStr + 'Z'
    const d = new Date(normalized)
    return isNaN(d.getTime()) ? null : d
  } catch {
    return null
  }
}

/**
 * Formate une date+heure UTC en heure locale du navigateur.
 * Affiche : "12 juil. 2025 à 11h31"
 *
 * @param {string|null|undefined} dateStr - Chaîne ISO UTC du backend
 * @returns {string} Date et heure formatées en local, ou '—' si invalide
 */
export function formatLocalDateTime(dateStr) {
  const d = toUTCDate(dateStr)
  if (!d) return '—'

  return d.toLocaleString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Formate uniquement la date (sans heure) en locale.
 * Affiche : "12 juil. 2025"
 *
 * @param {string|null|undefined} dateStr
 * @returns {string}
 */
export function formatLocalDate(dateStr) {
  const d = toUTCDate(dateStr)
  if (!d) return '—'

  return d.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

/**
 * Formate une date relative courte pour l'affichage compact.
 * Exemples : "Aujourd'hui à 11h31", "Hier à 09h15", "12 juil."
 *
 * @param {string|null|undefined} dateStr
 * @returns {string}
 */
export function formatRelativeDate(dateStr) {
  const d = toUTCDate(dateStr)
  if (!d) return '—'

  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const startOfYesterday = new Date(startOfToday)
  startOfYesterday.setDate(startOfYesterday.getDate() - 1)

  const timeStr = d.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  if (d >= startOfToday) {
    return `Aujourd'hui à ${timeStr}`
  }
  if (d >= startOfYesterday) {
    return `Hier à ${timeStr}`
  }

  return d.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  })
}
