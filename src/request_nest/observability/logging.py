"""Structured logging setup using structlog."""

from __future__ import annotations

import logging
from collections.abc import MutableMapping
from typing import Any

import structlog
from opentelemetry import trace

__all__ = ["setup_logging"]


def add_trace_context(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Add OpenTelemetry trace context to log events.

    Injects trace_id and span_id from the current active span so that
    log events can be correlated with distributed traces.

    Args:
        _logger: The wrapped logger object (unused, required by structlog processor interface).
        _method_name: The name of the log method called (unused, required by structlog processor interface).
        event_dict: The event dictionary to enrich.

    Returns:
        The enriched event dictionary.
    """
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging with unified JSON output.

    Routes both structlog and stdlib loggers through the same processor
    chain so all log output is JSON with trace context.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
    """
    # Shared processors applied to both structlog and stdlib log entries
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_trace_context,
    ]

    # Configure structlog: shared processors + handoff to stdlib
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Formatter that renders the final JSON output for all loggers
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
        foreign_pre_chain=shared_processors,
    )

    # Replace root logger handlers with our unified formatter
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))

    # Override uvicorn's loggers — they set propagate=False and attach
    # their own handlers before our lifespan runs, so clearing the root
    # logger alone doesn't affect them.
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.addHandler(handler)
        uv_logger.propagate = False
