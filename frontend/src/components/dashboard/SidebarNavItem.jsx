import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

/**
 * Élément de navigation sidebar — fond bleu uniquement au survol ou si actif (NavLink).
 * Supporte une icône Lucide optionnelle via la prop `icon`.
 */
export default function SidebarNavItem({ to, end = false, children, onClick, disabled = false, icon: Icon }) {
  const content = (
    <>
      {Icon && <Icon className="size-4 shrink-0" />}
      <span className="truncate">{children}</span>
    </>
  )

  const baseClass = 'flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm transition-all duration-200'

  if (disabled || !to) {
    return (
      <span
        className={cn(
          baseClass,
          'cursor-default bg-transparent text-white/50'
        )}
      >
        {content}
      </span>
    )
  }

  return (
    <NavLink
      to={to}
      end={end}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          baseClass,
          isActive
            ? 'bg-[#2963E8] text-white'
            : 'bg-transparent text-white/90 hover:bg-[#2963E8] hover:text-white'
        )
      }
    >
      {content}
    </NavLink>
  )
}
