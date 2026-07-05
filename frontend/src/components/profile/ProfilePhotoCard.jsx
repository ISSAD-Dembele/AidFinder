import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import ProfileAvatar from '@/src/components/profile/ProfileAvatar'

/** Carte photo de profil — upload, modification et suppression */
export default function ProfilePhotoCard({
  profile,
  onUpload,
  onDelete,
  uploading,
  deleting,
}) {
  const inputRef = useRef(null)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const hasPhoto = Boolean(profile?.photo_profil)

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (file) await onUpload(file)
    e.target.value = ''
  }

  const handleConfirmDelete = async () => {
    await onDelete()
    setConfirmOpen(false)
  }

  return (
    <>
      <Card className="border-border/60 shadow-sm">
        <CardContent className="flex flex-col items-center gap-4 py-6 sm:flex-row sm:items-center sm:gap-6">
          <ProfileAvatar
            photoPath={profile?.photo_profil}
            name={profile?.nom}
            className="size-24"
          />
          <div className="text-center sm:text-left">
            <p className="font-semibold text-foreground">{profile?.nom}</p>
            <div className="mt-2 flex flex-wrap justify-center gap-2 sm:justify-start">
              <Button
                variant="outline"
                size="sm"
                disabled={uploading || deleting}
                onClick={() => inputRef.current?.click()}
              >
                {uploading ? 'Envoi en cours...' : hasPhoto ? 'Modifier la photo' : 'Ajouter une photo'}
              </Button>
              {hasPhoto && (
                <Button
                  variant="outline"
                  size="sm"
                  disabled={uploading || deleting}
                  onClick={() => setConfirmOpen(true)}
                  className="text-destructive hover:text-destructive"
                >
                  {deleting ? 'Suppression...' : 'Supprimer la photo'}
                </Button>
              )}
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/heic"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>
        </CardContent>
      </Card>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Supprimer la photo de profil ?</DialogTitle>
            <DialogDescription>
              Cette action est réversible. Vous pourrez ajouter une nouvelle photo à tout moment.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>
              Annuler
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleting}
            >
              {deleting ? 'Suppression...' : 'Confirmer'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
