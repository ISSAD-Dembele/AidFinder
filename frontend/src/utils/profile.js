/**
 * Vérifie si le profil contient les informations obligatoires
 * pour personnaliser les recommandations d'aides.
 */
export function isProfileComplete(profile) {
  if (!profile) return false
  return Boolean(profile.date_naissance && profile.region)
}
