"""v6 §5.8 — OTEL span catalog + emission helpers.

Implements the spec at
``docs/reference/05_Exit_Evaluation_&_Control/05.8_Exit_Observability_Tests_and_Anti_Bypass_detailed.md``.

This module owns:
- the canonical Exit-Eval OTEL span name catalog (~40 names)
- the required-attributes set every Exit span must carry
- a thin emission helper that records spans into the
  ``ExitReviewPacket.otel_spans`` mapping AND, when an OTEL SDK is available,
  emits a real OpenTelemetry span via ``trace.get_tracer``.

Design choices:
- Soft dependency on ``opentelemetry`` — module is import-safe even when the
  SDK is not installed. When it is missing, ``record_span`` becomes a no-op
  for the SDK side but still updates the in-packet span dict so X1I observability
  checks can verify the span was recorded.
- Uses a context-manager ``span(...)`` for normal call-site use, and a free
  helper ``record_span(...)`` for after-the-fact recording from tests.
"""

from __future__ import annotations

# OTel GenAI semconv opt-out: this module emits OTel spans that are
# infrastructure / governance / state-write events, not GenAI agent /
# workflow / tool / model invocations. GenAI semconv attributes do
# not apply. Plan: three-bucket-gap-remediation-069806 (W3).
__non_genai_emitter__ = "L3 exit-evaluation governance spans — verdict + disposition, not GenAI invocations"

import contextlib
import logging
import time
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, Final

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket

logger = logging.getLogger(__name__)


# ---- Spec §5.8 OTEL SPAN CATALOG -----------------------------------------

# Input/normalization
SPAN_INPUT_RECEIVE: Final[str] = "exit.input.receive"
SPAN_INPUT_CLASSIFY_SOURCE: Final[str] = "exit.input.classify_source"
SPAN_INPUT_VALIDATE_RECEIPTS: Final[str] = "exit.input.validate_receipts"
SPAN_INPUT_BIND_IDENTITY: Final[str] = "exit.input.bind_identity"
SPAN_INPUT_PRESERVE_AUTHORITY_LABELS: Final[str] = "exit.input.preserve_authority_labels"
SPAN_INPUT_NORMALIZE_REVIEW_PACKET: Final[str] = "exit.input.normalize_review_packet"

# X1 checks — A through J
SPAN_X1A_POLICY: Final[str] = "exit.x1a.policy_rules_check"
SPAN_X1B_TASK: Final[str] = "exit.x1b.task_completion_check"
SPAN_X1C_SAFETY: Final[str] = "exit.x1c.safety_to_leave_check"
SPAN_X1D_GROUNDED: Final[str] = "exit.x1d.groundedness_check"
SPAN_X1E_TRAJECTORY: Final[str] = "exit.x1e.trajectory_check"
SPAN_X1F_ADVERSARIAL: Final[str] = "exit.x1f.adversarial_check"
SPAN_X1G_CONSISTENCY: Final[str] = "exit.x1g.consistency_check"
SPAN_X1H_REPLAY: Final[str] = "exit.x1h.replay_integrity_check"
SPAN_X1I_OBSERVABILITY: Final[str] = "exit.x1i.observability_check"
SPAN_X1J_WRITE_ELIGIBILITY: Final[str] = "exit.x1j.write_eligibility_check"

# Aggregation / disposition
SPAN_X2_AGGREGATE: Final[str] = "exit.x2.aggregate_decision"
SPAN_X3_SELECT: Final[str] = "exit.x3.disposition_select"
SPAN_X3A_DENY_EMIT: Final[str] = "exit.x3a.deny_reroute_emit"
SPAN_X3B_ESCALATE_EMIT: Final[str] = "exit.x3b.escalate_emit"
SPAN_X3C_COMMIT_REQUEST_EMIT: Final[str] = "exit.x3c.commit_request_disposition_emit"
SPAN_X3D_ALLOW_EMIT: Final[str] = "exit.x3d.allow_finish_emit"
SPAN_X3E_ABSTAIN_EMIT: Final[str] = "exit.x3e.safe_abstain_emit"
SPAN_X3F_BREAK_GLASS_EMIT: Final[str] = "exit.x3f.break_glass_allow_emit"

# HITL
SPAN_HITL_FREEZE: Final[str] = "exit.hitl.freeze"
SPAN_HITL_PACKET_MATERIALIZE: Final[str] = "exit.hitl.review_packet_materialize"
SPAN_HITL_DECISION_RECEIVE: Final[str] = "exit.hitl.decision_receive"
SPAN_HITL_MOD_DIFF: Final[str] = "exit.hitl.modification_diff_capture"
SPAN_HITL_L5_RECLEAR: Final[str] = "exit.hitl.l5_reclearance_request"
SPAN_HITL_REENTRY: Final[str] = "exit.hitl.reentry_dispatch"

