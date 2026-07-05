import { Link } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import ProfileAvatar from '@/src/components/profile/ProfileAvatar'
import { useProfile } from '@/src/contexts/ProfileContext'

const STATS = [
  { label: 'utilisateurs', value: '888' },
  { label: 'conversations', value: '1008' },
  { label: 'PDF Téléchargées', value: '101' },
  { label: 'Aides publiés', value: '300' },
]

const RECENT_AIDES = [
  { title: "Bourses d'excellence 2024", source: "Ministère de l'enseignement", date: '12/05/2024' },
  { title: 'Aide au logement', source: 'Agence Nationale', date: '10/05/2024' },
  { title: 'Subvention agricole', source: 'Ministère de l\'agriculture', date: '08/05/2024' },
  { title: 'Prime à la naissance', source: 'Caisse Nationale', date: '05/05/2024' },
]

/** Dashboard administrateur — conforme à la maquette Dashbord_admin */
export default function AdminDashboard() {
  const { profile } = useProfile()

  return (
    <div className="flex-1 bg-muted/30">
      {/* En-tête desktop */}
      <header className="hidden items-center justify-between border-b border-border bg-white px-6 py-4 lg:flex">
        <h1 className="text-xl font-bold text-foreground">Tableau de bord</h1>
        <div className="flex items-center gap-3">
          <ProfileAvatar photoPath={profile?.photo_profil} name={profile?.nom} className="size-10" />
          <div className="text-right">
            <p className="text-sm font-semibold text-foreground">{profile?.nom || 'Admin'}</p>
            <p className="text-xs text-muted-foreground">Administrateur</p>
          </div>
        </div>
      </header>

      <div className="px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        {/* Titre mobile */}
        <h1 className="mb-6 text-xl font-bold text-foreground lg:hidden">Tableau de bord</h1>

        <div className="mb-8">
          <h2 className="text-lg font-bold text-foreground sm:text-xl">
            Bienvenue, Administrateur !
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Voici un aperçu général de la plateforme AidFinder.
          </p>
        </div>

        {/* Cartes statistiques */}
        <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {STATS.map((stat) => (
            <Card key={stat.label} className="border-border/60 shadow-sm">
              <CardContent className="py-5 text-center">
                <p className="text-xs text-muted-foreground capitalize sm:text-sm">{stat.label}</p>
                <p className="mt-1 text-2xl font-bold text-foreground sm:text-3xl">{stat.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Aides récentes */}
          <Card className="border-border/60 shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base">Aides récentes</CardTitle>
              <span className="cursor-default text-sm text-[#2963E8]">Voir détails</span>
            </CardHeader>
            <CardContent className="divide-y divide-border/60 p-0 px-6 pb-4">
              {RECENT_AIDES.map((aide) => (
                <div key={aide.title} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{aide.title}</p>
                    <p className="text-xs text-muted-foreground">{aide.source}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{aide.date}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Activités — placeholder graphique */}
          <Card className="border-border/60 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Activités du 7 derniers jours</CardTitle>
              <div className="flex gap-4 pt-2 text-xs">
                <span className="font-medium text-purple-600">Nouveaux utilisateurs</span>
                <span className="font-medium text-sky-500">Conversations</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex h-48 items-end justify-between gap-2 rounded-lg bg-muted/40 p-4">
                {[40, 65, 45, 80, 55, 90, 70].map((h, i) => (
                  <div key={i} className="flex flex-1 flex-col items-center gap-1">
                    <div
                      className="w-full rounded-t bg-purple-400/60"
                      style={{ height: `${h}%` }}
                    />
                    <div
                      className="w-full rounded-t bg-sky-400/60"
                      style={{ height: `${h * 0.7}%` }}
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
