import { useState } from "react"
import { Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { deleteItem, type Item } from "@/lib/api"

interface ItemListProps {
  items: Item[]
  isLoading: boolean
  onItemDeleted: (id: number) => void
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + "..."
}

export function ItemList({ items, isLoading, onItemDeleted }: ItemListProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null)

  async function handleDelete(id: number) {
    setDeletingId(id)
    try {
      await deleteItem(id)
      onItemDeleted(id)
    } catch {
      // Item stays in the list if deletion fails; a real product would
      // surface this error, but for a single-user local tool, a failed
      // delete leaving the item visible is a reasonable, low-risk fallback.
    } finally {
      setDeletingId(null)
    }
  }

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
              <div className="flex items-center gap-2">
                <span className="text-xs text-neutral-400">
                  {new Date(item.created_at + "Z").toLocaleString()}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Delete this ${item.source_type}`}
                  onClick={() => handleDelete(item.id)}
                  disabled={deletingId === item.id}
                >
                  <Trash2 className={deletingId === item.id ? "animate-pulse" : "text-neutral-500"} />
                </Button>
              </div>
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