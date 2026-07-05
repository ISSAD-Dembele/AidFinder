import { cn } from '@/lib/utils'
import Logo from '@/src/components/Logo'
import SidebarNavItem from '@/src/components/dashboard/SidebarNavItem'
import { useAuth } from '@/src/contexts/AuthContext'

const NAV_LINKS = [
  { label: 'Utilisateurs', to: null },
  { label: 'Aides', to: null },
  { label: 'Statistiques', to: null },
  { label: 'Paramètres', to: 'profil' },
]

/** Sidebar du dashboard administrateur — conforme à la maquette Dashbord_admin */
export default function AdminSidebar({ basePath = '/admin', onDeactivate, onNavigate }) {
  const { logout } = useAuth()

  return (
    <div className="flex h-full flex-col px-5 py-6 lg:py-8">
      <div className="mb-10 hidden lg:block">
        <Logo linkTo={basePath} />
      </div>

      <nav className="flex flex-col gap-1">
        <SidebarNavItem to={basePath} end onClick={() => onNavigate?.()}>
          Tableau de bord
        </SidebarNavItem>

        {NAV_LINKS.map((item) => (
          <SidebarNavItem
            key={item.label}
            to={item.to ? `${basePath}/${item.to}` : null}
            disabled={!item.to}
            onClick={() => onNavigate?.()}
          >
            {item.label}
          </SidebarNavItem>
        ))}

        <button
          type="button"
          onClick={() => {
            logout()
            onNavigate?.()
          }}
          className={cn(
            'block w-full rounded-lg bg-transparent px-3 py-2.5 text-left text-sm text-white/90',
            'transition-all duration-200 hover:bg-[#2963E8] hover:text-white'
          )}
        >
          Déconnexion
        </button>

        <button
          type="button"
          onClick={() => {
            onDeactivate()
            onNavigate?.()
          }}
          className={cn(
            'block w-full rounded-lg bg-transparent px-3 py-2.5 text-left text-sm text-white/90',
            'transition-all duration-200 hover:bg-[#2963E8] hover:text-white'
          )}
        >
          Désactivation du compte
        </button>
      </nav>
    </div>
  )
}
