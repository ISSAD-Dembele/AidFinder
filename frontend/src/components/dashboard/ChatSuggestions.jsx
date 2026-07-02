import { Button } from '@/components/ui/button'

const SUGGESTIONS = [
  'Je cherche une aide pour mes études',
  "J'ai besoin d'aide pour mon logement",
  'Autres questions...',
]

/** Boutons de suggestions rapides pour le chatbot */
export default function ChatSuggestions({ onSelect }) {
  return (
    <div className="flex w-full max-w-2xl flex-col gap-3">
      {SUGGESTIONS.map((text) => (
        <Button
          key={text}
          variant="outline"
          className="h-auto justify-start rounded-xl border-border px-5 py-4 text-left text-sm font-normal text-foreground hover:bg-muted/50"
          onClick={() => onSelect?.(text)}
        >
          {text}
        </Button>
      ))}
    </div>
  )
}
