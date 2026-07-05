import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'

/**
 * Élément de navigation sidebar — fond bleu uniquement au survol ou si actif (NavLink).
 */
export default function SidebarNavItem({ to, end = false, children, onClick, disabled = false }) {
  if (disabled || !to) {
    return (
      <span
        className={cn(
          'block cursor-default rounded-lg bg-transparent px-3 py-2.5 text-sm text-white/90',
          'transition-all duration-200 hover:bg-[#2963E8] hover:text-white'
        )}
      >
        {children}
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
          'block rounded-lg px-3 py-2.5 text-sm transition-all duration-200',
          isActive
            ? 'bg-[#2963E8] text-white'
            : 'bg-transparent text-white/90 hover:bg-[#2963E8] hover:text-white'
        )
      }
    >
      {children}
    </NavLink>
  )
}
