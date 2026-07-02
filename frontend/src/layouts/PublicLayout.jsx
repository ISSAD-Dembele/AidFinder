import { Outlet } from 'react-router-dom'
import Navbar from '@/src/components/Navbar'

/** Layout pour les pages publiques avec navbar */
export default function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
