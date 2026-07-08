import { Skeleton } from '@/components/ui/skeleton'
import { Card } from '@/components/ui/card'

/** Skeleton de chargement pour une carte d'aide. */
export default function AidCardSkeleton() {
  return (
    <Card className="overflow-hidden border-border/60 py-0 shadow-sm">
      <Skeleton className="aspect-[16/10] w-full rounded-none" />
      <div className="space-y-3 p-5">
        <Skeleton className="h-5 w-4/5" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/5" />
        <Skeleton className="mt-2 h-7 w-full" />
      </div>
    </Card>
  )
}
