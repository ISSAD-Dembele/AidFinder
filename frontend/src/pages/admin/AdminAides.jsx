import { useState, useMemo } from 'react'
import {
  FileText, Search, RefreshCw, Edit2, Trash2, CheckCircle, XCircle,
  ChevronLeft, ChevronRight, Plus, X, Save,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import useAdminAides from '@/src/hooks/useAdminAides'
import { AdminTableSkeleton } from '@/src/components/admin/AdminSkeletons'
import AdminEmptyState from '@/src/components/admin/AdminEmptyState'
import AdminErrorState from '@/src/components/admin/AdminErrorState'
import { formatLocalDate } from '@/src/utils/date'
import { useToast } from '@/src/contexts/ToastContext'

const PAGE_SIZE = 10

/* ─────────────────────────────────────────────────────────────── */
/*  Badge Statut                                                    */
/* ─────────────────────────────────────────────────────────────── */

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

/* ─────────────────────────────────────────────────────────────── */
/*  Modal Formulaire Créer / Modifier                               */
/* ─────────────────────────────────────────────────────────────── */

const EMPTY_FORM = {
  titre: '',
  description: '',
  type_aide: '',
  region_cible: '',
  url_officielle: '',
  image_url: '',
  source_id: '',
  categorie_id: '',
  montant: '',
  age_min: '',
  age_max: '',
  niveau_etude_requis: '',
  statut_socio_pro_requis: '',
  est_active: true,
}

const REGIONS_FR = [
  'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Bretagne', 'Centre-Val de Loire',
  'Corse', 'Grand Est', 'Hauts-de-France', 'Île-de-France', 'Normandie',
  'Nouvelle-Aquitaine', 'Occitanie', 'Pays de la Loire', "Provence-Alpes-Côte d'Azur",
  'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte', 'National',
]

function AideFormModal({ aide, onClose, onSave, creating = false }) {
  const [form, setForm] = useState(
    aide
      ? {
          titre: aide.titre || '',
          description: aide.description || '',
          type_aide: aide.type_aide || '',
          region_cible: aide.region_cible || '',
          url_officielle: aide.url_officielle || '',
          image_url: aide.image_url || '',
          source_id: aide.source_id || '',
          categorie_id: aide.categorie_id || '',
          montant: aide.montant || '',
          age_min: aide.age_min || '',
          age_max: aide.age_max || '',
          niveau_etude_requis: aide.niveau_etude_requis || '',
          statut_socio_pro_requis: aide.statut_socio_pro_requis || '',
          est_active: aide.est_active !== false,
        }
      : EMPTY_FORM
  )
  const [saving, setSaving] = useState(false)

  const set = (field) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((prev) => ({ ...prev, [field]: val }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      // Nettoyage : convertir les champs numériques
      const payload = {
        ...form,
        source_id: form.source_id ? parseInt(form.source_id, 10) : null,
        categorie_id: form.categorie_id ? parseInt(form.categorie_id, 10) : null,
        montant: form.montant ? parseFloat(form.montant) : null,
        age_min: form.age_min ? parseInt(form.age_min, 10) : null,
        age_max: form.age_max ? parseInt(form.age_max, 10) : null,
      }
      await onSave(payload)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  const inputClass =
    'w-full rounded-lg border border-border bg-white px-3 py-2 text-sm outline-none focus:border-[#2963E8] focus:ring-2 focus:ring-[#2963E8]/20 transition-all'
  const labelClass = 'block text-xs font-semibold text-muted-foreground mb-1'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header fixe */}
        <div className="flex items-center justify-between border-b border-border/60 px-6 py-4 shrink-0">
          <h2 className="text-lg font-bold text-foreground">
            {creating ? 'Créer une aide' : 'Modifier l\'aide'}
          </h2>
          <button onClick={onClose} className="rounded-lg p-1 hover:bg-muted/50 text-muted-foreground">
            <X className="size-4" />
          </button>
        </div>

        {/* Corps scrollable */}
        <form onSubmit={handleSubmit} className="flex flex-col flex-1 min-h-0">
          <div className="overflow-y-auto p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {/* Titre */}
              <div className="col-span-2">
                <label className={labelClass}>Titre *</label>
                <input className={inputClass} value={form.titre} onChange={set('titre')} required placeholder="Nom de l'aide" />
              </div>

              {/* Description */}
              <div className="col-span-2">
                <label className={labelClass}>Description</label>
                <textarea
                  className={`${inputClass} resize-none`}
                  rows={3}
                  value={form.description}
                  onChange={set('description')}
                  placeholder="Description de l'aide..."
                />
              </div>

              {/* Type d'aide */}
              <div>
                <label className={labelClass}>Type d'aide</label>
                <input className={inputClass} value={form.type_aide} onChange={set('type_aide')} placeholder="Ex : Bourse, Subvention..." />
              </div>

              {/* Région */}
              <div>
                <label className={labelClass}>Région cible</label>
                <select className={inputClass} value={form.region_cible} onChange={set('region_cible')}>
                  <option value="">— Toutes régions —</option>
                  {REGIONS_FR.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>

              {/* Montant */}
              <div>
                <label className={labelClass}>Montant (€)</label>
                <input type="number" min={0} step={0.01} className={inputClass} value={form.montant} onChange={set('montant')} placeholder="0.00" />
              </div>

              {/* Âge min */}
              <div>
                <label className={labelClass}>Âge minimum</label>
                <input type="number" min={0} max={120} className={inputClass} value={form.age_min} onChange={set('age_min')} placeholder="0" />
              </div>

              {/* Âge max */}
              <div>
                <label className={labelClass}>Âge maximum</label>
                <input type="number" min={0} max={120} className={inputClass} value={form.age_max} onChange={set('age_max')} placeholder="99" />
              </div>

              {/* Niveau étude */}
              <div>
                <label className={labelClass}>Niveau d'étude requis</label>
                <input className={inputClass} value={form.niveau_etude_requis} onChange={set('niveau_etude_requis')} placeholder="Ex : Bac+2, Doctorat..." />
              </div>

              {/* Statut socio-pro */}
              <div>
                <label className={labelClass}>Statut socioprofessionnel requis</label>
                <input className={inputClass} value={form.statut_socio_pro_requis} onChange={set('statut_socio_pro_requis')} placeholder="Ex : Étudiant, Salarié..." />
              </div>

              {/* Source ID */}
              <div>
                <label className={labelClass}>ID Source</label>
                <input type="number" min={1} className={inputClass} value={form.source_id} onChange={set('source_id')} placeholder="1" />
              </div>

              {/* Catégorie ID */}
              <div>
                <label className={labelClass}>ID Catégorie</label>
                <input type="number" min={1} className={inputClass} value={form.categorie_id} onChange={set('categorie_id')} placeholder="1" />
              </div>

              {/* URL officielle */}
              <div className="col-span-2">
                <label className={labelClass}>URL officielle</label>
                <input type="url" className={inputClass} value={form.url_officielle} onChange={set('url_officielle')} placeholder="https://..." />
              </div>

              {/* Image URL */}
              <div className="col-span-2">
                <label className={labelClass}>URL de l'image</label>
                <input type="url" className={inputClass} value={form.image_url} onChange={set('image_url')} placeholder="https://..." />
              </div>

              {/* Statut actif */}
              <div className="col-span-2 flex items-center gap-3">
                <input
                  type="checkbox"
                  id="est_active"
                  checked={form.est_active}
                  onChange={set('est_active')}
                  className="size-4 rounded border-border accent-[#2963E8]"
                />
                <label htmlFor="est_active" className="text-sm text-foreground cursor-pointer">
                  Aide active (visible dans les recommandations)
                </label>
              </div>
            </div>
          </div>

          {/* Footer fixe */}
          <div className="border-t border-border/60 px-6 py-4 flex justify-end gap-3 shrink-0">
            <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
              Annuler
            </Button>
            <Button
              type="submit"
              disabled={saving}
              className="gap-2 bg-[#2963E8] hover:bg-[#1e52c7] text-white"
            >
              {saving ? <RefreshCw className="size-4 animate-spin" /> : <Save className="size-4" />}
              {creating ? 'Créer' : 'Enregistrer'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────── */
/*  Page principale                                                 */
/* ─────────────────────────────────────────────────────────────── */

export default function AdminAides() {
  const { aides, loading, error, refresh, activateAide, deactivateAide, deleteAide, updateAide, createAide } = useAdminAides()
  const { showToast } = useToast()
  const [search, setSearch] = useState('')
  const [filterCategorie, setFilterCategorie] = useState('')
  const [filterRegion, setFilterRegion] = useState('')
  const [page, setPage] = useState(1)
  const [actionLoading, setActionLoading] = useState(null)
  const [editAide, setEditAide] = useState(null)
  const [showCreate, setShowCreate] = useState(false)

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

  const handleToggleActive = async (aide) => {
    setActionLoading(aide.aide_id)
    try {
      if (aide.est_active !== false) {
        await deactivateAide(aide.aide_id)
        showToast('Aide désactivée.', 'success')
      } else {
        await activateAide(aide.aide_id)
        showToast('Aide activée.', 'success')
      }
    } catch {
      showToast('Une erreur est survenue.', 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async (aide) => {
    if (!window.confirm(`Supprimer l'aide "${aide.titre}" ? Cette action est irréversible.`)) return
    setActionLoading(aide.aide_id)
    try {
      await deleteAide(aide.aide_id)
      showToast('Aide supprimée.', 'success')
    } catch {
      showToast('Impossible de supprimer cette aide.', 'error')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSaveEdit = async (payload) => {
    try {
      await updateAide(editAide.aide_id, payload)
      showToast('Aide mise à jour.', 'success')
    } catch {
      showToast('Impossible de modifier cette aide.', 'error')
      throw new Error('update failed')
    }
  }

  const handleCreate = async (payload) => {
    try {
      await createAide(payload)
      showToast('Aide créée avec succès.', 'success')
    } catch {
      showToast('Impossible de créer cette aide.', 'error')
      throw new Error('create failed')
    }
  }

  return (
    <div className="flex-1 bg-muted/20 px-4 py-6 sm:px-6 lg:px-8 lg:py-8 space-y-6">
      {/* Modals */}
      {editAide && (
        <AideFormModal
          aide={editAide}
          onClose={() => setEditAide(null)}
          onSave={handleSaveEdit}
        />
      )}
      {showCreate && (
        <AideFormModal
          aide={null}
          onClose={() => setShowCreate(false)}
          onSave={handleCreate}
          creating
        />
      )}

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
        <div className="flex gap-2">
          <Button onClick={refresh} variant="outline" size="sm" className="gap-2">
            <RefreshCw className="size-4" /> Actualiser
          </Button>
          <Button
            onClick={() => setShowCreate(true)}
            size="sm"
            className="gap-2 bg-[#2963E8] hover:bg-[#1e52c7] text-white"
          >
            <Plus className="size-4" /> Créer une aide
          </Button>
        </div>
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
                        {(aide.categorie || aide.type_aide) ? (
                          <span className="rounded-md bg-[#2963E8]/10 px-2 py-1 font-semibold text-[#2963E8]">
                            {aide.categorie || aide.type_aide}
                          </span>
                        ) : '—'}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">{aide.region_cible || '—'}</td>
                      <td className="px-4 py-3 text-muted-foreground text-xs">{formatLocalDate(aide.date_creation)}</td>
                      <td className="px-4 py-3">
                        <AideBadge active={aide.est_active !== false} />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost" size="icon"
                            onClick={() => setEditAide(aide)}
                            className="size-8 text-muted-foreground hover:text-violet-600 hover:bg-violet-50"
                            title="Modifier"
                          >
                            <Edit2 className="size-4" />
                          </Button>
                          {aide.est_active !== false ? (
                            <Button
                              variant="ghost" size="icon"
                              onClick={() => handleToggleActive(aide)}
                              disabled={actionLoading === aide.aide_id}
                              className="size-8 hover:text-orange-600 hover:bg-orange-50"
                              title="Désactiver"
                            >
                              <XCircle className="size-4" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost" size="icon"
                              onClick={() => handleToggleActive(aide)}
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
                  <div className="flex flex-wrap justify-end gap-2">
                    <Button variant="outline" size="sm" onClick={() => setEditAide(aide)} className="text-violet-600 border-violet-200 hover:bg-violet-50 text-xs gap-1">
                      <Edit2 className="size-3" /> Modifier
                    </Button>
                    {aide.est_active !== false ? (
                      <Button variant="outline" size="sm" onClick={() => handleToggleActive(aide)} disabled={actionLoading === aide.aide_id} className="text-orange-600 border-orange-200 hover:bg-orange-50 text-xs">
                        Désactiver
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => handleToggleActive(aide)} disabled={actionLoading === aide.aide_id} className="text-emerald-600 border-emerald-200 hover:bg-emerald-50 text-xs">
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
