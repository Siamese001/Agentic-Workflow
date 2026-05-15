"""DataRobot OpenTelemetry export (additive; does not replace runtime ADG ingest).

Enabled when ``DATAROBOT_API_TOKEN`` and ``DATAROBOT_ENTITY_ID`` are set.
``DATAROBOT_OTEL_ENDPOINT`` may be omitted; derived from ``DATAROBOT_ENDPOINT``.

Pattern source: DataRobot plugin skill ``datarobot-external-agent-monitoring``.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

_CONFIGURED = False


def is_datarobot_export_enabled() -> bool:
    """True when required DataRobot OTel credentials are present."""
    return bool(os.environ.get("DATAROBOT_API_TOKEN")) and bool(
        os.environ.get("DATAROBOT_ENTITY_ID")
    )


def _build_dr_headers() -> dict[str, str]:
    api_key = os.environ.get("DATAROBOT_API_TOKEN", "")
    entity_id = os.environ.get("DATAROBOT_ENTITY_ID", "")
    if not api_key:
        logger.warning("DATAROBOT_API_TOKEN not set — DataRobot OTel export disabled")
    if not entity_id:
        logger.warning("DATAROBOT_ENTITY_ID not set — DataRobot OTel export disabled")
    return {
        "X-DataRobot-Entity-Id": entity_id,
        "X-DataRobot-Api-Key": api_key,
    }


def _get_endpoint() -> str:
    endpoint = os.environ.get("DATAROBOT_OTEL_ENDPOINT", "")
    if endpoint:
        return endpoint.rstrip("/")
    api_endpoint = os.environ.get("DATAROBOT_ENDPOINT", "")
    if api_endpoint:
        base = api_endpoint.rstrip("/")
        if base.endswith("/api/v2"):
            base = base[: -len("/api/v2")]
        return f"{base}/otel"
    return ""


def configure_datarobot_otel() -> bool:
    """Add DataRobot OTLP exporters alongside any existing OTel setup.

    Returns True when configuration ran; False when skipped (missing env or OTel SDK).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return True
    if not is_datarobot_export_enabled():
        return False

    headers = _build_dr_headers()
    endpoint = _get_endpoint()
    if not endpoint:
        logger.warning("DATAROBOT_OTEL_ENDPOINT not derivable — skipping DataRobot OTel")
        return False

    try:
        from opentelemetry import metrics, trace
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor
        from opentelemetry.sdk.metrics import Counter, Histogram, MeterProvider, ObservableCounter
        from opentelemetry.sdk.metrics.export import (
            AggregationTemporality,
            PeriodicExportingMetricReader,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    except ImportError as exc:
        logger.warning("OpenTelemetry SDK unavailable — DataRobot export skipped (%s)", exc)
        return False

    resource = Resource.create()

    dr_span_processor = SimpleSpanProcessor(
        OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", headers=headers)
    )
    existing_provider = trace.get_tracer_provider()
    if hasattr(existing_provider, "add_span_processor"):
        existing_provider.add_span_processor(dr_span_processor)
    else:
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(dr_span_processor)
        trace.set_tracer_provider(provider)

    log_exporter = OTLPLogExporter(endpoint=f"{endpoint}/v1/logs", headers=headers)
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logging.getLogger().addHandler(handler)

    preferred_temporality = {
        Counter: AggregationTemporality.DELTA,
        Histogram: AggregationTemporality.DELTA,
        ObservableCounter: AggregationTemporality.DELTA,
    }
    metric_exporter = OTLPMetricExporter(
        endpoint=f"{endpoint}/v1/metrics",
        headers=headers,
        preferred_temporality=preferred_temporality,
    )
    meter_provider = MeterProvider(
        metric_readers=[PeriodicExportingMetricReader(metric_exporter)],
        resource=resource,
    )
    metrics.set_meter_provider(meter_provider)

    _CONFIGURED = True
    logger.info("DataRobot OTel export configured (entity=%s)", headers.get("X-DataRobot-Entity-Id"))
    return True
