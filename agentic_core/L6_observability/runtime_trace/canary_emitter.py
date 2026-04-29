"""Canary span emitter — synthetic OTel-shaped spans for the LIC canary route.

Produces the seven-span DAG required by ``canary.lic.v1``::

    u0.intake (L0)
      └─ l0.route (L0)
          └─ c0.retrieval (L1) — flows_to → pa.assemble
              └─ pa.assemble (L1)
                  └─ l2.execute (L2) — writes_to → uwg.commit
                      └─ exit.disposition (L2)
                          └─ uwg.commit (L4)

These spans are the OTel-shape input format expected by
:func:`agentic_core.L6_observability.otel_runtime_ingest.emit_spans_to_runtime_adg`.
The canary runner (``scripts/proof/run_runtime_trace_proof.py``) emits them,
ingests, reads them back via the snapshot store, and validates against the
contract.
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# L6 canary workflow emitter — synthetic LIC canary route spans.
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (
    ATTR_OPERATION_NAME,
    OPERATION_INVOKE_WORKFLOW,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_INVOKE_WORKFLOW
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import time
from typing import Any


def build_canary_lic_spans(
    *,
    trace_id: str,
    route_id: str = "lic.standard",
    base_time_ms: int | None = None,
) -> list[dict[str, Any]]:
    """Return the synthetic seven-span LIC canary trace.

    Args:
        trace_id: explicit OTel trace id; carried as an attribute on every span.
        route_id: the route identifier; carried as an attribute on every span.
        base_time_ms: optional Unix-ms time anchor for span timestamps.
            Defaults to current time. Span timestamps are spaced 10 ms apart.

    Returns:
        List of 7 OTel-shaped span dicts ready for ``emit_spans_to_runtime_adg``.
    """
    if base_time_ms is None:
        base_time_ms = int(time.time() * 1000)
    base_ns = base_time_ms * 1_000_000

    common_attrs = {"trace_id": trace_id, "route_id": route_id}

    def _span(
        *,
        span_id: str,
        name: str,
        kind: str,
        layer: str,
        component: str,
        parent_span_id: str,
        offset_ms: int,
        extra_attrs: dict[str, Any],
        status: str = "ok",
    ) -> dict[str, Any]:
        ts_ns = base_ns + offset_ms * 1_000_000
        return {
            "span_id": span_id,
            "trace_id": trace_id,
            "name": name,
            "kind": kind,
            "layer": layer,
            "component": component,
            "parent_span_id": parent_span_id,
            "status": status,
            "start_time_unix_nano": ts_ns,
            "end_time_unix_nano": ts_ns + 5_000_000,
            "attributes": {**common_attrs, **extra_attrs},
        }

    spans: list[dict[str, Any]] = [
        _span(
            span_id="canary-u0",
            name="u0.intake",
            kind="orchestrator",
            layer="L0",
            component="canary.intake",
            parent_span_id="",
            offset_ms=0,
            extra_attrs={"tier": "T2", "mission": "lic.canary"},
        ),
        _span(
            span_id="canary-l0",
            name="l0.route",
            kind="orchestrator",
            layer="L0",
            component="canary.router",
            parent_span_id="canary-u0",
            offset_ms=10,
            extra_attrs={"selected_route": route_id},
        ),
        _span(
            span_id="canary-c0",
            name="c0.retrieval",
            kind="cognitive",
            layer="L1",
            component="canary.retrieval",
            parent_span_id="canary-l0",
            offset_ms=20,
            extra_attrs={
                "retrieval_mode": "hybrid",
                "k": 5,
                # Triggers `dependency` runtime edge → `flows_to` contract edge.
                "depends_on": "canary-pa",
            },
        ),
        _span(
            span_id="canary-pa",
            name="pa.assemble",
            kind="cognitive",
            layer="L1",
            component="canary.prompt_assembly",
            parent_span_id="canary-c0",
            offset_ms=30,
            extra_attrs={"prompt_packet_id": "PP-canary-1"},
        ),
        _span(
            span_id="canary-l2",
            name="l2.execute",
            kind="action",
            layer="L2",
            component="canary.executor",
            parent_span_id="canary-pa",
            offset_ms=40,
            extra_attrs={
                "tool_call_count": 2,
                # Triggers `write_edge` runtime edge whose dst is the literal
                # string "uwg.commit" — the adapter will translate dst from
                # span_id to span name when matching, so set the dst to the
                # span_id ``canary-uwg`` so name lookup resolves to "uwg.commit".
                "writes_to": "canary-uwg",
            },
        ),
        _span(
            span_id="canary-exit",
            name="exit.disposition",
            kind="action",
            layer="L2",
            component="canary.exit",
            parent_span_id="canary-l2",
            offset_ms=50,
            extra_attrs={
                "disposition": "X3.PASS",
                "evidence_packet_id": "EV-canary-1",
            },
        ),
        _span(
            span_id="canary-uwg",
            name="uwg.commit",
            kind="action",
            layer="L4",
            component="canary.uwg",
            parent_span_id="canary-exit",
            offset_ms=60,
            extra_attrs={
                "evidence_hash": "canary-hash-deadbeef",
                "actor": "lic-canary",
                "reason": "exit.commit",
                "write": True,
                "uwg": True,
            },
        ),
    ]
    return spans


__all__ = ["build_canary_lic_spans"]
