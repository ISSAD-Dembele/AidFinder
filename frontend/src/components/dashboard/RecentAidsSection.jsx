import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import EmptyState from './EmptyState'
import { Bookmark, ExternalLink } from 'lucide-react'
import dashboardService from '@/src/services/dashboardService'

export default function RecentAidsSection({ recentAids = [] }) {
  if (!recentAids || recentAids.length === 0) {
    return (
      <EmptyState
        title="Aucune aide consultée"
        description="Les aides que vous consultez s'afficheront ici."
        icon={Bookmark}
      />
    )
  }

  const handleConsult = async (aid) => {
    if (!aid?.url_officielle) {
      return
    }
    try {
      await dashboardService.recordAidConsultation(aid.aide_id)
    } finally {
      window.open(aid.url_officielle, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <div className="space-y-3">
      {recentAids.map((aid) => {
        const imageSrc = aid.image_url || 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=100&auto=format&fit=crop&q=60'

        return (
          <Card
            key={aid.aide_id}
            className="border-border/60 bg-white shadow-xs transition-all duration-200 hover:border-border hover:bg-muted/30"
          >
            <CardContent className="flex items-center gap-3 p-3">
              {/* Thumbnail */}
              <div className="relative size-12 shrink-0 overflow-hidden rounded-lg bg-muted">
                <img
                  src={imageSrc}
                  alt={aid.titre}
                  className="size-full object-cover"
                />
              </div>

              {/* Info */}
              <div className="min-w-0 flex-1 space-y-0.5">
                <h4 className="truncate text-xs font-bold text-foreground">
                  {aid.titre}
                </h4>
                {aid.type_aide && (
                  <span className="inline-block text-[10px] font-semibold text-[#2963E8]">
                    {aid.type_aide}
                  </span>
                )}
              </div>

              {/* Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleConsult(aid)}
                className="shrink-0 text-muted-foreground hover:bg-[#2963E8]/10 hover:text-[#2963E8]"
                disabled={!aid.url_officielle}
                aria-label="Consulter"
              >
                <ExternalLink className="size-4" />
              </Button>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
