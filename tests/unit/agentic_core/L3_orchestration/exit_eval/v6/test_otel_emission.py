"""Tests for §5.8 OTEL span catalog and emission helpers."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    EXIT_V6_SPAN_CATALOG,
    REQUIRED_ATTRIBUTES,
    ExitEvalPipeline,
    V6Disposition,
    collected_span_names,
    default_backends,
    missing_required_attributes,
    record_span,
    span,
)
from agentic_core.L3_orchestration.exit_eval.v6 import otel as v6_otel

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import (
    base_packet,
    base_receipts,
)


# ---- catalog --------------------------------------------------------------


def test_catalog_covers_every_spec_listed_span():
    """Spec §5.8 OTEL SPAN CATALOG enumerates ~40 span names."""
    expected = {
        "exit.input.receive",
        "exit.input.classify_source",
        "exit.input.validate_receipts",
        "exit.input.bind_identity",
        "exit.input.preserve_authority_labels",
        "exit.input.normalize_review_packet",
        "exit.x1a.policy_rules_check",
        "exit.x1b.task_completion_check",
        "exit.x1c.safety_to_leave_check",
        "exit.x1d.groundedness_check",
        "exit.x1e.trajectory_check",
        "exit.x1f.adversarial_check",
        "exit.x1g.consistency_check",
        "exit.x1h.replay_integrity_check",
        "exit.x1i.observability_check",
        "exit.x1j.write_eligibility_check",
        "exit.x2.aggregate_decision",
        "exit.x3.disposition_select",
        "exit.x3a.deny_reroute_emit",
        "exit.x3b.escalate_emit",
        "exit.x3c.commit_request_disposition_emit",
        "exit.x3d.allow_finish_emit",
        "exit.x3e.safe_abstain_emit",
        "exit.hitl.freeze",
        "exit.hitl.review_packet_materialize",
        "exit.hitl.decision_receive",
        "exit.hitl.modification_diff_capture",
        "exit.hitl.l5_reclearance_request",
        "exit.hitl.reentry_dispatch",
        "exit.return_payload.build",
        "exit.return_payload.validate",
        "exit.runtime_exhaust.seal",
        "exit.runtime_boundary.close",
        "exit.l6_handoff.enqueue",
        "exit.x3c.commit_request_build",
        "exit.x3c.uwg_handoff_emit",
        "exit.uwg_response.receive",
    }
    missing = expected - EXIT_V6_SPAN_CATALOG
    assert not missing, f"spec spans missing from catalog: {sorted(missing)}"


def test_required_attributes_match_spec():
    """Spec §5.8 + v4_hardening §H5.1 REQUIRED TRACE ATTRIBUTES.

    Base 26 from 05.8 + 13 H5 hardening attrs added by Wave 2 deferred-scope.
    """
    base_05_8 = {
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
    }
    h5_hardening = {
        "gate",
        "track",
        "trajectory_class",
        "rubric_version",
        "composition",
        "aggregate_score",
        "aggregate_threshold",
        "passed",
        "abstain",
        "disposition_hint",
        "bypass_audit_id",
        "grader_class",
        "rubric_id",
    }
    expected = base_05_8 | h5_hardening
    assert expected == set(REQUIRED_ATTRIBUTES), (
        f"missing: {expected - set(REQUIRED_ATTRIBUTES)}; "
        f"extra: {set(REQUIRED_ATTRIBUTES) - expected}"
    )


def test_unknown_span_name_rejected():
    packet = base_packet()
    with pytest.raises(ValueError, match="unknown Exit-v6 span name"):
        record_span("exit.bogus", packet)
    with pytest.raises(ValueError, match="unknown Exit-v6 span name"):
        with span("exit.bogus", packet=packet):
            pass


# ---- emission -------------------------------------------------------------


def test_record_span_writes_into_packet_and_default_attrs():
    packet = base_packet()
    record_span(v6_otel.SPAN_X1A_POLICY, packet, attributes={"gate_id": "X1A", "result": "PASS"})
    bucket = packet.otel_spans["v6"][v6_otel.SPAN_X1A_POLICY]
    assert len(bucket) == 1
    attrs = bucket[0]["attributes"]
    # all required keys present
    for key in REQUIRED_ATTRIBUTES:
        assert key in attrs
    # caller-supplied wins over default
    assert attrs["gate_id"] == "X1A"
    assert attrs["result"] == "PASS"
    # packet-derived attributes propagate
    assert attrs["request_id"] == "req-1"
    assert attrs["replay_key"] == "rk-1"


def test_span_context_manager_records_latency():
    packet = base_packet()
    with span(v6_otel.SPAN_X2_AGGREGATE, packet=packet, attributes={"x3_disposition": "X3D"}) as attrs:
        attrs["result"] = "PASS"
    bucket = packet.otel_spans["v6"][v6_otel.SPAN_X2_AGGREGATE]
    assert bucket
    assert bucket[0]["attributes"]["result"] == "PASS"
    assert bucket[0]["attributes"]["x3_disposition"] == "X3D"
    assert "latency_ms" in bucket[0]["attributes"]


def test_missing_required_attributes_helper_returns_empty_for_well_formed_span():
    packet = base_packet()
    record_span(v6_otel.SPAN_X1A_POLICY, packet)
    missing = missing_required_attributes(packet, v6_otel.SPAN_X1A_POLICY)
    assert missing == []


def test_missing_required_attributes_returns_full_list_when_no_recording():
    packet = base_packet()
    missing = missing_required_attributes(packet, v6_otel.SPAN_X1A_POLICY)
    # No recordings → full required list missing.
    assert set(missing) == set(REQUIRED_ATTRIBUTES)


# ---- pipeline-driven emission ---------------------------------------------


_INPUT_SPANS = (
    v6_otel.SPAN_INPUT_RECEIVE,
    v6_otel.SPAN_INPUT_CLASSIFY_SOURCE,
    v6_otel.SPAN_INPUT_VALIDATE_RECEIPTS,
    v6_otel.SPAN_INPUT_BIND_IDENTITY,
    v6_otel.SPAN_INPUT_PRESERVE_AUTHORITY_LABELS,
    v6_otel.SPAN_INPUT_NORMALIZE_REVIEW_PACKET,
)

_X1_SPANS = (
    v6_otel.SPAN_X1A_POLICY,
    v6_otel.SPAN_X1B_TASK,
    v6_otel.SPAN_X1C_SAFETY,
    v6_otel.SPAN_X1D_GROUNDED,
    v6_otel.SPAN_X1E_TRAJECTORY,
    v6_otel.SPAN_X1F_ADVERSARIAL,
    v6_otel.SPAN_X1G_CONSISTENCY,
    v6_otel.SPAN_X1H_REPLAY,
    v6_otel.SPAN_X1I_OBSERVABILITY,
    v6_otel.SPAN_X1J_WRITE_ELIGIBILITY,
)


def test_pipeline_emits_input_normalization_spans():
    pipeline = ExitEvalPipeline()
    result = pipeline.run(base_receipts())
    assert result.packet is not None
    names = collected_span_names(result.packet)
    for span_name in _INPUT_SPANS:
        assert span_name in names, f"missing {span_name}"


def test_pipeline_emits_all_ten_x1_spans():
    pipeline = ExitEvalPipeline()
    result = pipeline.run(base_receipts())
    assert result.packet is not None
    names = collected_span_names(result.packet)
    for span_name in _X1_SPANS:
        assert span_name in names


def test_pipeline_emits_x2_x3_select_and_x3d_emit():
    pipeline = ExitEvalPipeline()
    result = pipeline.run(base_receipts())
    assert result.disposition is V6Disposition.ALLOW
    names = collected_span_names(result.packet)
    assert v6_otel.SPAN_X2_AGGREGATE in names
    assert v6_otel.SPAN_X3_SELECT in names
    assert v6_otel.SPAN_X3D_ALLOW_EMIT in names
    assert v6_otel.SPAN_X3A_DENY_EMIT not in names


def test_pipeline_emits_return_build_validate_seal_close_spans():
    pipeline = ExitEvalPipeline()
    result = pipeline.run(base_receipts())
    names = collected_span_names(result.packet)
    assert v6_otel.SPAN_RETURN_BUILD in names
    assert v6_otel.SPAN_RETURN_VALIDATE in names
    assert v6_otel.SPAN_EXHAUST_SEAL in names
    assert v6_otel.SPAN_RUNTIME_BOUNDARY_CLOSE in names


def test_pipeline_emits_uwg_handoff_spans_on_commit_path():
    receipts = base_receipts(
        terminal_class="with_state_diff",
        write_intent_class="memory_promotion",
        capability_token={"authorizes_write": True},
        state_diff={
            "complete": True,
            "bounded": True,
            "uwg_routed": True,
            "blast_radius": "low",
            "rollback_plan": {"steps": []},
        },
        grader_composition={
            "roster": ["code_schema"],
            "threshold_profile": "production_v1",
            "consistency": {"pass_power_estimate": 0.99, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    pipeline = ExitEvalPipeline(uwg_backends=default_backends())
    result = pipeline.run(receipts)
    assert result.disposition is V6Disposition.COMMIT_REQUEST
    names = collected_span_names(result.packet)
    assert v6_otel.SPAN_X3C_COMMIT_REQUEST_BUILD in names
    assert v6_otel.SPAN_X3C_UWG_HANDOFF_EMIT in names
    assert v6_otel.SPAN_UWG_RESPONSE_RECEIVE in names
