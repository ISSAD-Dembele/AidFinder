import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/src/contexts/AuthContext'

/**
 * HOC de route — redirige vers /login si l'utilisateur n'est pas authentifié.
 */
export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}
