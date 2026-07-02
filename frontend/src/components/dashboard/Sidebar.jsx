import { Button } from '@/components/ui/button'
import Logo from '@/src/components/Logo'
import HelpCard from '@/src/components/dashboard/HelpCard'

const NAV_ITEMS = [
  { label: 'Historiques', href: '#', disabled: true },
  { label: 'Profil', href: '#', disabled: true },
  { label: 'Aides recommandées', href: '#', disabled: true },
]

/**
 * Sidebar du dashboard — reproduit la maquette Accueil_UI
 * avec navigation et bouton de désactivation du compte.
 */
export default function Sidebar({ onDeactivate, onNavigate }) {
  return (
    <div className="flex h-full flex-col px-5 py-6 lg:py-8">
      <div className="mb-10 hidden lg:block">
        <Logo linkTo="/dashboard" />
      </div>

      <Button
        className="mb-8 w-full bg-[#2963E8] py-5 text-sm font-medium hover:bg-[#1e52c7]"
        size="lg"
      >
        Nouveau Chat
      </Button>

      <nav className="flex flex-col gap-5">
        {NAV_ITEMS.map((item) => (
          <span
            key={item.label}
            className="cursor-default text-sm text-white/90 transition-colors hover:text-white"
          >
            {item.label}
          </span>
        ))}

        <button
          type="button"
          onClick={() => {
            onDeactivate()
            onNavigate?.()
          }}
          className="text-left text-sm text-white/90 transition-colors hover:text-white"
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
