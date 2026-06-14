"""Bridge: sealed runtime span records  →  L6 shadow ``raw_exhaust`` mapping.

This is the missing seam between *runtime tracing* (deterministic span records
appended by ``L6_system_learning.runtime_adg.runtime_span_emitter`` — shape:
``runtime.trace_root`` / ``L2.step.seal`` / ``exit.disposition`` etc.) and *L6
shadow observability* (``L6_observability.shadow_eval.ingest`` which consumes a
sealed ``raw_exhaust`` dict with top-level lineage keys + an ``events`` list).

It converts harvested span dicts into exactly the mapping shape that
:func:`agentic_core.L6_observability.shadow_eval.ingest.build_runtime_exhaust_bundle`
expects, so L6 can normalize evidence and decide eval-readiness **without ever
querying a live OTEL backend**.

Non-negotiable properties (process-map law):
  * **Pure.** No filesystem writes, no OTEL collector calls, no L4/UWG calls,
    no L6 imports. It only assembles and returns a dict.
  * **Post-boundary only.** ``runtime_boundary_crossed`` and
    ``exit_disposition_ref`` are caller-supplied and must reflect a run that has
    already crossed Exit — L6 ingest fails closed otherwise. This adapter does
    not invent them.
  * **Honest degradation.** When no trace evidence exists (no spans / no
    trace id), ``trace_root`` and ``events`` stay empty so L6 readiness fails
    honestly rather than being papered over.

L5 certification: when ``l5_certification_ref`` is omitted, the mapping leaves it
empty and L6 ingest substitutes its sanctioned gap-analysis sentinel
(``l5-cert-ref:MISSING``). This adapter never fabricates a real-looking cert ref.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

__all__ = ["build_l6_shadow_raw_exhaust", "layer_to_stage", "stage_order"]

# Canonical pipeline stages, mirroring
# ``L6_observability.shadow_eval.ingest.EXPECTED_STAGES``. Duplicated here as a
# literal (not imported) to keep this adapter free of any L6 dependency.
_EXPECTED_STAGES: tuple[str, ...] = ("U0", "L1", "L0", "C0", "PA", "L3", "L2", "EXIT", "UWG")
_STAGE_ORDER: dict[str, int] = {stage: idx for idx, stage in enumerate(_EXPECTED_STAGES)}

#: Layer-prefix → canonical stage (used only as a fallback after name/kind rules).
_LAYER_PREFIX_TO_STAGE: dict[str, str] = {"L0": "L0", "L1": "L1", "L2": "L2", "L3": "L3"}

_ERROR_STATUSES: frozenset[str] = frozenset({"error", "fail", "failed", "err"})


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def stage_order(stage: str) -> int:
    """Return the canonical execution-order index of *stage*, or ``-1``."""
    return _STAGE_ORDER.get(stage, -1)


def layer_to_stage(layer: str, name: str, kind: str = "") -> str:
    """Map a span's ``(layer, name, kind)`` to a canonical pipeline stage.

    Name/kind win for boundary stages (a ``exit.disposition`` span lives in
    ``L5_safety`` but is the ``EXIT`` stage); otherwise the L-layer prefix
    decides. Unknown shapes map to ``"UNKNOWN"``.
    """
    n = (name or "").lower()
    k = (kind or "").lower()
    if "exit" in n or k == "exit":
        return "EXIT"
    if "uwg" in n or "commit_request" in n:
        return "UWG"
    if n.startswith("u0") or "intake" in n:
        return "U0"
    if n.startswith("c0") or "retriev" in n or "grounding" in n:
        return "C0"
    prefix = (layer or "").strip().split("_", 1)[0].upper()
    return _LAYER_PREFIX_TO_STAGE.get(prefix, "UNKNOWN")


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _span_hash(span: Mapping[str, Any]) -> str:
    """Deterministic content hash of a span dict (canonical JSON, str-coerced)."""
    payload = json.dumps(span, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _span_to_event(span: Mapping[str, Any]) -> dict[str, Any]:
    """Convert one runtime span record to an L6-ingest event dict."""
    attrs = span.get("attributes") or {}
    span_id = str(span.get("span_id", ""))
    parent = str(span.get("parent_span_id", "") or "")
    status = str(span.get("status", "ok")).lower()
    return {
        "event_type": str(span.get("name", "unknown")),
        "stage": layer_to_stage(str(span.get("layer", "")), str(span.get("name", "")), str(span.get("kind", ""))),
        "source_ref": f"span:{span_id}",
        "payload_ref": f"span-payload:{span_id}",
        "trace_id": str(span.get("trace_id", "")),
        "span_id": span_id,
        "parent_span_id": parent,
        "provider_lane": (attrs.get("provider_lane") or attrs.get("llm.model") or attrs.get("model_id") or "unknown"),
        "latency_ms": _safe_float(span.get("duration_ms", 0.0)),
        "error_code": "SPAN_ERROR" if status in _ERROR_STATUSES else None,
        "reason_codes": _safe_list(attrs.get("reason_codes")),
        "step_id": attrs.get("step_id"),
        "attempt_id": attrs.get("attempt_id"),
        "model_id": attrs.get("model_id") or attrs.get("llm.model"),
        "tool_id": attrs.get("tool_id"),
        "token_count_in": _safe_int(attrs.get("token_count_in", 0)),
        "token_count_out": _safe_int(attrs.get("token_count_out", 0)),
        "cost_estimate": _safe_float(attrs.get("cost_estimate", 0.0)),
        "retry_count": _safe_int(attrs.get("retry_count", 0)),
        "repair_count": _safe_int(attrs.get("repair_count", 0)),
        "fallback_depth": _safe_int(attrs.get("fallback_depth", 0)),
        "prompt_hash": attrs.get("prompt_hash"),
        "context_hash": attrs.get("context_hash"),
        "artifact_digest": attrs.get("artifact_digest") or attrs.get("output_hash"),
        "eval_readiness_hint": str(attrs.get("eval_readiness_hint", "UNKNOWN")),
    }


def _span_to_source_manifest(span: Mapping[str, Any]) -> dict[str, Any]:
    """Convert one runtime span record to an L6-ingest source-manifest dict."""
    span_id = str(span.get("span_id", ""))
    parent = str(span.get("parent_span_id", "") or "")
    stage = layer_to_stage(str(span.get("layer", "")), str(span.get("name", "")), str(span.get("kind", "")))
    return {
        "source_type": "otel_span_record",
        "source_ref": f"span:{span_id}",
        "source_hash": _span_hash(span),
        "source_schema_version": "runtime-span-v1",
        "observed_stage": stage,
        "expected_stage_order": stage_order(stage),
        "lineage_parent_refs": [f"span:{parent}"] if parent else [],
        "lineage_child_refs": [],
        "completeness_status": "PRESENT",
        "trust_status": "SEALED_RUNTIME_EXHAUST",
        "gap_codes": [],
    }


def _resolve_trace_root(trace_root: str, spans: Sequence[Mapping[str, Any]]) -> str:
    """Prefer an explicit trace_root; else the first span's non-empty trace id."""
    if trace_root:
        return trace_root
    for span in spans:
        tid = str(span.get("trace_id", "") or "")
        if tid:
            return tid
    return ""


