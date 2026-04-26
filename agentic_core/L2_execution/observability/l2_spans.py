"""L2 OTEL span vocabulary — canonical span names + required attribute schema.

Maps to: docs/reference/04_L2_Execute/04.8 §PHASE 1 REQUIRED OTEL SPANS

This module is the *single source of truth* for L2 span names. Downstream
emitters (E1 prep, E2 valid, E3 exec, E4 heal, E5 seal, PTC sandbox) MUST
import the constants from here rather than hard-coding strings — that way
a typo cannot drift the trace registry.

The required-attribute set comes from 04.8 §PHASE 1 "Every span must
include:" list. :func:`validate_span_attributes` returns the list of
missing attributes for a given (span_name, attrs) pair so test fixtures
and runtime probes can fail-closed early.
"""

from __future__ import annotations

from typing import Any, Mapping


# ---------------------------------------------------------------------------
# Span name constants — grouped per E1..E5 + PTC (04.8 §PHASE 1)
# ---------------------------------------------------------------------------


L2_E1_SPANS: tuple[str, ...] = (
    "l2.e1.prep.receive",
    "l2.e1.prep.authority_bind",
    "l2.e1.prep.environment_freeze",
    "l2.e1.prep.determinism_bind",
    "l2.e1.prep.idempotency_guard",
    "l2.e1.prep.lineage_root",
    "l2.e1.prep.write_lock_assertion",
    "l2.e1.prep.receipt_emit",
)


L2_E2_SPANS: tuple[str, ...] = (
    "l2.e2.valid.signature_chain",
    "l2.e2.valid.capability_scope",
    "l2.e2.valid.budget_scope",
    "l2.e2.valid.schema_shape",
    "l2.e2.valid.side_effect_class",
    "l2.e2.valid.safety_sanity",
    "l2.e2.valid.executability",
    "l2.e2.valid.receipt_emit",
)


L2_E3_SPANS: tuple[str, ...] = (
    "l2.e3.exec.attempt_open",
    "l2.e3.exec.invocation_build",
    "l2.e3.exec.sandbox_run",
    "l2.e3.exec.model_call",
    "l2.e3.exec.tool_call",
    "l2.e3.exec.script_call",
    "l2.e3.exec.file_io",
    "l2.e3.exec.network_egress",
    "l2.e3.exec.output_capture",
    "l2.e3.exec.local_checks",
    "l2.e3.exec.result_classify",
    "l2.e3.exec.receipt_emit",
)


L2_E4_SPANS: tuple[str, ...] = (
    "l2.e4.heal.failure_record",
    "l2.e4.heal.localize",
    "l2.e4.heal.repair_plan",
    "l2.e4.heal.snapshot_guard",
    "l2.e4.heal.oscillation_guard",
    "l2.e4.heal.revalidate",
    "l2.e4.heal.receipt_emit",
)


L2_E5_SPANS: tuple[str, ...] = (
    "l2.e5.seal.payload_package",
    "l2.e5.seal.evidence_package",
    "l2.e5.seal.trace_package",
    "l2.e5.seal.replay_package",
    "l2.e5.seal.terminal_stamp",
    "l2.e5.seal.contract_check",
    "l2.e5.seal.commit_boundary",
    "l2.e5.seal.dispatch_receipt",
)


L2_PTC_SPANS: tuple[str, ...] = (
    "l2.ptc.validate_script",
    "l2.ptc.context_freeze",
    "l2.ptc.sandbox_start",
    "l2.ptc.tool_call",
    "l2.ptc.raw_result_store",
    "l2.ptc.stdout_summary_emit",
    "l2.ptc.context_unfreeze",
    "l2.ptc.fail_closed",
    "l2.ptc.receipt_emit",
)


def all_l2_span_names() -> tuple[str, ...]:
    """Return every canonical L2 span name (E1..E5 + PTC).

    Used by anti-bypass tests to assert that every emitted span is
    well-known and that no rogue span name leaks into telemetry.
    """
    return (
        *L2_E1_SPANS,
        *L2_E2_SPANS,
        *L2_E3_SPANS,
        *L2_E4_SPANS,
        *L2_E5_SPANS,
        *L2_PTC_SPANS,
    )


# ---------------------------------------------------------------------------
# Required-attribute schema (04.8 §PHASE 1 "Every span must include:")
# ---------------------------------------------------------------------------


# Always required on every L2 span.
_ALWAYS_REQUIRED: tuple[str, ...] = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "request_id",
    "run_id",
    "route_id",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "capability_token_ref",
    "sandbox_envelope_ref",
    "side_effect_class",
    "latency_ms",
)

# Conditionally required: present "when applicable". The condition keys
# below are checked by :func:`validate_span_attributes` against caller hints.
_CONDITIONAL_ATTRIBUTES: dict[str, str] = {
    "workflow_id": "workflow",
    "step_id": "workflow",
    "attempt_id": "attempt",
    "invocation_kind": "invocation",
    "terminal_class": "terminal",
    "reason_codes": "terminal",
    "artifact_refs": "artifacts",
}


L2_REQUIRED_SPAN_ATTRIBUTES: tuple[str, ...] = _ALWAYS_REQUIRED


class L2SpanAttributeViolation(ValueError):
    """Raised when a span is missing one or more required attributes."""


def validate_span_attributes(
    *,
    span_name: str,
    attrs: Mapping[str, Any],
    has_workflow: bool = False,
    has_attempt: bool = False,
    has_invocation: bool = False,
    has_terminal: bool = False,
    has_artifacts: bool = False,
) -> tuple[str, ...]:
    """Return the names of any missing required attributes for ``span_name``.

    Empty tuple means the span is well-formed.

    Args:
        span_name: One of :func:`all_l2_span_names`.
        attrs: The mapping of attributes the emitter is about to attach.
        has_workflow: Set True if this span is part of an L3-managed
            workflow — then ``workflow_id`` and ``step_id`` are required.
        has_attempt: Set True for spans inside an attempt context — then
            ``attempt_id`` is required.
        has_invocation: Set True for invocation spans (model/tool/script/
            action/artifact) — then ``invocation_kind`` is required.
        has_terminal: Set True for terminal-stamping spans (e5.seal.*) —
            then ``terminal_class`` and ``reason_codes`` are required.
        has_artifacts: Set True when generated artifacts exist — then
            ``artifact_refs`` is required.

    Raises:
        L2SpanAttributeViolation: if ``span_name`` is not a canonical L2 span.
    """
    if span_name not in all_l2_span_names():
        raise L2SpanAttributeViolation(
            f"unknown L2 span name: {span_name!r}; not in canonical registry"
        )

    missing: list[str] = []
    for required in _ALWAYS_REQUIRED:
        if required not in attrs or attrs.get(required) in (None, ""):
            missing.append(required)

    flags = {
        "workflow": has_workflow,
        "attempt": has_attempt,
        "invocation": has_invocation,
        "terminal": has_terminal,
        "artifacts": has_artifacts,
    }
    for cond_attr, cond_key in _CONDITIONAL_ATTRIBUTES.items():
        if flags.get(cond_key) and (
            cond_attr not in attrs or attrs.get(cond_attr) in (None, "")
        ):
            missing.append(cond_attr)

    return tuple(missing)


__all__ = [
    "L2_E1_SPANS",
    "L2_E2_SPANS",
    "L2_E3_SPANS",
    "L2_E4_SPANS",
    "L2_E5_SPANS",
    "L2_PTC_SPANS",
    "L2_REQUIRED_SPAN_ATTRIBUTES",
    "L2SpanAttributeViolation",
    "all_l2_span_names",
    "validate_span_attributes",
]
