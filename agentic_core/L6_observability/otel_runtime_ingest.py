"""In-process helper that feeds OTel-shaped spans into the runtime ADG store.

W7.1 / P1.1 — closes the producer-coverage gap identified in §8 of the static-vs-
runtime ADG doctrine. Before this helper, the only ingest path was the external
MCP tool ``otel_mcp::otel_ingest_to_runtime_adg``; no in-process producer in
``agentic_core/L6_observability/`` or ``system_learning/`` emitted spans that
landed in the runtime ADG store.

Contract
--------
Producers (``heal_router_otel``, ``consensus_otel``, ``system_learning._tracing``)
construct OTel-shaped span dicts and call :func:`emit_span_to_runtime_adg` or
:func:`emit_spans_to_runtime_adg`. The helper materializes them into a
:class:`RuntimeADGSnapshot` and persists via the L4-sovereign
:class:`FileBackedRuntimeADGStore`.

This helper is the in-process mirror of ``OTelIngestService.ingest_to_runtime_adg``;
it exists so L6 producers do not have to shell out to the MCP server to land
their spans in the runtime ADG store.

Fail-safe
---------
All ingest calls are best-effort. Persistence failures are logged and surfaced
via the returned result dict but never raise — an observability emitter must
not take down the producer it is instrumenting.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
from system_learning.runtime_adg.store import FileBackedRuntimeADGStore

logger = logging.getLogger(__name__)

# Process-level singleton store. FileBackedRuntimeADGStore is content-addressable
# and idempotent, so a single instance shared across all producers is safe.
_STORE: FileBackedRuntimeADGStore | None = None
_MATERIALIZER: RuntimeADGMaterializer | None = None


def _get_store() -> FileBackedRuntimeADGStore:
    global _STORE
    if _STORE is None:
        _STORE = FileBackedRuntimeADGStore()
    return _STORE


def _get_materializer() -> RuntimeADGMaterializer:
    global _MATERIALIZER
    if _MATERIALIZER is None:
        _MATERIALIZER = RuntimeADGMaterializer()
    return _MATERIALIZER


def emit_spans_to_runtime_adg(
    spans: list[dict[str, Any]],
    *,
    mission: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Materialize ``spans`` and persist as a runtime ADG snapshot.

    Parameters
    ----------
    spans
        List of OTel-shaped span dicts. Each span MUST carry at minimum
        ``span_id``, ``name``, and either ``service_name`` or ``component``
        (the materializer tolerates either).
    mission
        Optional mission/trace label. Defaults to ``trace_id`` or a
        timestamp fallback.
    trace_id
        Optional explicit trace id for index lookup.

    Returns
    -------
    dict
        ``{"success": bool, "snapshot_id": str, "version_id": str,
           "spans_ingested": int, "error": str | None}``.
        Always returns a dict; never raises.
    """

    if not isinstance(spans, list) or not spans:
        return {
            "success": False,
            "error": "spans must be a non-empty list",
            "spans_ingested": 0,
        }

    resolved_mission = mission or trace_id or f"trace_{int(time.time())}"

    try:
        snapshot = _get_materializer().materialize(spans, mission=resolved_mission)
        version_id = _get_store().persist(snapshot)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        logger.error(
            "otel_runtime_ingest_failed",
            extra={"trace_id": trace_id, "mission": resolved_mission, "error": str(exc)},
        )
        return {
            "success": False,
            "error": str(exc),
            "spans_ingested": 0,
            "trace_id": trace_id,
        }

    result = {
        "success": True,
        "snapshot_id": snapshot.snapshot_id,
        "version_id": version_id,
        "spans_ingested": len(spans),
        "trace_id": trace_id,
        "mission": resolved_mission,
    }
    logger.info("otel_runtime_ingest_success", extra=result)
    return result


def emit_span_to_runtime_adg(
    span: dict[str, Any],
    *,
    mission: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Convenience single-span form of :func:`emit_spans_to_runtime_adg`."""
    return emit_spans_to_runtime_adg([span], mission=mission, trace_id=trace_id)


__all__ = ["emit_span_to_runtime_adg", "emit_spans_to_runtime_adg"]
