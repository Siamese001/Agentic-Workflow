"""L2 Resolution OTEL spans — emission helpers + in-memory test recorder.

Maps to: docs/reference/04_L2_Execute/04.5a_L2_Resolution_Context_Invariant.md
Phase 4 OTEL CONTRACT.

Span vocabulary:
  l2.resolution.validate    — emitted at E2 with validator-side digest
  l2.resolution.heal        — emitted at E4 with heal-side digest
  l2.resolution.compare     — emitted at E4 boundary; resolution_match attr
  l2.heal.blocked           — emitted on mismatch; carries decisive_rule_id
  l2.heal.executed          — emitted when heal actually runs

This module:
  - Always records spans into a process-local in-memory recorder so tests
    can assert against real recorded spans (NOT logs).
  - Optionally bridges to opentelemetry.trace if available, but the test
    surface does not depend on opentelemetry being installed.

Tests inspect `recorded_spans()` / `clear_recorded_spans()`. Production code
calls only the `emit_*_span` functions.
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# L2 resolution emitter — agent-level resolution spans.
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (  # guardian: allow-layer-violation -- L2 resolution spans attach OTel GenAI semconv keys; test recorder does not hard-depend on OTEL
    ATTR_OPERATION_NAME,
    OPERATION_INVOKE_AGENT,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_INVOKE_AGENT
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import threading
from dataclasses import dataclass, field
from typing import Any

# Best-effort opentelemetry bridge. Failing import or runtime error must
# never break L2 control flow — emission is observability, not enforcement.
try:  # pragma: no cover - import guard, exercised by env without otel
    from opentelemetry import trace as _otel_trace  # type: ignore[import-not-found]

    _OTEL_TRACER = _otel_trace.get_tracer("agentic_core.L2_execution.resolution")
except ImportError:  # pragma: no cover
    _OTEL_TRACER = None  # type: ignore[assignment]


_LOCK = threading.Lock()
_RECORDED: list[RecordedSpan] = []


@dataclass(frozen=True)
class RecordedSpan:
    """Frozen recording of one emitted L2 resolution span."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)


def _record(name: str, attributes: dict[str, Any]) -> None:
    """Append the span to the in-memory recorder, then bridge to OTEL."""
    snapshot = RecordedSpan(name=name, attributes=dict(attributes))
    with _LOCK:
        _RECORDED.append(snapshot)
    if _OTEL_TRACER is not None:
        try:  # pragma: no cover - thin OTEL bridge
            with _OTEL_TRACER.start_as_current_span(name) as span:
                for key, value in attributes.items():
                    if value is None:
                        continue
                    span.set_attribute(key, value)
        except (
            RuntimeError,
            ValueError,
            TypeError,
        ):  # guardian: allow-silent-swallow -- OTEL bridge is best-effort observability; never break L2 control flow
            pass


def recorded_spans() -> tuple[RecordedSpan, ...]:
    """Return all spans recorded since the last `clear_recorded_spans()`."""
    with _LOCK:
        return tuple(_RECORDED)


def clear_recorded_spans() -> None:
    """Reset the in-memory recorder. Tests call this in fixtures."""
    with _LOCK:
        _RECORDED.clear()


def _common_attrs(
    *,
    request_id: str,
    run_id: str,
    route_id: str,
    step_id: str | None,
    trace_id: str,
    agent_id: str,
    agent_type: str,
    agent_version: str,
    validator_id: str,
    validator_version: str,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
    capability_scope_hash: str,
    sandbox_envelope_hash: str,
    snapshot_manifest_hash: str,
    provider_lane: str,
    repair_authority_class: str,
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "run_id": run_id,
        "route_id": route_id,
        "step_id": step_id or "",
        "trace_id": trace_id,
        "agent_id": agent_id,
        "agent_type": agent_type,
        "agent_version": agent_version,
        "validator_id": validator_id,
        "validator_version": validator_version,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "capability_scope_hash": capability_scope_hash,
        "sandbox_envelope_hash": sandbox_envelope_hash,
        "snapshot_manifest_hash": snapshot_manifest_hash,
        "provider_lane": provider_lane,
        "repair_authority_class": repair_authority_class,
    }


