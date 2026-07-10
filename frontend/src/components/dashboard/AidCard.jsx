import { motion } from 'framer-motion'
import { ExternalLink, Sparkles, CheckCircle2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import dashboardService from '@/src/services/dashboardService'

/**
 * Retourne les couleurs de la barre de compatibilité selon le score.
 */
function getCompatibilityColor(score) {
  if (score >= 80) return { bar: 'bg-emerald-500', badge: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' }
  if (score >= 50) return { bar: 'bg-amber-500', badge: 'bg-amber-50 text-amber-700 ring-amber-600/20' }
  return { bar: 'bg-red-400', badge: 'bg-red-50 text-red-700 ring-red-600/20' }
}

/**
 * Barre de compatibilité avec score et pourcentage.
 */
function CompatibilityBar({ score }) {
  if (score == null) return null
  const { bar, badge } = getCompatibilityColor(score)
  const pct = Math.min(100, Math.max(0, score))
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Compatibilité</span>
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ring-1 ${badge}`}>
          <Sparkles className="size-2.5" />
          {pct}%
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted/50">
        <motion.div
          className={`h-full rounded-full ${bar}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.3 }}
        />
      </div>
    </div>
  )
}

/**
 * Liste des raisons de recommandation.
 */
function ReasonsSection({ raisons }) {
  if (!raisons || raisons.length === 0) return null
  return (
    <div className="space-y-1.5">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        Pourquoi cette aide ?
      </p>
      <ul className="space-y-1">
        {raisons.slice(0, 3).map((reason, i) => (
          <li key={i} className="flex items-start gap-1.5">
            <CheckCircle2 className="mt-0.5 size-3 shrink-0 text-emerald-500" />
            <span className="text-xs leading-snug text-foreground/80">{reason}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

/**
 * Carte d'aide recommandée utilisée dans la DiscussionPage.
 * @param {object} props
 * @param {object} props.aid - Objet aide retourné par le backend
 * @param {number} props.index - Index pour le délai d'animation stagger
 */
export default function AidCard({ aid, index = 0 }) {
  const imageSrc =
    aid.image_url ||
    'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500&auto=format&fit=crop&q=60'

  const score = aid.compatibilite ?? aid.score_matching ?? null

  const handleConsult = async () => {
    if (!aid?.url_officielle) return
    try {
      await dashboardService.recordAidConsultation(aid.aide_id)
    } finally {
      window.open(aid.url_officielle, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut', delay: index * 0.1 }}
    >
      <Card className="group flex flex-col overflow-hidden border-border/60 bg-white shadow-xs transition-all duration-300 hover:shadow-md hover:-translate-y-1">
        {/* Image */}
        <div className="relative h-36 w-full overflow-hidden bg-muted">
          <img
            src={imageSrc}
            alt={aid.titre}
            className="size-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
          {aid.type_aide && (
            <span className="absolute top-2 left-2 rounded-full bg-white/90 px-2.5 py-1 text-[10px] font-semibold text-[#2963E8] shadow-xs backdrop-blur-xs">
              {aid.type_aide}
            </span>
          )}
        </div>

        {/* Contenu */}
        <CardContent className="flex flex-1 flex-col gap-3 p-4">
          <div className="space-y-0.5">
            <h4 className="line-clamp-2 text-sm font-bold leading-tight text-foreground transition-colors group-hover:text-[#2963E8]">
              {aid.titre}
            </h4>
            {aid.region_cible && (
              <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                {aid.region_cible}
              </p>
            )}
          </div>

          <p className="line-clamp-2 text-xs leading-relaxed text-muted-foreground">
            {aid.description || 'Aucune description disponible.'}
          </p>

          <CompatibilityBar score={score} />
          <ReasonsSection raisons={aid.raisons} />

          <div className="mt-auto pt-1">
            <Button
              onClick={handleConsult}
              disabled={!aid.url_officielle}
              className="w-full bg-[#2963E8] hover:bg-[#1e52c7] text-white rounded-lg text-xs font-semibold"
              id={`consult-aid-${aid.aide_id}`}
            >
              Consulter
              <ExternalLink className="ml-1.5 size-3.5" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
