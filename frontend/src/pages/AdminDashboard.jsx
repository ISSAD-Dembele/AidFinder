import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import ProfileAvatar from '@/src/components/profile/ProfileAvatar'
import { useProfile } from '@/src/contexts/ProfileContext'
import { useEffect, useState } from 'react'
import adminService from '@/src/services/admin'

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('fr-FR').format(new Date(value))
}

function buildBars(statistics) {
  const users = statistics?.evolution_utilisateurs?.slice(-7) || []
  const conversations = statistics?.evolution_conversations?.slice(-7) || []
  const max = Math.max(
    1,
    ...users.map((item) => item.total),
    ...conversations.map((item) => item.total)
  )
  return Array.from({ length: 7 }, (_, index) => ({
    users: Math.max(8, ((users[index]?.total || 0) / max) * 100),
    conversations: Math.max(8, ((conversations[index]?.total || 0) / max) * 100),
  }))
}

/** Dashboard administrateur — conforme à la maquette Dashbord_admin */
export default function AdminDashboard() {
  const { profile } = useProfile()
  const [dashboard, setDashboard] = useState(null)
  const [aides, setAides] = useState([])
  const [statistics, setStatistics] = useState(null)

  useEffect(() => {
    let mounted = true
    Promise.all([
      adminService.getDashboard(),
      adminService.getAides(),
      adminService.getStatistics(),
    ])
      .then(([dashboardData, aidesData, statisticsData]) => {
        if (!mounted) return
        setDashboard(dashboardData)
        setAides(aidesData.slice(0, 4))
        setStatistics(statisticsData)
      })
      .catch(() => {
        if (!mounted) return
        setDashboard(null)
        setAides([])
        setStatistics(null)
      })
    return () => {
      mounted = false
    }
  }, [])

  const stats = [
    { label: 'utilisateurs', value: dashboard?.total_utilisateurs ?? 0 },
    { label: 'conversations', value: dashboard?.total_conversations ?? 0 },
    { label: 'PDF téléchargés', value: dashboard?.total_pdf_exportes ?? 0 },
    { label: 'Aides publiées', value: dashboard?.total_aides ?? 0 },
  ]
  const bars = buildBars(statistics)

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
          {stats.map((stat) => (
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
              {aides.map((aide) => (
                <div key={aide.aide_id} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm font-semibold text-foreground">{aide.titre}</p>
                    <p className="text-xs text-muted-foreground">{aide.source || 'Source non renseignée'}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{formatDate(aide.date_creation)}</span>
                </div>
              ))}
              {aides.length === 0 && (
                <p className="py-4 text-sm text-muted-foreground">Aucune aide disponible.</p>
              )}
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
                {bars.map((bar, i) => (
                  <div key={i} className="flex flex-1 flex-col items-center gap-1">
                    <div
                      className="w-full rounded-t bg-purple-400/60"
                      style={{ height: `${bar.users}%` }}
                    />
                    <div
                      className="w-full rounded-t bg-sky-400/60"
                      style={{ height: `${bar.conversations}%` }}
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
