# AI Knowledge Inbox

A minimal single-user app to save notes/URLs and ask questions over them via a simple RAG pipeline. Built for the Turium AI take-home assignment.

## What it does

- Save short text notes or URLs (page content is fetched and extracted server-side)
- Ask questions over everything you've saved
- Get an answer grounded only in your saved content, with cited source snippets
- Delete individual saved items

## Tech stack

- **Backend**: FastAPI (Python), SQLite (in-memory), `sentence-transformers` for local embeddings, Claude API (Anthropic) for answer generation
- **Frontend**: React + TypeScript (Vite), Tailwind CSS v4, shadcn/ui components (Radix primitives)

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Runs on `http://127.0.0.1:8000`. Confirm with `GET /health`.

The first request after startup will be noticeably slower than the rest — that's the local embedding model (`all-MiniLM-L6-v2`) downloading (first run only) and loading into memory.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`.

## API

| Method   | Path          | Description                                                               |
| -------- | ------------- | ------------------------------------------------------------------------- |
| `POST`   | `/ingest`     | Save a note (`{"text": "..."}`) or a URL (`{"url": "..."}`)               |
| `GET`    | `/items`      | List all saved items, most recent first                                   |
| `DELETE` | `/items/{id}` | Delete an item and its chunks                                             |
| `POST`   | `/query`      | Ask a question (`{"question": "..."}`), returns an answer + cited sources |

## Design decisions and tradeoffs

### Chunking strategy

Fixed-size character windows (500 chars, 75 char overlap), no sentence/paragraph awareness. This is the simplest strategy that still works reasonably well for short notes and article text, and it's content-agnostic — no need to detect language-specific sentence boundaries.

**Observed limitation, not just theoretical**: during testing, a 500+ character note got chunked mid-word (`"...difficult to scan.Key Elements of Effective..."` split with no space, and a later chunk truncated at `"...Cl"` instead of `"Clarity"`). This directly hurt retrieval quality — the chunk containing the most relevant content (a bullet list) scored below the similarity threshold and was excluded, so the answer came from a weaker, more general chunk instead. A sentence-aware or paragraph-aware splitter (e.g. splitting on `\n\n` first, falling back to character windows only for long paragraphs) would fix this, at the cost of more chunking logic to write and test. Given the scope and time box, I chose to document this rather than build it.

### Vector storage

Embeddings are stored as JSON-encoded float lists in a SQLite `TEXT` column (SQLite has no native vector type). At query time, all chunk vectors are loaded into a numpy array and compared via cosine similarity, in-memory, on every request — no dedicated vector database (Chroma, pgvector, Pinecone, etc.).

This is a deliberate choice for single-user, small-corpus scale: it avoids an extra service/dependency for a workload of maybe a few hundred chunks, and it's easy to reason about and debug (the data really is just rows in a table). It does not scale — see below.

### Embeddings: local and free, not a hosted API

Uses `sentence-transformers` (`all-MiniLM-L6-v2`) running locally on CPU, rather than a hosted embeddings API (OpenAI, Voyage, etc.) I chose a free local model over paying for a hosted one, since embedding quality on a small personal-notes corpus doesn't need to be state-of-the-art. Tradeoff: slower cold start (model load), and it pulls in PyTorch as a dependency — a noticeably heavier install than a pure API call would be.

### Why an in-memory database

