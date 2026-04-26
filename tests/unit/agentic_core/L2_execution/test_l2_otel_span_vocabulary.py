"""Tests for L2 OTEL span vocabulary (doc 04.8).

Covers:
  * Every spec'd span name is in the canonical registry (04.8 §PHASE 1).
  * Required-attribute schema enforcement.
  * Unknown span names raise.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.observability.l2_spans import (
    L2_E1_SPANS,
    L2_E2_SPANS,
    L2_E3_SPANS,
    L2_E4_SPANS,
    L2_E5_SPANS,
    L2_PTC_SPANS,
    L2_REQUIRED_SPAN_ATTRIBUTES,
    L2SpanAttributeViolation,
    all_l2_span_names,
    validate_span_attributes,
)


# ---------------------------------------------------------------------------
# Spec coverage — every span name in 04.8 §PHASE 1 must be registered
# ---------------------------------------------------------------------------


_E1_REQUIRED = {
    "l2.e1.prep.receive",
    "l2.e1.prep.authority_bind",
    "l2.e1.prep.environment_freeze",
    "l2.e1.prep.determinism_bind",
    "l2.e1.prep.idempotency_guard",
    "l2.e1.prep.lineage_root",
    "l2.e1.prep.write_lock_assertion",
    "l2.e1.prep.receipt_emit",
}
_E2_REQUIRED = {
    "l2.e2.valid.signature_chain",
    "l2.e2.valid.capability_scope",
    "l2.e2.valid.budget_scope",
    "l2.e2.valid.schema_shape",
    "l2.e2.valid.side_effect_class",
    "l2.e2.valid.safety_sanity",
    "l2.e2.valid.executability",
    "l2.e2.valid.receipt_emit",
}
_E3_REQUIRED = {
    "l2.e3.exec.attempt_open",
    "l2.e3.exec.invocation_build",
    "l2.e3.exec.sandbox_run",
    "l2.e3.exec.model_call",
    "l2.e3.exec.tool_call",
    "l2.e3.exec.script_call",
    "l2.e3.exec.output_capture",
    "l2.e3.exec.local_checks",
    "l2.e3.exec.result_classify",
    "l2.e3.exec.receipt_emit",
}
_E4_REQUIRED = {
    "l2.e4.heal.failure_record",
    "l2.e4.heal.localize",
    "l2.e4.heal.repair_plan",
    "l2.e4.heal.snapshot_guard",
    "l2.e4.heal.oscillation_guard",
    "l2.e4.heal.receipt_emit",
}
_E5_REQUIRED = {
    "l2.e5.seal.payload_package",
    "l2.e5.seal.trace_package",
    "l2.e5.seal.replay_package",
    "l2.e5.seal.terminal_stamp",
    "l2.e5.seal.commit_boundary",
    "l2.e5.seal.dispatch_receipt",
}
_PTC_REQUIRED = {
    "l2.ptc.context_freeze",
    "l2.ptc.sandbox_start",
    "l2.ptc.tool_call",
    "l2.ptc.stdout_summary_emit",
    "l2.ptc.context_unfreeze",
    "l2.ptc.receipt_emit",
}


def test_e1_spans_cover_spec() -> None:
    assert _E1_REQUIRED.issubset(set(L2_E1_SPANS))


def test_e2_spans_cover_spec() -> None:
    assert _E2_REQUIRED.issubset(set(L2_E2_SPANS))


def test_e3_spans_cover_spec() -> None:
    assert _E3_REQUIRED.issubset(set(L2_E3_SPANS))


def test_e4_spans_cover_spec() -> None:
    assert _E4_REQUIRED.issubset(set(L2_E4_SPANS))


def test_e5_spans_cover_spec() -> None:
    assert _E5_REQUIRED.issubset(set(L2_E5_SPANS))


def test_ptc_spans_cover_spec() -> None:
    assert _PTC_REQUIRED.issubset(set(L2_PTC_SPANS))


def test_all_l2_span_names_is_union_no_dupes() -> None:
    names = all_l2_span_names()
    assert len(names) == len(set(names)), "duplicate L2 span name in registry"
    # Every spec'd span across all groups appears.
    spec = _E1_REQUIRED | _E2_REQUIRED | _E3_REQUIRED | _E4_REQUIRED | _E5_REQUIRED | _PTC_REQUIRED
    assert spec.issubset(set(names))


def test_every_l2_span_uses_l2_prefix() -> None:
    for name in all_l2_span_names():
        assert name.startswith("l2."), f"span {name!r} missing 'l2.' prefix"


# ---------------------------------------------------------------------------
# Required-attribute schema
# ---------------------------------------------------------------------------


def _full_attrs() -> dict:
    return {
        "trace_id": "tr-1",
        "span_id": "sp-1",
        "parent_span_id": "psp-1",
        "request_id": "req-1",
        "run_id": "run-1",
        "route_id": "route-1",
        "policy_hash": "pol-1",
        "blueprint_hash": "bp-1",
        "replay_key": "rk-1",
        "capability_token_ref": "cap-1",
        "sandbox_envelope_ref": "sbx-1",
        "side_effect_class": "READ",
        "latency_ms": 42,
    }


def test_required_attribute_set_is_exhaustive() -> None:
    expected = {
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
    }
    assert set(L2_REQUIRED_SPAN_ATTRIBUTES) == expected


def test_validate_span_attributes_clean() -> None:
    missing = validate_span_attributes(
        span_name="l2.e1.prep.receive",
        attrs=_full_attrs(),
    )
    assert missing == ()


def test_validate_span_attributes_reports_missing() -> None:
    attrs = _full_attrs()
    del attrs["trace_id"]
    del attrs["replay_key"]
    missing = validate_span_attributes(
        span_name="l2.e1.prep.receive",
        attrs=attrs,
    )
    assert "trace_id" in missing
    assert "replay_key" in missing


def test_validate_span_attributes_workflow_required_when_managed() -> None:
    attrs = _full_attrs()
    missing = validate_span_attributes(
        span_name="l2.e1.prep.receive",
        attrs=attrs,
        has_workflow=True,
    )
    assert "workflow_id" in missing
    assert "step_id" in missing


def test_validate_span_attributes_attempt_required() -> None:
    attrs = _full_attrs()
    missing = validate_span_attributes(
        span_name="l2.e3.exec.attempt_open",
        attrs=attrs,
        has_attempt=True,
    )
    assert "attempt_id" in missing


def test_validate_span_attributes_invocation_required() -> None:
    attrs = _full_attrs()
    missing = validate_span_attributes(
        span_name="l2.e3.exec.tool_call",
        attrs=attrs,
        has_invocation=True,
    )
    assert "invocation_kind" in missing


def test_validate_span_attributes_terminal_required() -> None:
    attrs = _full_attrs()
    missing = validate_span_attributes(
        span_name="l2.e5.seal.terminal_stamp",
        attrs=attrs,
        has_terminal=True,
    )
    assert "terminal_class" in missing
    assert "reason_codes" in missing


def test_validate_span_attributes_artifacts_required() -> None:
    attrs = _full_attrs()
    missing = validate_span_attributes(
        span_name="l2.e3.exec.output_capture",
        attrs=attrs,
        has_artifacts=True,
    )
    assert "artifact_refs" in missing


def test_unknown_span_raises() -> None:
    with pytest.raises(L2SpanAttributeViolation, match="unknown L2 span"):
        validate_span_attributes(span_name="l2.unknown.foo", attrs=_full_attrs())


def test_required_attribute_includes_observability_keys() -> None:
    """Sanity: trace identity, run identity, snapshot identity, latency."""
    must_have = {"trace_id", "run_id", "policy_hash", "blueprint_hash", "latency_ms"}
    assert must_have.issubset(set(L2_REQUIRED_SPAN_ATTRIBUTES))
