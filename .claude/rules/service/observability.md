# Observability

## OpenTelemetry Tracing

- Tracing setup lives in `observability/tracing.py`, called from the app lifespan handler
- `setup_tracing()` returns a `TracerProvider` (or `None` if disabled); shut it down in lifespan cleanup
- Apply `FastAPIInstrumentor.instrument_app(app)` at module scope (not in the lifespan); the middleware's internal tracer is a proxy that resolves the global `TracerProvider` at span-creation time, so it works even though `setup_tracing()` runs later in the lifespan
- Respect standard OTel environment variables (`OTEL_SDK_DISABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`); these do NOT use the app prefix
- `ConsoleSpanExporter` in development only; OTLP exporter gated on `OTEL_EXPORTER_OTLP_ENDPOINT` being set

### Custom Spans

- Create a module-level tracer: `tracer = trace.get_tracer(__name__)`
- Wrap service method logic in `with tracer.start_as_current_span("operation_name") as span:`
- Span names: `snake_case`, matching the operation (`create_bin`, `ingest_request`, `list_events_by_bin`)
- Span attributes: dot-separated namespaces (`bin.id`, `event.id`, `bins.count`, `error.type`)
- Include resource IDs, counts for lists, error types for failures
- Record errors: `span.set_status(StatusCode.ERROR, "description")` and raise; do NOT swallow exceptions
- Spans go on **service** methods (business logic), not controllers or routes

## Structured Logging

- Use `structlog.get_logger()` at module level in controllers and auth
- Log event names: `snake_case`, past tense for success (`bin_created`, `event_ingested`), noun for actions (`auth_failure`)
- Levels: `info` for success, `warning` for expected errors (auth failures), `error` for unexpected failures
- Include relevant context fields: resource IDs, counts, method, error reason
- Log at the **controller** layer (after service call succeeds), not in services

### Trace Context in Logs

- `add_trace_context` structlog processor injects `trace_id` and `span_id` from the active OTel span
- Place this processor in the chain before the renderer
- `structlog.contextvars.merge_contextvars` must be first in the processor chain for request-scoped context

## Prometheus Metrics

- Metrics setup lives in `observability/metrics.py`, called from the app lifespan handler
- Use `PrometheusMetricReader` with the default registry; HTTP server on a configurable port (`REQUEST_NEST_METRICS_PORT`)
- Define counters and histograms at module level via the OTel meter API: `meter = metrics.get_meter(__name__)`
- Naming: `snake_case`, domain-prefixed (e.g., `request_nest.events.ingested`, `request_nest.events.ingest_errors`, `request_nest.bins.created`)
- Counter attributes: use dot-separated namespaces matching span attributes (`error.type`, `http.method`)
- Every KPI identified in `docs/workflows-and-kpis.md` should have a corresponding metric
- Metrics go on **service** methods alongside spans (same layer as tracing)

## Workflow Documentation

- User workflows and KPIs are documented in `docs/workflows-and-kpis.md`
- Each KPI maps to a specific instrumentation point (service/controller method)
- Most KPIs have a Prometheus metric, a custom span, and a structured log event; some KPIs omit one channel where it doesn't add value
