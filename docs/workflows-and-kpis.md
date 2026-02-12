# Core User Workflows and Application KPIs

This document defines the end-user workflows in request-nest and the application-level KPIs
used to measure workflow health. It serves as the foundation for instrumentation (OpenTelemetry
tracing and structlog enrichment) and Playwright e2e test coverage.

## User Workflows

### Workflow 1: Authenticate

**Description**: User provides an admin token to access the application.

**User Journey**:
1. User opens the application at `/`
2. App checks localStorage for `request_nest_admin_token`
3. If no token, `AuthPrompt` component displayed
4. User enters admin token and submits
5. Token saved to localStorage
6. App loads bins list (Workflow 3)

**Error Path**: If token is invalid, the first API call returns 401, token is cleared from
localStorage, and the user is re-prompted.

**API Endpoints**:
- No dedicated auth endpoint; authentication is validated on each API call via `Authorization: Bearer <token>` header

**Frontend Routes**: `/` (all routes show AuthPrompt when unauthenticated)

---

### Workflow 2: Create a Bin

**Description**: User creates a new disposable HTTP endpoint (bin) for capturing webhooks.

**User Journey**:
1. User clicks "New Bin" button on the bins list page
2. Modal opens with optional name field
3. User enters a name (optional) and submits
4. Bin created via API
5. Bins list refreshes with the new bin visible

**API Endpoints**:
- `POST /api/v1/bins` -- creates a new bin (requires auth)

**Frontend Routes**: `/` (BinsIndex page with CreateBinModal)

---

### Workflow 3: View Bins List

**Description**: Authenticated user views all existing bins.

**User Journey**:
1. User navigates to `/` (or is redirected after authentication)
2. Bins fetched from API
3. Bins displayed in a responsive table (desktop) or cards (mobile)
4. Each bin shows: name, ID, created date, ingest URL with copy button

**API Endpoints**:
- `GET /api/v1/bins` -- lists all bins (requires auth)

**Frontend Routes**: `/` (BinsIndex page)

---

### Workflow 4: Copy Ingest URL

**Description**: User copies a bin's ingest URL to share with external systems.

**User Journey**:
1. User views the bins list or bin detail page
2. Clicks the copy button next to the bin's ingest URL
3. URL copied to clipboard
4. Brief "Copied" feedback displayed

**API Endpoints**: None (client-side clipboard interaction)

**Frontend Routes**: `/` (BinsIndex), `/bins/:binId` (BinDetail)

---

### Workflow 5: Send Webhook to Bin (Ingest)

**Description**: External system sends an HTTP request to a bin's ingest URL, which is captured as an event.

**User Journey** (from the external system's perspective):
1. External system sends HTTP request to `/b/{bin_id}/{path}`
2. Request is captured: method, headers, query params, body, remote IP
3. Response returned: `{"ok": true, "event_id": "e_..."}`

**Error Paths**:
- Bin not found: 404 response
- Payload too large: 413 response (exceeds `max_body_size`)

**API Endpoints**:
- `ANY /b/{bin_id}` -- capture request at root path (public, no auth)
- `ANY /b/{bin_id}/{path:path}` -- capture request at sub-path (public, no auth)

**Frontend Routes**: None (backend-only interaction)

---

### Workflow 6: View Bin Detail and Events

**Description**: User views a specific bin's details and its captured events.

**User Journey**:
1. User clicks a bin row on the bins list page
2. Navigates to `/bins/{binId}`
3. Bin info and events fetched in parallel
4. Events displayed in table: timestamp, method badge, path, size
5. Empty state shown if no events captured yet

**API Endpoints**:
- `GET /api/v1/bins/{bin_id}` -- get bin details (requires auth)
- `GET /api/v1/bins/{bin_id}/events` -- list events for bin (requires auth)

**Frontend Routes**: `/bins/:binId` (BinDetail page)

---

### Workflow 7: Inspect Event Detail

**Description**: User inspects the full details of a captured HTTP request.

**User Journey**:
1. User clicks an event row on the bin detail page
2. Navigates to `/events/{eventId}`
3. Full event displayed: method badge, path, timestamp, remote IP
4. Sections displayed: query parameters, headers (with copy), body (JSON auto-formatted, with copy)
5. Breadcrumb navigation available back to bin

**API Endpoints**:
- `GET /api/v1/events/{event_id}` -- get event details (requires auth)

**Frontend Routes**: `/events/:eventId` (EventDetail page)

---

## Application-Level KPIs

These KPIs measure the health and usage of the application's core workflows. Each KPI maps
to a specific instrumentation point in the backend code.

| KPI | Description | Instrumentation Point | Workflow | Prometheus Metric | Span | Log Event |
|-----|-------------|----------------------|----------|-------------------|------|-----------|
| bins_created | Total number of bins created | `BinService.create_bin()` | Workflow 2 | `request_nest.bins.created` | `create_bin` | `bin_created` |
| events_ingested | Total webhook events captured | `EventService.ingest_request()` | Workflow 5 | `request_nest.events.ingested` | `ingest_request` | `event_ingested` |
| events_viewed | Event detail page API calls | `EventController.get_event()` | Workflow 7 | `request_nest.events.viewed` | `get_event` | `event_retrieved` |
| bins_listed | Bins list page API calls | `BinController.list_bins()` | Workflow 3 | `request_nest.bins.listed` | `list_bins` | `bins_listed` |
| bin_events_listed | Bin detail page API calls | `EventController.list_events_by_bin()` | Workflow 6 | `request_nest.bins.events_listed` | `list_events_by_bin` | `bin_events_listed` |
| ingest_errors | Failed ingestion attempts (404 bin not found, 413 payload too large) | `EventService.ingest_request()` | Workflow 5 | `request_nest.events.ingest_errors` | `ingest_request` (error status) | — |
| auth_failures | Failed authentication attempts (invalid or missing token) | `verify_admin_token()` | Workflow 1 | `request_nest.auth.failures` | — | `auth_failure` |

### KPI Instrumentation Strategy

Most KPIs are instrumented through three complementary mechanisms where applicable:

1. **Prometheus metrics**: Counters and histograms on service methods, enabling real-time
   dashboards and alerting via Grafana/Prometheus.

2. **OpenTelemetry spans**: Custom spans on the service/controller methods listed above,
   with attributes that enable filtering and aggregation (bin_id, event_id, method, error type).

3. **structlog events**: Enriched log events at each instrumentation point, with workflow
   context fields (bin_id, event_id, trace_id) that enable log-based queries and dashboard
   aggregation.

This approach ensures that KPIs can be tracked via metrics (Prometheus/Grafana), tracing
backends (Jaeger, Tempo), or log aggregation tools (Loki, CloudWatch Logs, Datadog Logs).
Not every KPI requires all three; for example, `ingest_errors` uses metrics and spans but
has no dedicated log event, while `auth_failures` uses logs but no custom span.