def build_l6_shadow_raw_exhaust(
    *,
    request_id: str,
    run_id: str,
    trace_root: str = "",
    completed_at: str = "",
    runtime_boundary_crossed: bool,
    exit_disposition_ref: str,
    spans: Sequence[Mapping[str, Any]],
    session_id: str = "",
    tenant_id: str = "",
    route_contract_ref: str | None = None,
    l1_plan_ref: str | None = None,
    c0_evidence_contract_refs: list[str] | None = None,
    prompt_envelope_refs: list[str] | None = None,
    l2_artifact_refs: list[str] | None = None,
    l3_workflow_package_ref: str | None = None,
    hitl_packet_refs: list[str] | None = None,
    uwg_receipt_refs: list[str] | None = None,
    policy_hash: str | None = None,
    blueprint_hash: str | None = None,
    replay_key: str | None = None,
    source_lineage_manifest_ref: str | None = None,
    artifacts: dict[str, Any] | None = None,
    source_exhaust: list[dict[str, Any]] | None = None,
    l5_certification_ref: str | None = None,
    route_id: str | None = None,
    outcome_class: str | None = None,
) -> dict[str, Any]:
    """Assemble the sealed ``raw_exhaust`` mapping L6 shadow ingest consumes.

    See module docstring for invariants. ``runtime_boundary_crossed`` /
    ``exit_disposition_ref`` are required (and must reflect a post-Exit run).
    ``completed_at`` defaults to now when omitted. Returns a plain dict.
    """
    span_list = list(spans or [])
    events = [_span_to_event(span) for span in span_list]
    sources = source_exhaust if source_exhaust is not None else [_span_to_source_manifest(span) for span in span_list]
    return {
        "request_id": request_id,
        "run_id": run_id,
        "session_id": session_id,
        "tenant_id": tenant_id,
        "trace_root": _resolve_trace_root(trace_root, span_list),
        "completed_at": completed_at or _utcnow(),
        "runtime_boundary_crossed": bool(runtime_boundary_crossed),
        "exit_disposition_ref": exit_disposition_ref,
        "events": events,
        "source_exhaust": sources,
        "route_contract_ref": route_contract_ref,
        "route_id": route_id,
        "l1_plan_ref": l1_plan_ref,
        "c0_evidence_contract_refs": list(c0_evidence_contract_refs or []),
        "prompt_envelope_refs": list(prompt_envelope_refs or []),
        "l2_artifact_refs": list(l2_artifact_refs or []),
        "l3_workflow_package_ref": l3_workflow_package_ref,
        "hitl_packet_refs": list(hitl_packet_refs or []),
        "uwg_receipt_refs": list(uwg_receipt_refs or []),
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "source_lineage_manifest_ref": source_lineage_manifest_ref,
        "artifacts": dict(artifacts or {}),
        # Empty -> L6 ingest applies its sanctioned MISSING sentinel; never fabricated.
        "l5_certification_ref": l5_certification_ref or "",
        "outcome_class": outcome_class or "unresolved_unknown",
    }