# Return / exhaust
SPAN_RETURN_BUILD: Final[str] = "exit.return_payload.build"
SPAN_RETURN_VALIDATE: Final[str] = "exit.return_payload.validate"
SPAN_EXHAUST_SEAL: Final[str] = "exit.runtime_exhaust.seal"
SPAN_RUNTIME_BOUNDARY_CLOSE: Final[str] = "exit.runtime_boundary.close"
SPAN_L6_HANDOFF_ENQUEUE: Final[str] = "exit.l6_handoff.enqueue"

# UWG handoff
SPAN_X3C_COMMIT_REQUEST_BUILD: Final[str] = "exit.x3c.commit_request_build"
SPAN_X3C_UWG_HANDOFF_EMIT: Final[str] = "exit.x3c.uwg_handoff_emit"
SPAN_UWG_RESPONSE_RECEIVE: Final[str] = "exit.uwg_response.receive"

# Live signal consumption
SPAN_LIVE_BELL_CONSUME: Final[str] = "exit.live_bell.consume"
SPAN_EVIDENCE_SEAL_VERIFY: Final[str] = "exit.evidence_seal.verify"

#: Frozen set of every Exit-Eval v6 OTEL span name. Used by X1I observability
#: gate and the §5.8 anti-bypass tests.
EXIT_V6_SPAN_CATALOG: frozenset[str] = frozenset(
    {
        # input/normalize
        SPAN_INPUT_RECEIVE,
        SPAN_INPUT_CLASSIFY_SOURCE,
        SPAN_INPUT_VALIDATE_RECEIPTS,
        SPAN_INPUT_BIND_IDENTITY,
        SPAN_INPUT_PRESERVE_AUTHORITY_LABELS,
        SPAN_INPUT_NORMALIZE_REVIEW_PACKET,
        # X1
        SPAN_X1A_POLICY,
        SPAN_X1B_TASK,
        SPAN_X1C_SAFETY,
        SPAN_X1D_GROUNDED,
        SPAN_X1E_TRAJECTORY,
        SPAN_X1F_ADVERSARIAL,
        SPAN_X1G_CONSISTENCY,
        SPAN_X1H_REPLAY,
        SPAN_X1I_OBSERVABILITY,
        SPAN_X1J_WRITE_ELIGIBILITY,
        # aggregation
        SPAN_X2_AGGREGATE,
        SPAN_X3_SELECT,
        SPAN_X3A_DENY_EMIT,
        SPAN_X3B_ESCALATE_EMIT,
        SPAN_X3C_COMMIT_REQUEST_EMIT,
        SPAN_X3D_ALLOW_EMIT,
        SPAN_X3E_ABSTAIN_EMIT,
        SPAN_X3F_BREAK_GLASS_EMIT,
        # HITL
        SPAN_HITL_FREEZE,
        SPAN_HITL_PACKET_MATERIALIZE,
        SPAN_HITL_DECISION_RECEIVE,
        SPAN_HITL_MOD_DIFF,
        SPAN_HITL_L5_RECLEAR,
        SPAN_HITL_REENTRY,
        # return/exhaust
        SPAN_RETURN_BUILD,
        SPAN_RETURN_VALIDATE,
        SPAN_EXHAUST_SEAL,
        SPAN_RUNTIME_BOUNDARY_CLOSE,
        SPAN_L6_HANDOFF_ENQUEUE,
        # UWG handoff
        SPAN_X3C_COMMIT_REQUEST_BUILD,
        SPAN_X3C_UWG_HANDOFF_EMIT,
        SPAN_UWG_RESPONSE_RECEIVE,
        # live signal
        SPAN_LIVE_BELL_CONSUME,
        SPAN_EVIDENCE_SEAL_VERIFY,
    }
)


#: Spec §5.8 REQUIRED TRACE ATTRIBUTES — every Exit span must carry these
#: (where applicable; missing values are recorded as empty strings, not omitted,
#: so X1I can verify presence).
REQUIRED_ATTRIBUTES: tuple[str, ...] = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "request_id",
    "run_id",
    "session_id",
    "tenant_id",
    "source_type",
    "route_id",
    "execution_form",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "exit_review_packet_id",
    "gate_id",
    "x3_disposition",
    "commit_request_id",
    "hitl_review_packet_id",
    "evidence_contract_ref",
    "prompt_artifact_ref",
    "sealed_l2_artifact_ref",
    "l3_workflow_package_ref",
    "result",
    "reason_codes",
    "latency_ms",
    "deterministic_digest",
    # v4_hardening §H5.1 — per-gate span attributes (Wave 2 of deferred-scope)
    # These extend the base 26 with the addendum-mandated 13 hardening attributes
    # so dashboards / runtime ADG ingest / SLO panels can group by them.
    "gate",
    "track",  # capability | regression | production | shadow-candidate
    "trajectory_class",
    "rubric_version",
    "composition",  # binary | weighted | hybrid
    "aggregate_score",
    "aggregate_threshold",
    "passed",
    "abstain",
    "disposition_hint",  # X3A | X3B | X3C_pending | X3D
    "bypass_audit_id",  # links to H3 break-glass row when applicable
    "grader_class",  # code_based | model_based | human-calibrated
    "rubric_id",
)


