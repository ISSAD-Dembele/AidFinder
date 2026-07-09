import { cn } from '@/lib/utils'
import Logo from '@/src/components/Logo'
import HelpCard from '@/src/components/dashboard/HelpCard'
import SidebarNavItem from '@/src/components/dashboard/SidebarNavItem'

/** Sidebar du dashboard utilisateur */
export default function Sidebar({ basePath = '/dashboard', onDeactivate, onNavigate }) {
  return (
    <div className="flex h-full flex-col px-5 py-6 lg:py-8">
      <div className="mb-10 hidden lg:block">
        <Logo linkTo={basePath} />
      </div>

      <nav className="flex flex-col gap-1">
        {/* Nouveau Chat */}
        <SidebarNavItem
          to={`${basePath}?view=chat`}
          onClick={() => onNavigate?.()}
        >
          Nouveau Chat
        </SidebarNavItem>

        {/* Tableau de bord */}
        <SidebarNavItem
          to={basePath}
          end
          onClick={() => onNavigate?.()}
        >
          Tableau de bord
        </SidebarNavItem>

        {/* Profil */}
        <SidebarNavItem
          to={`${basePath}/profil`}
          onClick={() => onNavigate?.()}
        >
          Profil
        </SidebarNavItem>

        {/* Historiques */}
        <SidebarNavItem
          to={`${basePath}?scroll=history`}
          onClick={() => onNavigate?.()}
        >
          Historiques
        </SidebarNavItem>

        {/* Aides recommandées */}
        <SidebarNavItem
          to={`${basePath}?scroll=recommendations`}
          onClick={() => onNavigate?.()}
        >
          Aides recommandées
        </SidebarNavItem>

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

      <div className="mt-auto pt-8">
        <HelpCard />
      </div>
    </div>
  )
}
