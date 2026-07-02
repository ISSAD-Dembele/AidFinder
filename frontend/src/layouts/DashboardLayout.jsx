import { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import Logo from '@/src/components/Logo'
import Sidebar from '@/src/components/dashboard/Sidebar'
import ProfileCompletionDialog from '@/src/components/profile/ProfileCompletionDialog'
import { ProfileProvider, useProfile } from '@/src/contexts/ProfileContext'
import { useAuth } from '@/src/contexts/AuthContext'

function DashboardContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { deactivateAccount } = useAuth()
  const { loading, isProfileComplete } = useProfile()
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
    <div className="flex min-h-screen bg-white">
      <ProfileCompletionDialog />

      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Fermer le menu"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-[#1a2332] transition-transform duration-300 lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between px-5 lg:hidden">
          <Logo linkTo="/dashboard" />
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="text-white"
            aria-label="Fermer"
          >
            <X className="size-5" />
          </button>
        </div>
        <Sidebar onDeactivate={handleDeactivate} onNavigate={() => setSidebarOpen(false)} />
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center border-b border-border px-4 lg:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="mr-3 text-foreground"
            aria-label="Ouvrir le menu"
          >
            <Menu className="size-5" />
          </button>
          <Logo linkTo="/dashboard" />
        </header>

        <main
          className={`flex flex-1 flex-col transition-opacity duration-300 ${
            !loading && !isProfileComplete ? 'pointer-events-none opacity-40' : ''
          }`}
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}

/** Layout du dashboard avec sidebar responsive et complétion de profil */
export default function DashboardLayout() {
  return (
    <ProfileProvider>
      <DashboardContent />
    </ProfileProvider>
  )
}