@dataclass(slots=True)
class SpanRecord:
    """In-memory record of an Exit-Eval span — used when no OTEL SDK is wired."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    start_ms: int = 0
    end_ms: int = 0
    latency_ms: int = 0


def _packet_attrs(packet: ExitReviewPacket) -> dict[str, Any]:
    rc = packet.route_contract or {}
    return {
        "request_id": packet.request_id,
        "run_id": packet.run_id,
        "session_id": packet.session_id,
        "trace_id": packet.trace_root,
        "source_type": packet.source_type.value if packet.source_type else "",
        "route_id": packet.route_id or rc.get("route_id", ""),
        "execution_form": rc.get("execution_form", ""),
        "policy_hash": packet.policy_hash,
        "blueprint_hash": packet.blueprint_hash,
        "replay_key": packet.replay_key,
        "tenant_id": rc.get("tenant_scope", "") or rc.get("tenant_id", ""),
    }


def required_attrs_with_defaults(
    packet: ExitReviewPacket,
    *,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dict pre-populated with every key in ``REQUIRED_ATTRIBUTES``.

    Missing values default to empty string (or empty list for ``reason_codes``)
    so the X1I observability check can validate by-key presence rather than
    truthiness — required for spec invariant 'every Exit span must include …'.
    """
    base: dict[str, Any] = {key: "" for key in REQUIRED_ATTRIBUTES}
    base["reason_codes"] = []
    base["latency_ms"] = 0
    base.update(_packet_attrs(packet))
    if extra:
        base.update(dict(extra))
    return base


def _record_into_packet(
    packet: ExitReviewPacket | None,
    name: str,
    attributes: Mapping[str, Any],
    *,
    start_ms: int,
    end_ms: int,
) -> SpanRecord:
    record = SpanRecord(
        name=name,
        attributes=dict(attributes),
        start_ms=start_ms,
        end_ms=end_ms,
        latency_ms=max(0, end_ms - start_ms),
    )
    if packet is None:
        return record
    bucket = packet.otel_spans.setdefault("v6", {})  # type: ignore[union-attr]
    bucket.setdefault(name, []).append(
        {
            "attributes": record.attributes,
            "start_ms": record.start_ms,
            "end_ms": record.end_ms,
            "latency_ms": record.latency_ms,
        }
    )
    # Backward compat: also seed the legacy ``spans`` map so the existing
    # X1I gate sees common entries (e.g. ``exit_disposition``).
    legacy_map = packet.otel_spans.setdefault("spans", {})  # type: ignore[union-attr]
    if name == SPAN_X3_SELECT:
        legacy_map["exit_disposition"] = attributes.get("x3_disposition", "")
    return record


# ---- public API ----------------------------------------------------------


def _try_emit_to_sdk(name: str, attributes: Mapping[str, Any]) -> None:
    """Best-effort emission via the OpenTelemetry SDK if installed.

    Uses a function-local import so this module is import-safe when the SDK
    isn't present.
    """
    try:
        from opentelemetry import trace  # type: ignore[import-not-found]
    except ImportError:  # guardian: allow-return-none-swallow -- opentelemetry optional; returns None (bare return) when SDK absent; caller omits span silently
        return
    try:
        tracer = trace.get_tracer("agentic_core.L3_orchestration.exit_eval.v6")
        with tracer.start_as_current_span(name) as sdk_span:  # type: ignore[arg-type]
            for k, v in attributes.items():
                # Avoid attribute-type errors: stringify complex values.
                if isinstance(v, (str, int, float, bool)):
                    sdk_span.set_attribute(k, v)
                else:
                    sdk_span.set_attribute(k, str(v))
    except (RuntimeError, OSError, ValueError) as exc:  # pragma: no cover
        logger.debug("OTEL SDK emission failed for span=%s: %s", name, exc)


