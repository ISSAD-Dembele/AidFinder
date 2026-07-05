/** Retourne le chemin de base du dashboard selon le rôle */
export function getDashboardBasePath(role) {
  return role === 'administrateur' ? '/admin' : '/dashboard'
}

/** Vérifie si l'utilisateur est administrateur */
export function isAdmin(role) {
  return role === 'administrateur'
}
