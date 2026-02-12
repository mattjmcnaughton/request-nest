"""OpenTelemetry metrics setup with Prometheus exporter."""

from __future__ import annotations

import os

import prometheus_client
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

from request_nest import __version__

__all__ = ["setup_metrics"]

DEFAULT_PROMETHEUS_PORT = 9464


def setup_metrics() -> MeterProvider | None:
    """Configure OpenTelemetry metrics with Prometheus exporter.

    Sets up a MeterProvider with a PrometheusMetricReader and starts an
    HTTP server on the configured port (default 9464) for Prometheus to scrape.

    Respects OTEL_SDK_DISABLED=true to disable metrics entirely.

    Returns:
        The configured MeterProvider, or None if metrics are disabled.
    """
    if os.environ.get("OTEL_SDK_DISABLED", "").lower() == "true":
        return None

    resource = Resource.create(
        {
            "service.name": "request-nest",
            "service.version": __version__,
        }
    )

    reader = PrometheusMetricReader()
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    port = int(os.environ.get("OTEL_EXPORTER_PROMETHEUS_PORT", DEFAULT_PROMETHEUS_PORT))
    prometheus_client.start_http_server(port)

    return provider
