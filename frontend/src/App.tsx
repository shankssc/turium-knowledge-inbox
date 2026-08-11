import { useEffect, useState } from "react"

import { AddItemForm } from "@/components/AddItemForm"
import { ItemList } from "@/components/ItemList"
import { AskQuestion } from "@/components/AskQuestion"
import { AnswerView } from "@/components/AnswerView"
import { fetchItems, type Item, type QueryResponse } from "@/lib/api"

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [isLoadingItems, setIsLoadingItems] = useState(true)
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null)

  useEffect(() => {
    fetchItems()
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setIsLoadingItems(false))
  }, [])

  function handleItemAdded(item: Item) {
    setItems((prev) => [item, ...prev])
  }

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900">
      <div className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10">
        <header>
          <h1 className="text-xl font-semibold">AI Knowledge Inbox</h1>
          <p className="text-sm text-neutral-500">
            Save notes and links, then ask questions over everything you've saved.
          </p>
        </header>

        <AddItemForm onItemAdded={handleItemAdded} />

        <section>
          <h2 className="mb-2 text-sm font-medium text-neutral-700">Saved items</h2>
          <ItemList items={items} isLoading={isLoadingItems} />
        </section>

        <AskQuestion onAnswer={setQueryResult} />

        <AnswerView result={queryResult} />
      </div>
    </div>
  )
}

export default App