@contextlib.contextmanager
def span(
    name: str,
    *,
    packet: ExitReviewPacket | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Context manager that records a span into the packet + emits via SDK.

    Yields the attribute dict so the caller can mutate it during the span
    body (e.g. attach result, reason_codes, latency).
    """
    if name not in EXIT_V6_SPAN_CATALOG:
        raise ValueError(f"unknown Exit-v6 span name: {name!r}")
    base_attrs = (
        required_attrs_with_defaults(
            packet or ExitReviewPacket(source_type=type("S", (), {"value": ""})()),  # type: ignore[arg-type]
            extra=attributes,
        )
        if packet
        else dict(attributes or {})
    )
    start = int(time.time() * 1000)
    try:
        yield base_attrs
    finally:
        end = int(time.time() * 1000)
        base_attrs["latency_ms"] = max(0, end - start)
        _record_into_packet(packet, name, base_attrs, start_ms=start, end_ms=end)
        _try_emit_to_sdk(name, base_attrs)


def record_span(
    name: str,
    packet: ExitReviewPacket,
    *,
    attributes: Mapping[str, Any] | None = None,
    latency_ms: int = 0,
) -> SpanRecord:
    """Record a synthetic span (no body) into ``packet.otel_spans``.

    Useful for unit tests and for places where a span has effectively zero
    measurable duration (e.g. building a packet shape).
    """
    if name not in EXIT_V6_SPAN_CATALOG:
        raise ValueError(f"unknown Exit-v6 span name: {name!r}")
    attrs = required_attrs_with_defaults(packet, extra=attributes)
    attrs["latency_ms"] = int(latency_ms)
    now = int(time.time() * 1000)
    rec = _record_into_packet(packet, name, attrs, start_ms=now - latency_ms, end_ms=now)
    _try_emit_to_sdk(name, attrs)
    return rec


def collected_span_names(packet: ExitReviewPacket) -> set[str]:
    """Return the set of v6-span names recorded into the packet."""
    bucket = (packet.otel_spans or {}).get("v6", {}) if packet.otel_spans else {}
    return set(bucket.keys())


def missing_required_attributes(packet: ExitReviewPacket, span_name: str) -> list[str]:
    """Return the list of required-attribute keys missing from any recording of ``span_name``."""
    bucket = (packet.otel_spans or {}).get("v6", {}).get(span_name, [])
    if not bucket:
        return list(REQUIRED_ATTRIBUTES)
    # Use the most-recent emission for the check.
    last = bucket[-1]
    attrs = last.get("attributes", {})
    return [k for k in REQUIRED_ATTRIBUTES if k not in attrs]


__all__ = [
    "EXIT_V6_SPAN_CATALOG",
    "REQUIRED_ATTRIBUTES",
    "SPAN_EVIDENCE_SEAL_VERIFY",
    "SPAN_EXHAUST_SEAL",
    "SPAN_HITL_DECISION_RECEIVE",
    "SPAN_HITL_FREEZE",
    "SPAN_HITL_L5_RECLEAR",
    "SPAN_HITL_MOD_DIFF",
    "SPAN_HITL_PACKET_MATERIALIZE",
    "SPAN_HITL_REENTRY",
    "SPAN_INPUT_BIND_IDENTITY",
    "SPAN_INPUT_CLASSIFY_SOURCE",
    "SPAN_INPUT_NORMALIZE_REVIEW_PACKET",
    "SPAN_INPUT_PRESERVE_AUTHORITY_LABELS",
    "SPAN_INPUT_RECEIVE",
    "SPAN_INPUT_VALIDATE_RECEIPTS",
    "SPAN_L6_HANDOFF_ENQUEUE",
    "SPAN_LIVE_BELL_CONSUME",
    "SPAN_RETURN_BUILD",
    "SPAN_RETURN_VALIDATE",
    "SPAN_RUNTIME_BOUNDARY_CLOSE",
    "SPAN_UWG_RESPONSE_RECEIVE",
    "SPAN_X1A_POLICY",
    "SPAN_X1B_TASK",
    "SPAN_X1C_SAFETY",
    "SPAN_X1D_GROUNDED",
    "SPAN_X1E_TRAJECTORY",
    "SPAN_X1F_ADVERSARIAL",
    "SPAN_X1G_CONSISTENCY",
    "SPAN_X1H_REPLAY",
    "SPAN_X1I_OBSERVABILITY",
    "SPAN_X1J_WRITE_ELIGIBILITY",
    "SPAN_X2_AGGREGATE",
    "SPAN_X3A_DENY_EMIT",
    "SPAN_X3B_ESCALATE_EMIT",
    "SPAN_X3C_COMMIT_REQUEST_BUILD",
    "SPAN_X3C_COMMIT_REQUEST_EMIT",
    "SPAN_X3C_UWG_HANDOFF_EMIT",
    "SPAN_X3D_ALLOW_EMIT",
    "SPAN_X3E_ABSTAIN_EMIT",
    "SPAN_X3F_BREAK_GLASS_EMIT",
    "SPAN_X3_SELECT",
    "SpanRecord",
    "collected_span_names",
    "missing_required_attributes",
    "record_span",
    "required_attrs_with_defaults",
    "span",
]
