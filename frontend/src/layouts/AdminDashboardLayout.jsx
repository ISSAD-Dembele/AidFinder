import { useNavigate } from 'react-router-dom'
import AdminSidebar from '@/src/components/dashboard/AdminSidebar'
import DashboardShell from '@/src/components/dashboard/DashboardShell'
import { ProfileProvider } from '@/src/contexts/ProfileContext'
import { useAuth } from '@/src/contexts/AuthContext'

const BASE_PATH = '/admin'

function AdminDashboardContent() {
  const { deactivateAccount } = useAuth()
  const navigate = useNavigate()

  const handleDeactivate = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir désactiver votre compte ?')) return
    try {
      await deactivateAccount()
      navigate('/')
    } catch {
      // Erreur gérée par le composant appelant
    }
  }

  return (
    <DashboardShell
      basePath={BASE_PATH}
      sidebar={({ onNavigate }) => (
        <AdminSidebar
          basePath={BASE_PATH}
          onDeactivate={handleDeactivate}
          onNavigate={onNavigate}
        />
      )}
    />
  )
}

/** Layout du dashboard administrateur */
export default function AdminDashboardLayout() {
  return (
    <ProfileProvider>
      <AdminDashboardContent />
    </ProfileProvider>
  )
}
