import { useState } from 'react'
import { Users, Eye, Edit2, UserCheck, UserX, Trash2, Search, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import useAdminUsers from '@/src/hooks/useAdminUsers'
import { AdminTableSkeleton } from '@/src/components/admin/AdminSkeletons'
import AdminEmptyState from '@/src/components/admin/AdminEmptyState'
import AdminErrorState from '@/src/components/admin/AdminErrorState'
import { getApiBaseUrl } from '@/src/config/env'

function UserAvatar({ user }) {
  const initials = user.nom
    ? user.nom.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '?'

  if (user.photo_profil) {
    return (
      <img
        src={`${getApiBaseUrl()}${user.photo_profil}`}
        alt={user.nom}
        className="size-10 rounded-full object-cover border border-border"
      />
    )
  }
  return (
    <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-[#2963E8]/10 text-sm font-bold text-[#2963E8] border border-[#2963E8]/20">
      {initials}
    </div>
  )
}

function StatusBadge({ status }) {
  const isActive = status === 'actif'
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-semibold ${
        isActive
          ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20'
          : 'bg-red-50 text-red-700 ring-1 ring-red-600/20'
      }`}
    >
      <span className={`size-1.5 rounded-full ${isActive ? 'bg-emerald-500' : 'bg-red-500'}`} />
      {isActive ? 'Actif' : 'Désactivé'}
    </span>
  )
}

function UserDetailModal({ user, onClose }) {
  if (!user) return null
  const formatDate = (d) => d ? new Date(d).toLocaleDateString('fr-FR') : '—'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-4">
          <UserAvatar user={user} />
          <div>
            <h2 className="text-lg font-bold text-foreground">{user.nom}</h2>
            <p className="text-sm text-muted-foreground">{user.email}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          {[
            ['Rôle', user.role],
            ['Région', user.region || '—'],
            ['Niveau étude', user.niveau_etude || '—'],
            ['Statut pro', user.statut_socio_pro || '—'],
            ['Inscription', formatDate(user.date_creation)],
            ['Connexion', formatDate(user.date_derniere_connexion)],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg bg-muted/30 p-3">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
              <p className="mt-0.5 font-semibold text-foreground">{value}</p>
            </div>
          ))}
        </div>
        <Button onClick={onClose} className="w-full" variant="outline">Fermer</Button>
      </div>
    </div>
  )
}

/**
 * Page Gestion des Utilisateurs (Admin)
 */
export default function AdminUsers() {
  const { users, loading, error, refresh, activateUser, deactivateUser, deleteUser } = useAdminUsers()
  const [search, setSearch] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)

  const filtered = users.filter(
    (u) =>
      u.nom?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
  )

  const handleAction = async (fn, userId) => {
    setActionLoading(userId)
    try { await fn(userId) } catch { /* error handled silently */ } finally { setActionLoading(null) }
  }

  const handleDelete = async (userId, nom) => {
    if (!window.confirm(`Supprimer l'utilisateur "${nom}" ? Cette action est irréversible.`)) return
    setActionLoading(userId)
    try { await deleteUser(userId) } catch { /* error handled */ } finally { setActionLoading(null) }
  }

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('fr-FR') : '—'

  return (
    <div className="flex-1 bg-muted/20 px-4 py-6 sm:px-6 lg:px-8 lg:py-8 space-y-6">
      {selectedUser && <UserDetailModal user={selectedUser} onClose={() => setSelectedUser(null)} />}

      {/* En-tête */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-bold text-foreground sm:text-2xl">
            <Users className="size-6 text-[#2963E8]" />
            Gestion des utilisateurs
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {users.length} utilisateur{users.length !== 1 ? 's' : ''} au total
          </p>
        </div>
        <Button onClick={refresh} variant="outline" size="sm" className="gap-2">
          <RefreshCw className="size-4" /> Actualiser
        </Button>
      </div>

      {/* Barre de recherche */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Rechercher par nom ou email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-border bg-white py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[#2963E8] focus:ring-2 focus:ring-[#2963E8]/20 transition-all"
        />
      </div>

      {/* Contenu */}
      {loading ? (
        <AdminTableSkeleton cols={5} rows={8} />
      ) : error ? (
        <AdminErrorState
          description="Impossible de charger les utilisateurs."
          onRetry={refresh}
        />
      ) : filtered.length === 0 ? (
        <AdminEmptyState
          icon={Users}
          title="Aucun utilisateur trouvé"
          description={search ? 'Aucun résultat pour cette recherche.' : 'Aucun utilisateur enregistré.'}
        />
      ) : (
        /* Table desktop */
        <div className="overflow-hidden rounded-xl border border-border/60 bg-white shadow-sm">
          {/* Desktop view */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/60 bg-muted/30">
                  <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Utilisateur</th>
                  <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Email</th>
                  <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Statut</th>
                  <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Inscription</th>
                  <th className="px-6 py-3.5 text-right text-xs font-semibold uppercase tracking-wider text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filtered.map((user) => (
                  <tr key={user.user_id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <UserAvatar user={user} />
                        <span className="font-semibold text-foreground">{user.nom}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{user.email}</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={user.statut_compte} />
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{formatDate(user.date_creation)}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setSelectedUser(user)}
                          className="size-8 text-muted-foreground hover:text-[#2963E8] hover:bg-[#2963E8]/10"
                          title="Voir"
                        >
                          <Eye className="size-4" />
                        </Button>
                        {user.statut_compte === 'actif' ? (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleAction(deactivateUser, user.user_id)}
                            disabled={actionLoading === user.user_id}
                            className="size-8 text-muted-foreground hover:text-orange-600 hover:bg-orange-50"
                            title="Désactiver"
                          >
                            <UserX className="size-4" />
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleAction(activateUser, user.user_id)}
                            disabled={actionLoading === user.user_id}
                            className="size-8 text-muted-foreground hover:text-emerald-600 hover:bg-emerald-50"
                            title="Activer"
                          >
                            <UserCheck className="size-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(user.user_id, user.nom)}
                          disabled={actionLoading === user.user_id}
                          className="size-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                          title="Supprimer"
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile view — cartes */}
          <div className="md:hidden divide-y divide-border/60">
            {filtered.map((user) => (
              <div key={user.user_id} className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <UserAvatar user={user} />
                    <div>
                      <p className="font-semibold text-foreground">{user.nom}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  <StatusBadge status={user.statut_compte} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Inscrit le {formatDate(user.date_creation)}</span>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => setSelectedUser(user)} className="size-8">
                      <Eye className="size-4" />
                    </Button>
                    {user.statut_compte === 'actif' ? (
                      <Button variant="ghost" size="icon" onClick={() => handleAction(deactivateUser, user.user_id)} disabled={actionLoading === user.user_id} className="size-8 hover:text-orange-600">
                        <UserX className="size-4" />
                      </Button>
                    ) : (
                      <Button variant="ghost" size="icon" onClick={() => handleAction(activateUser, user.user_id)} disabled={actionLoading === user.user_id} className="size-8 hover:text-emerald-600">
                        <UserCheck className="size-4" />
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(user.user_id, user.nom)} disabled={actionLoading === user.user_id} className="size-8 hover:text-destructive">
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
