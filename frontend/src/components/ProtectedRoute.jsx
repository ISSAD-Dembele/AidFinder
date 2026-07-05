import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/src/contexts/AuthContext'
import { getDashboardBasePath } from '@/src/utils/navigation'

/**
 * Protège les routes privées — vérifie l'authentification et optionnellement le rôle.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, role, authLoading } = useAuth()
  const location = useLocation()

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Chargement...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to={getDashboardBasePath(role)} replace />
  }

  return children
}
