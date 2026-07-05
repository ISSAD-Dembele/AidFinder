import { User } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getProfilePhotoUrl } from '@/src/services/user'

/** Avatar par défaut moderne ou photo de profil */
export default function ProfileAvatar({ photoPath, name, className }) {
  const photoUrl = getProfilePhotoUrl(photoPath)

  return (
    <div
      className={cn(
        'flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-[#2963E8]/20 to-[#2963E8]/5 ring-2 ring-[#2963E8]/20',
        className
      )}
    >
      {photoUrl ? (
        <img src={photoUrl} alt={name ? `Photo de ${name}` : 'Photo de profil'} className="size-full object-cover" />
      ) : (
        <User className="size-1/2 text-[#2963E8]" />
      )}
    </div>
  )
}
