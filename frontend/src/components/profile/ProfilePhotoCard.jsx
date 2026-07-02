import { useRef } from 'react'
import { User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { getProfilePhotoUrl } from '@/src/services/user'

/** Carte photo de profil avec bouton d'upload */
export default function ProfilePhotoCard({ profile, onUpload, uploading }) {
  const inputRef = useRef(null)

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (file) await onUpload(file)
    e.target.value = ''
  }

  const photoUrl = getProfilePhotoUrl(profile?.photo_profil)

  return (
    <Card className="border-border/60 shadow-sm">
      <CardContent className="flex flex-col items-center gap-4 py-6 sm:flex-row sm:items-center sm:gap-6">
        <div className="flex size-24 shrink-0 items-center justify-center overflow-hidden rounded-full bg-muted">
          {photoUrl ? (
            <img src={photoUrl} alt="Photo de profil" className="size-full object-cover" />
          ) : (
            <User className="size-10 text-muted-foreground" />
          )}
        </div>
        <div className="text-center sm:text-left">
          <p className="font-semibold text-foreground">{profile?.nom}</p>
          <Button
            variant="outline"
            size="sm"
            className="mt-2"
            disabled={uploading}
            onClick={() => inputRef.current?.click()}
          >
            {uploading ? 'Envoi en cours...' : 'Modifier la photo'}
          </Button>
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
      </CardContent>
    </Card>
  )
}
