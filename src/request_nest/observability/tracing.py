"""OpenTelemetry tracing setup."""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from request_nest import __version__

__all__ = ["setup_tracing"]


def setup_tracing(*, enable_console: bool = False) -> TracerProvider | None:
    """Configure OpenTelemetry tracing.

    Sets up a TracerProvider with an optional ConsoleSpanExporter for development
    and an optional OTLP exporter when OTEL_EXPORTER_OTLP_ENDPOINT is set.

    Respects OTEL_SDK_DISABLED=true to disable tracing entirely.

    Args:
        enable_console: Whether to add ConsoleSpanExporter (for development).

    Returns:
        The configured TracerProvider, or None if tracing is disabled.
    """
    if os.environ.get("OTEL_SDK_DISABLED", "").lower() == "true":
        return None

    resource = Resource.create(
        {
            "service.name": "request-nest",
            "service.version": __version__,
        }
    )

    provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint is configured
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
    elif enable_console:
        # Console exporter only when OTLP is not configured, to avoid
        # polluting stdout with multi-line span JSON alongside structured logs.
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return provider
