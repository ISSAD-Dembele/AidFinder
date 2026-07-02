import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/src/contexts/AuthContext'
import ProtectedRoute from '@/src/components/ProtectedRoute'
import PublicLayout from '@/src/layouts/PublicLayout'
import DashboardLayout from '@/src/layouts/DashboardLayout'
import Home from '@/src/pages/Home'
import Register from '@/src/pages/Register'
import Login from '@/src/pages/Login'
import DashbordUI from '@/src/pages/DashbordUI'

/** Redirige les utilisateurs connectés vers le dashboard */
function GuestRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route
          path="register"
          element={
            <GuestRoute>
              <Register />
            </GuestRoute>
          }
        />
        <Route
          path="login"
          element={
            <GuestRoute>
              <Login />
            </GuestRoute>
          }
        />
      </Route>

      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<DashbordUI />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
