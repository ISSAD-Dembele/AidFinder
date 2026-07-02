import { Link } from 'react-router-dom'
import logo from '@/src/assets/images/logo.svg'

/** Logo AidFinder réutilisable avec lien optionnel vers la home */
export default function Logo({ className = '', linkTo = '/' }) {
  return (
    <Link to={linkTo} className={`inline-flex items-center ${className}`}>
      <img src={logo} alt="AidFinder" className="h-7 w-auto md:h-8" />
    </Link>
  )
}
