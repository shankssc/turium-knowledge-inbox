import { Card, CardContent } from "@/components/ui/card"
import type { Item } from "@/lib/api"

interface ItemListProps {
  items: Item[]
  isLoading: boolean
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + "..."
}

export function ItemList({ items, isLoading }: ItemListProps) {
  if (isLoading) {
    return <p className="text-sm text-neutral-500">Loading saved items...</p>
  }

  if (items.length === 0) {
    return (
      <p className="text-sm text-neutral-500">
        Nothing saved yet. Add a note or URL above to get started.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {items.map((item) => (
        <Card key={item.id}>
          <CardContent className="p-3">
            <div className="flex items-start justify-between gap-2">
              <span className="text-xs font-medium uppercase text-neutral-500">
                {item.source_type}
              </span>
              <span className="text-xs text-neutral-400">
                {new Date(item.created_at + "Z").toLocaleString()}
              </span>
            </div>
            {item.source_url && (
              <a
                href={item.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-neutral-500 underline break-all"
              >
                {item.source_url}
              </a>
            )}
            <p className="mt-1 text-sm">{truncate(item.content, 200)}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}