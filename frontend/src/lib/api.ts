const API_BASE = "http://127.0.0.1:8000"

export interface Item {
  id: number
  content: string
  source_type: "note" | "url"
  source_url: string | null
  created_at: string
}

export interface SourceSnippet {
  item_id: number
  source_type: "note" | "url"
  source_url: string | null
  text: string
  score: number
}

export interface QueryResponse {
  answer: string
  sources: SourceSnippet[]
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    const message = Array.isArray(detail)
      ? detail.map((d: { msg: string }) => d.msg).join(", ")
      : detail || `Request failed with status ${response.status}`
    throw new Error(message)
  }
  return response.json()
}

export async function ingestNote(text: string): Promise<Item> {
  const response = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  })
  return handleResponse<Item>(response)
}

export async function ingestUrl(url: string): Promise<Item> {
  const response = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  })
  return handleResponse<Item>(response)
}

export async function fetchItems(): Promise<Item[]> {
  const response = await fetch(`${API_BASE}/items`)
  return handleResponse<Item[]>(response)
}

export async function askQuestion(question: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })
  return handleResponse<QueryResponse>(response)
}

export async function deleteItem(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/items/${id}`, { method: "DELETE" })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || `Request failed with status ${response.status}`)
  }
}