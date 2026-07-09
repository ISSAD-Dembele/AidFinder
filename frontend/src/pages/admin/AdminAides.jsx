import { useState, useMemo } from 'react'
import { FileText, Search, RefreshCw, Edit2, Trash2, CheckCircle, XCircle, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import useAdminAides from '@/src/hooks/useAdminAides'
import { AdminTableSkeleton } from '@/src/components/admin/AdminSkeletons'
import AdminEmptyState from '@/src/components/admin/AdminEmptyState'
import AdminErrorState from '@/src/components/admin/AdminErrorState'

const PAGE_SIZE = 10

function AideBadge({ active }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-semibold ${
        active
          ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20'
          : 'bg-red-50 text-red-700 ring-1 ring-red-600/20'
      }`}
    >
      <span className={`size-1.5 rounded-full ${active ? 'bg-emerald-500' : 'bg-red-500'}`} />
      {active ? 'Active' : 'Inactive'}
    </span>
  )
}

/**
 * Page Gestion des Aides (Admin)
 */
export default function AdminAides() {
  const { aides, loading, error, refresh, activateAide, deactivateAide, deleteAide } = useAdminAides()
  const [search, setSearch] = useState('')
  const [filterCategorie, setFilterCategorie] = useState('')
  const [filterRegion, setFilterRegion] = useState('')
  const [page, setPage] = useState(1)
  const [actionLoading, setActionLoading] = useState(null)

  // Catégories et régions uniques pour les filtres
  const categories = useMemo(() => {
    const set = new Set(aides.map((a) => a.categorie || a.type_aide).filter(Boolean))
    return [...set].sort()
  }, [aides])

  const regions = useMemo(() => {
    const set = new Set(aides.map((a) => a.region_cible).filter(Boolean))
    return [...set].sort()
  }, [aides])

  const filtered = useMemo(() => {
    return aides.filter((a) => {
      const matchSearch =
        !search ||
        a.titre?.toLowerCase().includes(search.toLowerCase()) ||
        a.source?.toLowerCase().includes(search.toLowerCase())
      const matchCat = !filterCategorie || (a.categorie || a.type_aide) === filterCategorie
      const matchRegion = !filterRegion || a.region_cible === filterRegion
      return matchSearch && matchCat && matchRegion
    })
  }, [aides, search, filterCategorie, filterRegion])

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleAction = async (fn, aideId) => {
    setActionLoading(aideId)
    try { await fn(aideId) } catch { /* silent */ } finally { setActionLoading(null) }
  }

  const handleDelete = async (aide) => {
    if (!window.confirm(`Supprimer l'aide "${aide.titre}" ? Cette action est irréversible.`)) return
    setActionLoading(aide.aide_id)
    try { await deleteAide(aide.aide_id) } catch { /* silent */ } finally { setActionLoading(null) }
  }

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('fr-FR') : '—'

  return (
    <div className="flex-1 bg-muted/20 px-4 py-6 sm:px-6 lg:px-8 lg:py-8 space-y-6">
      {/* En-tête */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-bold text-foreground sm:text-2xl">
            <FileText className="size-6 text-[#2963E8]" />
            Gestion des aides
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {aides.length} aide{aides.length !== 1 ? 's' : ''} au total
          </p>
        </div>
        <Button onClick={refresh} variant="outline" size="sm" className="gap-2">
          <RefreshCw className="size-4" /> Actualiser
        </Button>
      </div>

      {/* Filtres */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Titre, source..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full rounded-lg border border-border bg-white py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[#2963E8] focus:ring-2 focus:ring-[#2963E8]/20 transition-all"
          />
        </div>
        <select
          value={filterCategorie}
          onChange={(e) => { setFilterCategorie(e.target.value); setPage(1) }}
          className="rounded-lg border border-border bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2963E8] focus:ring-2 focus:ring-[#2963E8]/20 transition-all"
        >
          <option value="">Toutes catégories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select
          value={filterRegion}
          onChange={(e) => { setFilterRegion(e.target.value); setPage(1) }}
          className="rounded-lg border border-border bg-white px-3 py-2.5 text-sm outline-none focus:border-[#2963E8] focus:ring-2 focus:ring-[#2963E8]/20 transition-all"
        >
          <option value="">Toutes régions</option>
          {regions.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>

      {/* Contenu */}
      {loading ? (
        <AdminTableSkeleton cols={6} rows={10} />
      ) : error ? (
        <AdminErrorState description="Impossible de charger les aides." onRetry={refresh} />
      ) : filtered.length === 0 ? (
        <AdminEmptyState
          icon={FileText}
          title="Aucune aide trouvée"
          description="Aucune aide ne correspond à vos filtres."
        />
      ) : (
        <>
          <div className="overflow-hidden rounded-xl border border-border/60 bg-white shadow-sm">
            {/* Desktop */}
            <div className="hidden lg:block overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/60 bg-muted/30">
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Image</th>
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Titre</th>
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Source</th>
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Catégorie</th>
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Région</th>
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Date</th>
                    <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">Statut</th>
                    <th className="px-4 py-3.5 text-right text-xs font-semibold uppercase tracking-wider text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {paginated.map((aide) => (
                    <tr key={aide.aide_id} className="hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3">
                        {aide.image_url ? (
                          <img src={aide.image_url} alt={aide.titre} className="size-12 rounded-lg object-cover border border-border" />
                        ) : (
                          <div className="size-12 rounded-lg bg-muted flex items-center justify-center">
                            <FileText className="size-5 text-muted-foreground" />
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <p className="max-w-xs line-clamp-2 font-semibold text-foreground">{aide.titre}</p>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">{aide.source || '—'}</td>
                      <td className="px-4 py-3 text-xs">
                        <span className="rounded-md bg-[#2963E8]/10 px-2 py-1 font-semibold text-[#2963E8]">
                          {aide.categorie || aide.type_aide || '—'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">{aide.region_cible || '—'}</td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">{formatDate(aide.date_creation)}</td>
                      <td className="px-4 py-3">
                        <AideBadge active={aide.est_active !== false} />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1">
                          {aide.est_active !== false ? (
                            <Button
                              variant="ghost" size="icon"
                              onClick={() => handleAction(deactivateAide, aide.aide_id)}
                              disabled={actionLoading === aide.aide_id}
                              className="size-8 hover:text-orange-600 hover:bg-orange-50"
                              title="Désactiver"
                            >
                              <XCircle className="size-4" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost" size="icon"
                              onClick={() => handleAction(activateAide, aide.aide_id)}
                              disabled={actionLoading === aide.aide_id}
                              className="size-8 hover:text-emerald-600 hover:bg-emerald-50"
                              title="Activer"
                            >
                              <CheckCircle className="size-4" />
                            </Button>
                          )}
                          <Button
                            variant="ghost" size="icon"
                            onClick={() => handleDelete(aide)}
                            disabled={actionLoading === aide.aide_id}
                            className="size-8 hover:text-destructive hover:bg-destructive/10"
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

            {/* Mobile */}
            <div className="lg:hidden divide-y divide-border/60">
              {paginated.map((aide) => (
                <div key={aide.aide_id} className="p-4 space-y-3">
                  <div className="flex items-start gap-3">
                    {aide.image_url ? (
                      <img src={aide.image_url} alt={aide.titre} className="size-14 rounded-lg object-cover border border-border shrink-0" />
                    ) : (
                      <div className="size-14 rounded-lg bg-muted flex items-center justify-center shrink-0">
                        <FileText className="size-5 text-muted-foreground" />
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="line-clamp-2 font-semibold text-foreground text-sm">{aide.titre}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">{aide.source || '—'}</p>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        <AideBadge active={aide.est_active !== false} />
                        {(aide.categorie || aide.type_aide) && (
                          <span className="rounded-md bg-[#2963E8]/10 px-2 py-0.5 text-[10px] font-semibold text-[#2963E8]">
                            {aide.categorie || aide.type_aide}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2">
                    {aide.est_active !== false ? (
                      <Button variant="outline" size="sm" onClick={() => handleAction(deactivateAide, aide.aide_id)} disabled={actionLoading === aide.aide_id} className="text-orange-600 border-orange-200 hover:bg-orange-50 text-xs">
                        Désactiver
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => handleAction(activateAide, aide.aide_id)} disabled={actionLoading === aide.aide_id} className="text-emerald-600 border-emerald-200 hover:bg-emerald-50 text-xs">
                        Activer
                      </Button>
                    )}
                    <Button variant="outline" size="sm" onClick={() => handleDelete(aide)} disabled={actionLoading === aide.aide_id} className="text-destructive border-red-200 hover:bg-red-50 text-xs">
                      Supprimer
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, filtered.length)} sur {filtered.length}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline" size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="gap-1"
                >
                  <ChevronLeft className="size-4" /> Préc.
                </Button>
                <Button
                  variant="outline" size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="gap-1"
                >
                  Suiv. <ChevronRight className="size-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
