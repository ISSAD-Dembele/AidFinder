import { FileText } from 'lucide-react'

export default function EmptyState({
  title = 'Aucune donnée disponible',
  description = 'Il n\'y a actuellement aucun élément à afficher.',
  icon: Icon = FileText,
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 bg-muted/20 px-6 py-12 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-muted/60 text-muted-foreground/80">
        <Icon className="size-6" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">{title}</h3>
      <p className="mx-auto mt-2 max-w-xs text-xs leading-relaxed text-muted-foreground">
        {description}
      </p>
    </div>
  )
}
