import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useProfile } from '@/src/contexts/ProfileContext'
import { useToast } from '@/src/contexts/ToastContext'
import ProfilePhotoCard from '@/src/components/profile/ProfilePhotoCard'
import ProfileInfoSection from '@/src/components/profile/ProfileInfoSection'
import { getApiErrorMessage } from '@/src/utils/errors'
import { getDashboardBasePath, isAdmin } from '@/src/utils/navigation'

/**
 * Page profil unique — partagée entre utilisateur et administrateur.
 * Le contenu s'adapte automatiquement selon profile.role.
 */
export default function Profile() {
  const { profile, loading, updateProfile, uploadPhoto, deletePhoto } = useProfile()
  const { showToast } = useToast()
  const [uploading, setUploading] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [photoError, setPhotoError] = useState('')

  const basePath = getDashboardBasePath(profile?.role)
  const adminUser = isAdmin(profile?.role)

  const handlePhotoUpload = async (file) => {
    setUploading(true)
    setPhotoError('')
    try {
      await uploadPhoto(file)
      showToast('Photo de profil mise à jour avec succès.')
    } catch (err) {
      setPhotoError(getApiErrorMessage(err, "Impossible d'envoyer la photo."))
    } finally {
      setUploading(false)
    }
  }

  const handlePhotoDelete = async () => {
    setDeleting(true)
    setPhotoError('')
    try {
      await deletePhoto()
      showToast('Photo de profil supprimée avec succès.')
    } catch (err) {
      setPhotoError(getApiErrorMessage(err, 'Impossible de supprimer la photo.'))
    } finally {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center p-8">
        <p className="text-sm text-muted-foreground">Chargement du profil...</p>
      </div>
    )
  }

  return (
    <div className="flex-1 px-4 py-6 sm:px-8 sm:py-8">
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Mon Profil</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {adminUser
              ? 'Gérez vos informations d\'administrateur'
              : 'Gérez vos informations personnelles'}
          </p>
        </div>

        {photoError && (
          <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {photoError}
          </div>
        )}

        <ProfilePhotoCard
          profile={profile}
          onUpload={handlePhotoUpload}
          onDelete={handlePhotoDelete}
          uploading={uploading}
          deleting={deleting}
        />

        <ProfileInfoSection profile={profile} onSave={updateProfile} />

        {adminUser && (
          <Card className="border-border/60 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Espace administrateur</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Vous disposez des droits d&apos;administration sur la plateforme AidFinder.
                Les fonctionnalités de gestion seront disponibles prochainement.
              </p>
            </CardContent>
          </Card>
        )}

        <Card className="border-border/60 shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Sécurité</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link
              to={`${basePath}/changer-mot-de-passe`}
              className="flex items-center justify-between rounded-lg border border-border/60 px-4 py-3 text-sm transition-colors hover:bg-muted/50"
            >
              <span className="font-medium">Mot de passe</span>
              <ChevronRight className="size-4 text-muted-foreground" />
            </Link>
            <Button variant="outline" className="w-full sm:w-auto" asChild>
              <Link to={`${basePath}/changer-mot-de-passe`}>Changer Mot de Passe</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