No auth is implemented (per the assignment's scope), so there's no real access control on saved data. Rather than try to clear data on browser-tab-close (unreliable — there's no dependable signal from a closed tab to a long-running server process), the database is SQLite `:memory:`: it resets automatically on every server restart, and there's also a manual "Delete" action per item for the current session. A real persistence layer (file-backed SQLite, or Postgres) is a one-line change (`DATABASE_URL`) away when persistence across restarts is actually needed.

### No migration tooling (Alembic)

Schema is created via a single `CREATE TABLE IF NOT EXISTS` script run at startup, not a migrations framework like Alembic. This fits the current scope: one schema, defined once, with a database that resets on every restart anyway (see above) — there's no existing data to migrate _from_, so a migration tool would have nothing to do here. Reaching for Alembic now would mean maintaining a migrations directory to manage change against a database that doesn't persist changes in the first place.

This stops being true the moment the app moves to a persistent database (see "What I'd change for production"): at that point, schema changes need to happen against real user data without data loss, and ad hoc `ALTER TABLE` statements stop being safe or repeatable. Alembic (or an equivalent) would become necessary there specifically for versioned, reversible schema changes and backfills — the exact problems it's built for, and exactly the problems this project doesn't have yet.

### Retrieval filtering

Retrieval returns the top-4 chunks by cosine similarity, but only if they score at least `0.35`. Without this floor, low-relevance chunks were being shown in the UI as "sources" even when the LLM's answer clearly hadn't used them — which is misleading to the user about what actually informed the answer. `0.35` is a heuristic threshold tuned by inspecting real scores during testing (clearly-related pairs scored 0.5+, clearly-unrelated pairs scored under 0.3), not a formally derived value.

### Beyond the required endpoints: DELETE

The assignment specifies `POST /ingest`, `GET /items`, `POST /query`. I added `DELETE /items/{id}` because, without auth or any other way to remove a bad entry, a single mis-saved item (a malformed URL, a 403'd page) would otherwise persist for the rest of that server session with no recovery short of restarting and losing everything else too. It's a small, low-risk addition on infrastructure the app already had (`ON DELETE CASCADE` on the `chunks` table).

### What breaks at scale

- **Retrieval is O(n) per query** — cosine similarity against every stored chunk, recomputed from scratch each time. Fine for hundreds of chunks; degrades noticeably into the tens of thousands.
- **Single shared SQLite connection** — a consequence of using `:memory:` (each new connection to `:memory:` gets its own empty database, so the app holds one connection open for its whole lifetime). This means writes are effectively serialized; fine for one user, a real bottleneck the moment there's more than one concurrent writer.
- **URL content extraction is tag-stripping, not true content extraction** — pages whose navigation/chrome isn't wrapped in semantic `<nav>`/`<header>`/`<footer>` tags (seen during testing with a MyAnimeList page) leak site chrome into the stored content as noise. A proper readability-style extractor (e.g. `readability-lxml`) would fix this but adds a dependency.
- **Synchronous ingestion** — chunking and embedding happen inline within the `/ingest` request. Fine for short notes; a very large document or a slow/large URL fetch would make the request noticeably slow, since there's no background job queue.

### What I'd change for production

- Swap `:memory:` SQLite for a persistent, file-backed or hosted database (Postgres), with real user accounts and auth.
- Move to a dedicated vector store (pgvector if already on Postgres, or a managed option like Pinecone/Qdrant) once chunk counts outgrow in-memory cosine similarity.
- Move embedding generation off the request path into a background queue (Celery + Redis) so ingesting a large document doesn't block the response.
- Add a sentence/paragraph-aware chunker to fix the mid-word-splitting issue observed during testing.
- Add readability-based content extraction for URLs instead of tag-stripping.

## Testing approach

No automated test suite — for a minimal demo app with no CI pipeline, I prioritized time on the RAG pipeline and tradeoff write-ups over test infrastructure. Instead, every endpoint was manually verified against its happy path and realistic failure modes during development: empty/malformed input, unreachable URLs, non-200 and non-HTML URL responses, multi-chunk retrieval on long notes, and the zero-relevant-results fallback. In a longer-lived version of this project, `pytest` coverage for `chunking.py` and `retrieval.py` (both pure functions, no I/O) would be the first tests I'd add, since they're the cheapest to test and the most likely to have subtle bugs.

## Debuggability

- Structured JSON logging on all key events (`app_startup`, `item_ingested`, `item_deleted`, `query_answered`, `query_no_relevant_chunks`, plus warnings on URL fetch failures and LLM errors).
- Distinct, correct HTTP status codes throughout: `400` for bad input (empty fields, unreachable URLs), `404` for deleting a non-existent item, `502` for upstream failures (URL fetch timeout/error, LLM provider errors), `422` for request validation errors (via Pydantic).
