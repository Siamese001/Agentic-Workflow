"""Unit tests for `agentic_core.L5_safety.v5.governance_spans`.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md
Phase 5 OTEL CONTRACT.
And: docs/reference/00A_L5_Governance_Safety/00A.8a_L5_Cross_Child_Certification_Consistency_Tests.md
Phase 6 OTEL ASSERTION SHAPE.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5.governance_spans import (
    clear_recorded_spans,
    emit_aggregate_span,
    emit_blocked_span,
    emit_child_emit_span,
    emit_compare_span,
    emit_context_frozen_span,
    recorded_spans,
)


@pytest.fixture(autouse=True)
def _reset_recorder() -> None:
    clear_recorded_spans()


def _filler(seed: str) -> str:
    return (seed * 16)[:64]


class TestRecorderLifecycle:
    def test_clear_resets_recorder(self) -> None:
        emit_blocked_span(
            decisive_rule_id="L5_GOVERNANCE_CONTEXT_MISMATCH",
            first_mismatched_field="x",
            trace_id="t",
            sealed_evidence_id="s",
            terminal_class="T",
        )
        assert len(recorded_spans()) == 1
        clear_recorded_spans()
        assert recorded_spans() == ()


class TestSpanShapes:
    def test_context_frozen_span_carries_all_required_attrs(self) -> None:
        emit_context_frozen_span(
            canonical_context_digest=_filler("a"),
            request_id="req-1",
            run_id="run-1",
            trace_id="trace-1",
            tenant_id="tenant-1",
            principal_id="prin-1",
            route_id="route-1",
            step_id="step-1",
            execution_form="L2_BOUNDED",
            risk_tier="R2",
            side_effect_class="READ_ONLY",
            policy_hash=_filler("p"),
            blueprint_hash=_filler("b"),
            registry_snapshot_hash=_filler("c"),
            agent_profile_hash=_filler("d"),
            capability_scope_hash=_filler("e"),
            sandbox_envelope_hash=_filler("f"),
            origin_trust_manifest_hash=_filler("0"),
            egress_profile_hash="",
            hitl_packet_hash="",
            reclearance_hash="",
            replay_envelope_hash=_filler("1"),
            audit_manifest_hash=_filler("2"),
            static_governance_snapshot_hash=_filler("3"),
        )
        spans = recorded_spans()
        assert len(spans) == 1
        span = spans[0]
        assert span.name == "l5.governance.context.frozen"
        assert span.attributes["l5_context_digest"] == _filler("a")
        assert span.attributes["execution_form"] == "L2_BOUNDED"
        assert span.attributes["risk_tier"] == "R2"
        assert span.attributes["side_effect_class"] == "READ_ONLY"

    def test_child_emit_span(self) -> None:
        emit_child_emit_span(
            certifier_id="cert-1",
            certifier_version="v1",
            certification_scope="SAFETY",
            canonical_context_digest=_filler("a"),
            child_digest_alias="safety_enforcement_digest",
            stage_emitted_digest=_filler("a"),
            trace_id="trace-1",
        )
        span = recorded_spans()[0]
        assert span.name == "l5.governance.child.emit"
        assert span.attributes["child_digest_alias"] == "safety_enforcement_digest"
        assert span.attributes["certification_scope"] == "SAFETY"

    def test_compare_span_match(self) -> None:
        emit_compare_span(
            required_digests_seen=5,
            conditional_digests_seen=0,
            all_required_match=True,
            conditional_match=True,
            first_mismatched_field="",
            trace_id="trace-1",
        )
        span = recorded_spans()[0]
        assert span.name == "l5.governance.compare"
        assert span.attributes["all_required_match"] is True
        assert span.attributes["first_mismatched_field"] == ""

    def test_compare_span_mismatch(self) -> None:
        emit_compare_span(
            required_digests_seen=5,
            conditional_digests_seen=0,
            all_required_match=False,
            conditional_match=True,
            first_mismatched_field="origin_trust_digest",
            trace_id="trace-1",
        )
        span = recorded_spans()[0]
        assert span.attributes["all_required_match"] is False
        assert span.attributes["first_mismatched_field"] == "origin_trust_digest"

    def test_aggregate_span_only_on_certified(self) -> None:
        emit_aggregate_span(
            aggregate_governance_digest=_filler("a"),
            all_match=True,
            trace_id="trace-1",
            certified=True,
            terminal_class="L5_CERTIFIED",
        )
        span = recorded_spans()[0]
        assert span.name == "l5.governance.aggregate"
        assert span.attributes["certified"] is True
        assert span.attributes["terminal_class"] == "L5_CERTIFIED"

    def test_blocked_span_carries_decisive_rule_id(self) -> None:
        emit_blocked_span(
            decisive_rule_id="L5_GOVERNANCE_CONTEXT_MISMATCH",
            first_mismatched_field="origin_trust_digest",
            trace_id="trace-1",
            sealed_evidence_id="l5-evid-abc",
            terminal_class="L5_NOT_CERTIFIED",
        )
        span = recorded_spans()[0]
        assert span.name == "l5.governance.blocked"
        assert span.attributes["decisive_rule_id"] == "L5_GOVERNANCE_CONTEXT_MISMATCH"
        assert span.attributes["sealed_evidence_id"] == "l5-evid-abc"


class TestSpanCardinality:
    """Section enforcing 00A.8a Phase 6 cardinality:
    - exactly one l5.governance.context.frozen per packet
    - exactly one l5.governance.compare per packet
    - at most one l5.governance.aggregate (zero on mismatch)
    - exactly one l5.governance.blocked on mismatch (zero on match)
    """

    def test_match_path_emits_no_blocked(self) -> None:
        emit_compare_span(
            required_digests_seen=5,
            conditional_digests_seen=0,
            all_required_match=True,
            conditional_match=True,
            first_mismatched_field="",
            trace_id="t",
        )
        emit_aggregate_span(
            aggregate_governance_digest=_filler("a"),
            all_match=True,
            trace_id="t",
            certified=True,
            terminal_class="L5_CERTIFIED",
        )
        names = [s.name for s in recorded_spans()]
        assert names == ["l5.governance.compare", "l5.governance.aggregate"]
        assert "l5.governance.blocked" not in names

    def test_mismatch_path_emits_no_aggregate(self) -> None:
        emit_compare_span(
            required_digests_seen=5,
            conditional_digests_seen=0,
            all_required_match=False,
            conditional_match=True,
            first_mismatched_field="origin_trust_digest",
            trace_id="t",
        )
        emit_blocked_span(
            decisive_rule_id="L5_GOVERNANCE_CONTEXT_MISMATCH",
            first_mismatched_field="origin_trust_digest",
            trace_id="t",
            sealed_evidence_id="l5-evid-abc",
            terminal_class="L5_NOT_CERTIFIED",
        )
        names = [s.name for s in recorded_spans()]
        assert "l5.governance.aggregate" not in names
        assert "l5.governance.blocked" in names
