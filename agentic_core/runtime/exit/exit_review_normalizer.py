"""AG-5 terminal normalization → v6 ExitReviewPacket."""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
from agentic_core.runtime.exit.exit_validation_types import AG5NormalizationError

__all__ = ["AG5NormalizationError", "normalize_ag5_terminal_input"]

_SOURCE_MAP: dict[str, SourceType] = {
    "RET_EXACT_CACHE": SourceType.RET_CACHE_EXACT,
    "RET_SEMANTIC_CACHE": SourceType.RET_CACHE_SEMANTIC,
    "RET_FALLBACK": SourceType.RET_FALLBACK,
    "SEALED_L2_ARTIFACT": SourceType.L2_SEALED_ARTIFACT,
    "SEALED_WORKFLOW_PACKAGE": SourceType.L3_WORKFLOW_PACKAGE,
    "RECLEARED_HITL_PACKET": SourceType.HITL_RECLEARED_PACKET,
    "APP_BINDING_COMPATIBILITY_PACKAGE": SourceType.APP_BINDING_COMPATIBILITY_PACKAGE,
}


def normalize_ag5_terminal_input(raw: Mapping[str, Any]) -> ExitReviewPacket:
    """Map an AG-5 terminal dict into the v6 ExitReviewPacket carrier."""
    st_raw = str(raw.get("source_type") or "").strip()
    mapped = _SOURCE_MAP.get(st_raw)
    if mapped is None:
        try:
            mapped = SourceType(st_raw)
        except ValueError as exc:
            raise AG5NormalizationError(f"unknown source_type {st_raw!r}") from exc

    route_contract = dict(raw.get("route_contract") or {})
    if not isinstance(route_contract, dict):
        route_contract = {}

    otel_raw = raw.get("otel_spans") or {}
    otel_spans = otel_raw if isinstance(otel_raw, dict) else {}

    exec_raw = raw.get("exec_trace") or {}
    exec_trace = exec_raw if isinstance(exec_raw, dict) else {}

    out_raw = raw.get("output") or {}
    output = out_raw if isinstance(out_raw, dict) else {}

    gc_raw = raw.get("grader_composition") or {}
    grader_composition = gc_raw if isinstance(gc_raw, dict) else {}

    return ExitReviewPacket(
        source_type=mapped,
        request_id=str(raw.get("request_id") or ""),
        run_id=str(raw.get("run_id") or ""),
        trace_root=str(raw.get("trace_root") or ""),
        route_id=str(raw.get("route_id") or ""),
        policy_hash=str(raw.get("policy_hash") or ""),
        blueprint_hash=str(raw.get("blueprint_hash") or ""),
        replay_key=str(raw.get("replay_key") or ""),
        route_contract=route_contract,
        terminal_class=str(raw.get("terminal_class") or ""),
        output=output,
        otel_spans=otel_spans,
        exec_trace=exec_trace,
        app_id=str(raw.get("app_id") or ""),
        task_class=str(raw.get("task_class") or ""),
        route_contract_ref=str(raw.get("route_contract_ref") or ""),
        grader_composition=grader_composition,
        track_label=str(raw.get("track_label") or "") or "production",
    )
