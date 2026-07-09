import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import EmptyState from './EmptyState'
import { History, MessageSquare, Play } from 'lucide-react'

export default function HistorySection({ conversations = [], onContinueChat }) {
  if (!conversations || conversations.length === 0) {
    return (
      <EmptyState
        title="Aucune discussion"
        description="Vous n'avez pas encore de conversation. Cliquez sur Nouvelle discussion pour commencer."
        icon={History}
      />
    )
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    const date = new Date(dateStr)
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-3">
      {conversations.map((conv) => (
        <Card
          key={conv.historique_id}
          className="border-border/60 bg-white shadow-xs transition-all duration-200 hover:border-border hover:bg-muted/30"
        >
          <CardContent className="flex items-center justify-between gap-4 p-4">
            <div className="min-w-0 flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <MessageSquare className="size-4 shrink-0 text-[#2963E8]" />
                <h4 className="truncate text-sm font-semibold text-foreground">
                  {conv.titre_resume || 'Discussion sans titre'}
                </h4>
              </div>
              <p className="truncate text-xs text-muted-foreground pl-6">
                {conv.dernier_message || 'Démarrée le ' + formatDate(conv.date_creation)}
              </p>
              <p className="text-[10px] text-muted-foreground pl-6">
                Activité : {formatDate(conv.date_derniere_activite || conv.date_creation)}
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onContinueChat?.(conv)}
              className="shrink-0 border-border text-xs font-semibold hover:bg-[#2963E8] hover:text-white"
            >
              Continuer
              <Play className="ml-1 size-3 fill-current" />
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
