import { Skeleton } from '@/components/ui/skeleton'

/** Skeleton pour une carte catégorie. */
export default function CategoryCardSkeleton() {
  return (
    <div className="rounded-xl border border-border/60 bg-card p-5 shadow-sm">
      <Skeleton className="mb-4 size-11 rounded-xl" />
      <Skeleton className="h-5 w-2/3" />
      <Skeleton className="mt-2 h-4 w-1/3" />
    </div>
  )
}
