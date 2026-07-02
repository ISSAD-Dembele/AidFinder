import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import Logo from '@/src/components/Logo'
import HelpCard from '@/src/components/dashboard/HelpCard'

const NAV_LINKS = [
  { label: 'Historiques', to: null },
  { label: 'Profil', to: '/dashboard/profil' },
  { label: 'Aides recommandées', to: null },
]

const navLinkClass = ({ isActive }) =>
  cn(
    'block rounded-lg px-3 py-2.5 text-sm transition-all duration-200',
    isActive
      ? 'bg-[#2963E8] text-white'
      : 'text-white/90 hover:bg-[#2963E8] hover:text-white'
  )

const disabledItemClass =
  'block rounded-lg px-3 py-2.5 text-sm text-white/90 transition-all duration-200 hover:bg-[#2963E8] hover:text-white cursor-default'

/**
 * Sidebar du dashboard — navigation avec NavLink pour l'état actif
 * et effet hover bleu sur chaque élément.
 */
export default function Sidebar({ onDeactivate, onNavigate }) {
  return (
    <div className="flex h-full flex-col px-5 py-6 lg:py-8">
      <div className="mb-10 hidden lg:block">
        <Logo linkTo="/dashboard" />
      </div>

      <NavLink
        to="/dashboard"
        end
        className={navLinkClass}
        onClick={() => onNavigate?.()}
      >
        Nouveau Chat
      </NavLink>

      <nav className="mt-5 flex flex-col gap-1">
        {NAV_LINKS.map((item) =>
          item.to ? (
            <NavLink
              key={item.label}
              to={item.to}
              className={navLinkClass}
              onClick={() => onNavigate?.()}
            >
              {item.label}
            </NavLink>
          ) : (
            <span key={item.label} className={disabledItemClass}>
              {item.label}
            </span>
          )
        )}

        <button
          type="button"
          onClick={() => {
            onDeactivate()
            onNavigate?.()
          }}
          className={cn(disabledItemClass, 'w-full text-left')}
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
