# PRD — request-nest MVP (Steel Thread)

## Goal
Deliver a minimal, end-to-end "steel thread":
- **Bins:** create + list + read
- **Events:** ingest + index + read (per bin)
Backed by **one Postgres table**.

## Scope
### In-scope
- Create bin
- List bins
- Ingest requests to a bin (store as events)
- List events for a bin
- Read a specific event

### Out-of-scope
- Replay
- Retention/TTL
- Redaction rules UI
- Multi-user/RBAC/OIDC (use a single admin token)
- Attachments / multipart parsing beyond raw body bytes

## Data model (single Postgres table)
Table: `request_bin_objects`

Columns:
- `id` TEXT PRIMARY KEY
- `type` TEXT NOT NULL  -- 'bin' | 'event'
- `bin_id` TEXT NULL    -- set for events
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `data` JSONB NOT NULL

Conventions:
- Bin rows: `type='bin'`, `bin_id=NULL`
- Event rows: `type='event'`, `bin_id=<bin id>`
- `data` holds the payload:
  - for bins: `{ "name": "...", "slug": "...?" }`
  - for events: `{ "method": "...", "path": "...", "query": {...}, "headers": {...}, "body_b64": "...", "remote_ip": "..." }`

## API
Auth: `Authorization: Bearer <REQUEST_NEST_ADMIN_TOKEN>` for admin endpoints.

### Bins
- `POST /api/bins`
  - body: `{ "name": "optional" }`
  - response: `{ "id": "b_xxx", "ingest_url": "https://host/b/b_xxx" }`

- `GET /api/bins`
  - response: list of `{ id, created_at, name? }`

- `GET /api/bins/:bin_id`
  - response: `{ id, created_at, name? }`

### Ingest
- `ANY /b/:bin_id/*`
  - no auth
  - stores an event row
  - response: `{ "ok": true, "event_id": "e_xxx" }`

### Events
- `GET /api/bins/:bin_id/events?limit=50`
  - response: list of `{ id, created_at, method, path, size_bytes }`

- `GET /api/events/:event_id`
  - response: full stored event payload

## UI (minimal)
- `/` Bins index
  - list bins
  - "Create bin" button

- `/bins/:bin_id` Bin detail
  - events table (newest first)
  - click event -> view detail

- `/events/:event_id` Event detail
  - method/path/time
  - headers (pretty JSON)
  - body (pretty JSON if possible, else raw)

## Acceptance criteria
- Can create a bin and see it in the bin list
- Can send `curl -X POST <ingest_url> -d '{"x":1}'` and see an event appear
- Can view event details, including headers and body
- All data persists in Postgres via the single table
- Basic guardrails:
  - max body size (configurable)
  - reject unknown bin_id with 404

## Metrics (informal)
- P50 ingest latency < 50ms on local network
- Handles at least 10 req/sec without errors on modest hardware
