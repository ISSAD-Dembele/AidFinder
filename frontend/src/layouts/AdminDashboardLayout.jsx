import AdminSidebar from '@/src/components/dashboard/AdminSidebar'
import DashboardShell from '@/src/components/dashboard/DashboardShell'
import { ProfileProvider } from '@/src/contexts/ProfileContext'

const BASE_PATH = '/admin'

function AdminDashboardContent() {
  return (
    <DashboardShell
      basePath={BASE_PATH}
      sidebar={({ onNavigate }) => (
        <AdminSidebar
          basePath={BASE_PATH}
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
