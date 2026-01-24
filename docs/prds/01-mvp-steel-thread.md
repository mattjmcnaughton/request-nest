# PRD — request-nest MVP (Steel Thread)

## Goal
Deliver a minimal, end-to-end "steel thread":
- **Bins:** create + list + read
- **Events:** ingest + index + read (per bin)
Backed by **two Postgres tables** (bins and events) using SqlModel ORM.

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

## Data model (two Postgres tables)

### Table: `bins`
Columns:
- `id` TEXT PRIMARY KEY
- `name` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### Table: `events`
Columns:
- `id` TEXT PRIMARY KEY
- `bin_id` TEXT NOT NULL REFERENCES bins(id)
- `method` TEXT NOT NULL
- `path` TEXT NOT NULL
- `query_params` JSONB NOT NULL DEFAULT '{}'
- `headers` JSONB NOT NULL DEFAULT '{}'
- `body_b64` TEXT NOT NULL
- `remote_ip` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- `idx_events_bin_id` on `events(bin_id)`
- `idx_events_created_at` on `events(created_at)`

Notes:
- Using SqlModel for domain models with type-safe Pydantic validation
- Body stored as base64 to handle binary data
- Query params and headers stored as JSONB for flexibility

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
- All data persists in Postgres via bins and events tables
- Basic guardrails:
  - max body size (configurable)
  - reject unknown bin_id with 404

## Metrics (informal)
- P50 ingest latency < 50ms on local network
- Handles at least 10 req/sec without errors on modest hardware

---

## Implementation Tickets

This PRD has been broken down into 17 Linear tickets (all tagged with `for-ai` and `prd-01-steel-thread`):

### Dependency Graph

```
Foundation Layer:
  AGE-108 (Alembic Setup)
    ↓
  AGE-109 (Schema: Bins + Events Tables)
    ↓
  AGE-110 (DB Engine & Session Management)
    ↓
    ├──────────┬─────────┬──────────┐
    ↓          ↓         ↓          ↓
  AGE-111   AGE-112   AGE-122 (Test Fixtures)
  (Bin      (Event
  Model)    Model)
    ↓          ↓
    └──┬───────┘
       ↓
  AGE-113 (Bin API)
       ↓
       ├─────────────────┐
       ↓                 ↓
  AGE-114           AGE-115 (Ingest Endpoint) ⭐ CRITICAL PATH
  (Event API)            ↓
       ↓                 └──> AGE-119 (Metrics)
       ├─────────────────┤
       ↓                 ↓
  AGE-116          AGE-123 (E2E Tests) ⭐ VALIDATION
  (Bins Index)
       ↓
  AGE-117 (Bin Detail)
       ↓
  AGE-118 (Event Detail)

Infrastructure (parallel):
  AGE-120 (Container → GHCR)
    ↓
  AGE-121 (Helm Chart)

Documentation (end):
  (All tickets) → AGE-124 (Docs)
```

### Ticket List

| ID | Title | Dependencies |
|----|-------|--------------|
| AGE-108 | Setup Database Migrations with Alembic | None |
| AGE-109 | Create Bins and Events Table Schema | AGE-108 |
| AGE-110 | Add Database Engine and Session Management | AGE-109 |
| AGE-111 | Implement Bin Domain Model and Repository | AGE-110 |
| AGE-112 | Implement Event Domain Model and Repository | AGE-110 |
| AGE-113 | Implement Bin Service and Admin API Endpoints | AGE-111 |
| AGE-114 | Implement Event Service and Admin API Endpoints | AGE-112, AGE-113 |
| AGE-115 | Implement Ingest Endpoint (Public, No Auth) | AGE-111, AGE-112 |
| AGE-116 | Implement Bins Index Web Page (React + Tailwind) | AGE-113 |
| AGE-117 | Implement Bin Detail Web Page (React + Tailwind) | AGE-114, AGE-116 |
| AGE-118 | Implement Event Detail Web Page (React + Tailwind) | AGE-114 |
| AGE-119 | Instrument Core Business Metrics (OpenTelemetry) | AGE-115 |
| AGE-120 | Container Packaging and Publishing to GHCR | None |
| AGE-121 | Create Helm Chart for Deployment | AGE-120 |
| AGE-122 | Create Test Fixtures and Factories | AGE-110, AGE-111, AGE-112 |
| AGE-123 | End-to-End Testing of Steel Thread | AGE-113, AGE-114, AGE-115 |
| AGE-124 | Update Documentation for MVP Launch | All tickets |

### Critical Path

**AGE-108 → AGE-109 → AGE-110 → AGE-112 → AGE-115 → AGE-119 → AGE-124**

This represents the minimum sequence of tickets needed to deliver the core webhook capture functionality.

### Parallel Opportunities

- **Phase 1 (Foundation)**: AGE-108 → AGE-109 → AGE-110 → AGE-122 (sequential)
- **Phase 2 (Data Layer)**: AGE-111 (Bin) ‖ AGE-112 (Event) - parallel after AGE-110
- **Phase 3 (API Layer)**:
  - AGE-113 after AGE-111
  - AGE-114 after AGE-112 + AGE-113
  - AGE-115 after AGE-111 + AGE-112 (CRITICAL)
- **Phase 4 (UI & Infrastructure)**:
  - AGE-116, AGE-117, AGE-118 can overlap after their dependencies
  - AGE-119 after AGE-115
  - AGE-120 → AGE-121 can start anytime
- **Phase 5 (Validation)**: AGE-123 after AGE-113, AGE-114, AGE-115
- **Phase 6 (Documentation)**: AGE-124 after all
