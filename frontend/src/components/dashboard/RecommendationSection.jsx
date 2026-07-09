import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import EmptyState from './EmptyState'
import { ExternalLink, Sparkles } from 'lucide-react'

export default function RecommendationSection({ recommendations = [] }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <EmptyState
        title="Aucune recommandation pour le moment"
        description="Complétez votre profil ou démarrez une conversation avec le chatbot pour obtenir des recommandations d'aides adaptées."
        icon={Sparkles}
      />
    )
  }

  const handleConsult = (url) => {
    if (url) {
      window.open(url, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {recommendations.map((aid) => {
        // Fallback pour l'image
        const imageSrc = aid.image_url || 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500&auto=format&fit=crop&q=60'

        return (
          <Card
            key={aid.aide_id}
            className="group flex flex-col overflow-hidden border-border/60 bg-white shadow-xs transition-all duration-300 hover:shadow-md hover:translate-y-[-4px]"
          >
            {/* Image / Gradient Header */}
            <div className="relative h-44 w-full overflow-hidden bg-muted">
              <img
                src={imageSrc}
                alt={aid.titre}
                className="size-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
              
              {/* Badge de catégorie ou type d'aide */}
              {aid.type_aide && (
                <span className="absolute top-3 left-3 rounded-full bg-white/90 px-2.5 py-1 text-[10px] font-semibold text-[#2963E8] shadow-xs backdrop-blur-xs">
                  {aid.type_aide}
                </span>
              )}

              {/* Score de matching si présent */}
              {aid.score_matching && (
                <span className="absolute top-3 right-3 flex items-center gap-1 rounded-full bg-amber-500/90 px-2.5 py-1 text-[10px] font-bold text-white shadow-xs">
                  <Sparkles className="size-3" />
                  {aid.score_matching}%
                </span>
              )}
            </div>

            {/* Contenu */}
            <CardContent className="flex flex-1 flex-col gap-3 p-5">
              <div className="space-y-1">
                <h4 className="line-clamp-2 text-sm font-bold leading-tight text-foreground transition-colors group-hover:text-[#2963E8]">
                  {aid.titre}
                </h4>
                {aid.region_cible && (
                  <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                    {aid.region_cible}
                  </p>
                )}
              </div>

              <p className="line-clamp-3 text-xs leading-relaxed text-muted-foreground">
                {aid.description || 'Aucune description disponible pour cette aide.'}
              </p>

              {/* Bouton Consulter */}
              <div className="mt-auto pt-4">
                <Button
                  onClick={() => handleConsult(aid.url_officielle)}
                  className="w-full bg-[#2963E8] hover:bg-[#1e52c7] text-white rounded-lg text-xs font-semibold"
                  disabled={!aid.url_officielle}
                >
                  Consulter
                  <ExternalLink className="ml-1.5 size-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
