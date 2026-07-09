import { Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/src/contexts/AuthContext'
import { ToastProvider } from '@/src/contexts/ToastContext'
import ProtectedRoute from '@/src/components/ProtectedRoute'
import PublicLayout from '@/src/layouts/PublicLayout'
import DashboardLayout from '@/src/layouts/DashboardLayout'
import AdminDashboardLayout from '@/src/layouts/AdminDashboardLayout'
import Home from '@/src/pages/Home'
import Register from '@/src/pages/Register'
import Login from '@/src/pages/Login'
import DashbordUI from '@/src/pages/DashbordUI'
import AdminDashboard from '@/src/pages/AdminDashboard'
import Profile from '@/src/pages/Profile'
import ChangePassword from '@/src/pages/ChangePassword'
import DiscussionPage from '@/src/pages/DiscussionPage'
import HistoriquePage from '@/src/pages/HistoriquePage'
import AidesRecommandeesPage from '@/src/pages/AidesRecommandeesPage'
import { getDashboardBasePath } from '@/src/utils/navigation'

/** Redirige les utilisateurs connectés vers leur dashboard selon le rôle */
function GuestRoute({ children }) {
  const { isAuthenticated, role, authLoading } = useAuth()

  if (authLoading) return null

  if (isAuthenticated && role) {
    return <Navigate to={getDashboardBasePath(role)} replace />
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

      {/* Dashboard utilisateur */}
      <Route
        element={
          <ProtectedRoute allowedRoles={['utilisateur']}>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<DashbordUI />} />
        <Route path="dashboard/profil" element={<Profile />} />
        <Route path="dashboard/changer-mot-de-passe" element={<ChangePassword />} />
        <Route path="dashboard/discussion" element={<DiscussionPage />} />
        <Route path="dashboard/discussion/:id" element={<DiscussionPage />} />
        <Route path="dashboard/historique" element={<HistoriquePage />} />
        <Route path="dashboard/aides-recommandees" element={<AidesRecommandeesPage />} />
      </Route>

      {/* Dashboard administrateur */}
      <Route
        element={
          <ProtectedRoute allowedRoles={['administrateur']}>
            <AdminDashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="admin/profil" element={<Profile />} />
        <Route path="admin/changer-mot-de-passe" element={<ChangePassword />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppRoutes />
      </ToastProvider>
    </AuthProvider>
  )
}