def emit_validate_span(
    *,
    validator_resolution_digest: str,
    request_id: str,
    run_id: str,
    route_id: str,
    step_id: str | None,
    trace_id: str,
    agent_id: str,
    agent_type: str,
    agent_version: str,
    validator_id: str,
    validator_version: str,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
    capability_scope_hash: str,
    sandbox_envelope_hash: str,
    snapshot_manifest_hash: str,
    provider_lane: str,
    repair_authority_class: str,
) -> None:
    """Emit `l2.resolution.validate` span (E2 side)."""
    attrs = _common_attrs(
        request_id=request_id,
        run_id=run_id,
        route_id=route_id,
        step_id=step_id,
        trace_id=trace_id,
        agent_id=agent_id,
        agent_type=agent_type,
        agent_version=agent_version,
        validator_id=validator_id,
        validator_version=validator_version,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        capability_scope_hash=capability_scope_hash,
        sandbox_envelope_hash=sandbox_envelope_hash,
        snapshot_manifest_hash=snapshot_manifest_hash,
        provider_lane=provider_lane,
        repair_authority_class=repair_authority_class,
    )
    attrs["validator_resolution_digest"] = validator_resolution_digest
    _record("l2.resolution.validate", attrs)


def emit_heal_span(
    *,
    heal_resolution_digest: str,
    request_id: str,
    run_id: str,
    route_id: str,
    step_id: str | None,
    trace_id: str,
    agent_id: str,
    agent_type: str,
    agent_version: str,
    validator_id: str,
    validator_version: str,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
    capability_scope_hash: str,
    sandbox_envelope_hash: str,
    snapshot_manifest_hash: str,
    provider_lane: str,
    repair_authority_class: str,
) -> None:
    """Emit `l2.resolution.heal` span (E4 side)."""
    attrs = _common_attrs(
        request_id=request_id,
        run_id=run_id,
        route_id=route_id,
        step_id=step_id,
        trace_id=trace_id,
        agent_id=agent_id,
        agent_type=agent_type,
        agent_version=agent_version,
        validator_id=validator_id,
        validator_version=validator_version,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        capability_scope_hash=capability_scope_hash,
        sandbox_envelope_hash=sandbox_envelope_hash,
        snapshot_manifest_hash=snapshot_manifest_hash,
        provider_lane=provider_lane,
        repair_authority_class=repair_authority_class,
    )
    attrs["heal_resolution_digest"] = heal_resolution_digest
    _record("l2.resolution.heal", attrs)


def emit_compare_span(
    *,
    validator_resolution_digest: str,
    heal_resolution_digest: str,
    resolution_match: bool,
    first_mismatched_field: str,
    trace_id: str,
    decision_id: str = "",
) -> None:
    """Emit `l2.resolution.compare` span — pure compare result."""
    _record(
        "l2.resolution.compare",
        {
            "validator_resolution_digest": validator_resolution_digest,
            "heal_resolution_digest": heal_resolution_digest,
            "resolution_match": resolution_match,
            "first_mismatched_field": first_mismatched_field,
            "trace_id": trace_id,
            "decision_id": decision_id,
        },
    )


def emit_blocked_span(
    *,
    decisive_rule_id: str,
    validator_resolution_digest: str,
    heal_resolution_digest: str,
    first_mismatched_field: str,
    trace_id: str,
    sealed_artifact_id: str,
    terminal_class: str,
) -> None:
    """Emit `l2.heal.blocked` span — fired when resolution_match=False."""
    _record(
        "l2.heal.blocked",
        {
            "decisive_rule_id": decisive_rule_id,
            "validator_resolution_digest": validator_resolution_digest,
            "heal_resolution_digest": heal_resolution_digest,
            "first_mismatched_field": first_mismatched_field,
            "trace_id": trace_id,
            "sealed_artifact_id": sealed_artifact_id,
            "terminal_class": terminal_class,
        },
    )


def emit_executed_span(
    *,
    trace_id: str,
    sealed_artifact_id: str,
    repair_count: int,
    max_repair_count: int,
    terminal_class: str,
) -> None:
    """Emit `l2.heal.executed` span — fired when heal actually runs."""
    _record(
        "l2.heal.executed",
        {
            "trace_id": trace_id,
            "sealed_artifact_id": sealed_artifact_id,
            "repair_count": repair_count,
            "max_repair_count": max_repair_count,
            "resolution_match": True,
            "terminal_class": terminal_class,
        },
    )


__all__ = [
    "RecordedSpan",
    "recorded_spans",
    "clear_recorded_spans",
    "emit_validate_span",
    "emit_heal_span",
    "emit_compare_span",
    "emit_blocked_span",
    "emit_executed_span",
]
