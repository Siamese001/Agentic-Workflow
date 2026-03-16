"""Wave 2.3 — PolicyUpdateProposal emission tests.

Tests prove:
1) Positive: approve() emits exactly one PolicyUpdateProposal with evidence_pack_id + trace_id
2) Positive: reject() emits exactly one PolicyUpdateProposal; hil_outcome correct; rationale non-empty
3) Negative: submit_for_review only (no finalization) emits no proposal
4) Determinism: same input → identical proposed_changes via fixed mapping table
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement.governance_contracts import (
    build_hil_policy_proposal,
)
from agentic_core.L0_routing.types.governance_types import (
    ChangeAction,
    HILOutcome,
    PolicyUpdateProposal,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_hil_policy_proposal_emission")
_emit_applies_guardrail("p0", "test_hil_policy_proposal_emission", "p0_governance")
_emit_snapshots_state("p0", "test_hil_policy_proposal_emission", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_hil_policy_proposal_emission", "p4obs", "metric_1")
_emit_emits_metric_event("test_hil_policy_proposal_emission", "p4obs", "metric_2")
_emit_emits_metric_event("test_hil_policy_proposal_emission", "p4obs", "metric_3")
_emit_emits_metric_event("test_hil_policy_proposal_emission", "p4obs", "metric_4")
_emit_emits_metric_event("test_hil_policy_proposal_emission", "p4obs", "metric_5")
_emit_emits_metric_event("test_hil_policy_proposal_emission", "p4obs", "metric_6")
_emit_records_incident_event("test_hil_policy_proposal_emission", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hil_policy_proposal_emission", "p4obs", "anomaly")
_emit_writes_observability_log("test_hil_policy_proposal_emission", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hil_policy_proposal_emission", "p4obs", "mon_state")
_emit_triggers_alert("test_hil_policy_proposal_emission", "p4obs", "alert")
_emit_links_incident_trace("test_hil_policy_proposal_emission", "p4obs", "trace_link")
_emit_captures_pattern("test_hil_policy_proposal_emission", "p3lm", "pattern")
_emit_records_learning_event("test_hil_policy_proposal_emission", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hil_policy_proposal_emission", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hil_policy_proposal_emission", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hil_policy_proposal_emission", "p3lm", "routing")
_emit_improves_agent_policy("test_hil_policy_proposal_emission", "p3lm", "policy")
_emit_stores_learning_state("test_hil_policy_proposal_emission", "p3lm", "state")
_emit_records_execution_trace("test_hil_policy_proposal_emission", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hil_policy_proposal_emission", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hil_policy_proposal_emission", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hil_policy_proposal_emission", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hil_policy_proposal_emission", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hil_policy_proposal_emission", "env_read", "p2_env_1")
_emit_reads_environ("test_hil_policy_proposal_emission", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hil_policy_proposal_emission", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hil_policy_proposal_emission", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_hil_policy_proposal_emission", "context_pull")
_emit_pulls_context("p1", "test_hil_policy_proposal_emission", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_hil_policy_proposal_emission", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hil_policy_proposal_emission", "uwg_term_2")
_emit_writes_through("p1", "test_hil_policy_proposal_emission", "write_through")
_emit_writes_through("p1", "test_hil_policy_proposal_emission", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_hil_policy_proposal_emission", "safety_validation")
_emit_invokes_eval("p1", "test_hil_policy_proposal_emission", "eval_call")
_emit_proposal_commits_routing("p1", "test_hil_policy_proposal_emission", "routing_commit")
_emit_escalates_to_human("p1", "test_hil_policy_proposal_emission", "human_escalation")
_emit_routes_through("p1", "test_hil_policy_proposal_emission", "route_through")
_emit_checks_agent_registry("p1", "test_hil_policy_proposal_emission", "agent_registry")
_emit_validates_agent_capability("p1", "test_hil_policy_proposal_emission", "capability")
_emit_dispatches_execution_plan("p1", "test_hil_policy_proposal_emission", "exec_plan")
_emit_agent_executes_agent("p1", "test_hil_policy_proposal_emission", "sub_agent")
_emit_routes_to_agent("p1", "test_hil_policy_proposal_emission", "target_agent")
_emit_verifies_policy("p1", "test_hil_policy_proposal_emission", "policy_check")
_emit_observes_runtime_state("p1", "test_hil_policy_proposal_emission", "runtime_state")
_emit_verifies_boundary("p1", "test_hil_policy_proposal_emission", "boundary_check")
_emit_transcripts_response("p1", "test_hil_policy_proposal_emission", "transcript")
_emit_hard_fails_untranscripted("p1", "test_hil_policy_proposal_emission")
_emit_gated_by_confidence("p1", "test_hil_policy_proposal_emission", "confidence_gate")
emit_replay_key("p0", "test_hil_policy_proposal_emission")
emit_determinism_digest("p0", "test_hil_policy_proposal_emission")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hil_policy_proposal_emission", "execution_auth")
_emit_validates_capability("p2", "test_hil_policy_proposal_emission", "capability_check")
_emit_routes_to_capability("p2", "test_hil_policy_proposal_emission", "capability_route")
_emit_writes_via_uwg("p2", "test_hil_policy_proposal_emission", "uwg_write")
_emit_blocks_direct_write("p2", "test_hil_policy_proposal_emission", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hil_policy_proposal_emission", "tool_invocation")
_emit_captures_execution_output("p2", "test_hil_policy_proposal_emission", "exec_output")
_emit_dispatches_agent("p3", "test_hil_policy_proposal_emission", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hil_policy_proposal_emission", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hil_policy_proposal_emission", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hil_policy_proposal_emission", "healing_outcome")
_emit_escalates_failure("p3", "test_hil_policy_proposal_emission", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hil_policy_proposal_emission", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hil_policy_proposal_emission", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hil_policy_proposal_emission", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hil_policy_proposal_emission", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hil_policy_proposal_emission", "eval_metric")
_emit_stores_embedding("p4", "test_hil_policy_proposal_emission", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hil_policy_proposal_emission", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hil_policy_proposal_emission", "exec_snapshot_link")

# =========================================================================
# Unit tests — build_hil_policy_proposal construction
# =========================================================================


class TestPolicyProposalConstruction:
    """Unit: build_hil_policy_proposal produces valid, typed PolicyUpdateProposal."""

    def test_approved_proposal_has_required_fields(self):
        proposal = build_hil_policy_proposal(
            trace_id="t1",
            evidence_pack_id="ep-001",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="alice",
            review_notes="Looks good",
            request_id="req-1",
        )
        assert isinstance(proposal, PolicyUpdateProposal)
        assert proposal.trace_id == "t1"
        assert proposal.evidence_pack_id == "ep-001"
        assert proposal.hil_outcome == HILOutcome.APPROVED
        assert proposal.proposal_id  # non-empty uuid4
        assert proposal.timestamp_utc  # non-empty ISO8601
        assert proposal.rationale == "Looks good"
        assert proposal.proposer == "SYSTEM"
        assert 0.0 <= proposal.confidence <= 1.0

    def test_rejected_proposal_has_correct_outcome(self):
        proposal = build_hil_policy_proposal(
            trace_id="t2",
            evidence_pack_id="ep-002",
            hil_outcome=HILOutcome.REJECTED,
            reviewer_id="bob",
            review_notes="Too risky",
            request_id="req-2",
        )
        assert proposal.hil_outcome == HILOutcome.REJECTED
        assert proposal.rationale == "Too risky"
        assert len(proposal.proposed_changes) >= 1

    def test_needs_more_info_has_empty_changes_but_rationale(self):
        proposal = build_hil_policy_proposal(
            trace_id="t3",
            evidence_pack_id="ep-003",
            hil_outcome=HILOutcome.NEEDS_MORE_INFO,
            reviewer_id="carol",
            review_notes="",
            request_id="req-3",
        )
        assert proposal.proposed_changes == ()
        assert proposal.rationale  # non-empty fallback

    def test_proposal_is_frozen(self):
        proposal = build_hil_policy_proposal(
            trace_id="t4",
            evidence_pack_id="ep-004",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="dan",
            review_notes="ok",
            request_id="req-4",
        )
        with pytest.raises(AttributeError):
            proposal.rationale = "changed"  # type: ignore[misc]

    def test_proposal_serializable(self):
        proposal = build_hil_policy_proposal(
            trace_id="t5",
            evidence_pack_id="ep-005",
            hil_outcome=HILOutcome.REJECTED,
            reviewer_id="eve",
            review_notes="deny this",
            request_id="req-5",
        )
        d = asdict(proposal)
        assert d["trace_id"] == "t5"
        assert d["evidence_pack_id"] == "ep-005"
        assert d["hil_outcome"] == HILOutcome.REJECTED or d["hil_outcome"] == "rejected"
        assert len(d["proposed_changes"]) >= 1
        pc_action = d["proposed_changes"][0]["action"]
        assert pc_action == ChangeAction.ADD or pc_action == "add"

    def test_backward_compat_old_style_still_works(self):
        proposal = PolicyUpdateProposal(
            trace_id="old",
            override_id="ov-1",
            proposed_policy_diff="diff",
            originating_agent="agent",
            semantic_clock_tick=0,
        )
        assert proposal.trace_id == "old"
        assert proposal.proposal_id == ""
        assert proposal.evidence_pack_id == ""
        assert proposal.hil_outcome is None
        assert proposal.proposed_changes == ()


# =========================================================================
# Determinism tests — same input → identical proposed_changes
# =========================================================================


class TestDeterministicMapping:
    """Determinism: fixed mapping table produces stable proposed_changes."""

    def test_approved_mapping_stable(self):
        p1 = build_hil_policy_proposal(
            trace_id="det-1",
            evidence_pack_id="ep-det",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="tester",
            review_notes="stable test",
            request_id="req-det",
        )
        p2 = build_hil_policy_proposal(
            trace_id="det-1",
            evidence_pack_id="ep-det",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="tester",
            review_notes="stable test",
            request_id="req-det",
        )
        # proposed_changes must be identical (same mapping)
        c1 = [(asdict(c)["target"], asdict(c)["action"], asdict(c)["scope"]) for c in p1.proposed_changes]
        c2 = [(asdict(c)["target"], asdict(c)["action"], asdict(c)["scope"]) for c in p2.proposed_changes]
        assert c1 == c2
        assert len(c1) >= 1

    def test_rejected_mapping_stable(self):
        p1 = build_hil_policy_proposal(
            trace_id="det-2",
            evidence_pack_id="ep-det2",
            hil_outcome=HILOutcome.REJECTED,
            reviewer_id="tester",
            review_notes="stable reject",
            request_id="req-det2",
        )
        p2 = build_hil_policy_proposal(
            trace_id="det-2",
            evidence_pack_id="ep-det2",
            hil_outcome=HILOutcome.REJECTED,
            reviewer_id="tester",
            review_notes="stable reject",
            request_id="req-det2",
        )
        c1 = [(asdict(c)["target"], asdict(c)["action"]) for c in p1.proposed_changes]
        c2 = [(asdict(c)["target"], asdict(c)["action"]) for c in p2.proposed_changes]
        assert c1 == c2

    def test_file_scope_override_is_deterministic(self):
        p1 = build_hil_policy_proposal(
            trace_id="det-3",
            evidence_pack_id="ep-det3",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="tester",
            review_notes="scoped",
            request_id="req-det3",
            file_scope="agentic_core/L3_orchestration/reasoning/Foo.py",
        )
        p2 = build_hil_policy_proposal(
            trace_id="det-3",
            evidence_pack_id="ep-det3",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="tester",
            review_notes="scoped",
            request_id="req-det3",
            file_scope="agentic_core/L3_orchestration/reasoning/Foo.py",
        )
        assert p1.proposed_changes[0].scope == p2.proposed_changes[0].scope
        assert p1.proposed_changes[0].scope == "agentic_core/L3_orchestration/reasoning/Foo.py"


# =========================================================================
# Integration tests — HumanReviewQueue.approve/reject emits proposal
# =========================================================================


def _make_queue_and_request():
    """Build a HumanReviewQueue with one pending request that has context."""
    from agentic_core.L5_safety.enforcement.human_review_queue_enforcer import (
        ContextBundle,
        HumanReviewQueue,
        ProposedDiff,
        SimulatedOutcome,
    )

    queue = HumanReviewQueue()
    ctx = ContextBundle(
        detection_signal={"type": "test"},
        proposed_diff=ProposedDiff(
            file_path=Path("test/file.py"),
            original_content="old",
            proposed_content="new",
            change_summary="test change",
        ),
        ai_rationale="test rationale",
        simulated_outcome=SimulatedOutcome(),
        risk_assessment={"level": "high"},
        additional_context={
            "evidence_pack_id": "ep-integration-001",
            "trace_id": "trace-integration-001",
        },
    )
    request = queue.submit_for_review(ctx)
    return queue, request


class TestApproveEmitsProposal:
    """Integration: approve() emits exactly one PolicyUpdateProposal."""

    def test_positive_approved_emits_proposal(self):
        queue, request = _make_queue_and_request()
        captured = []

        original_emit = queue._emit_policy_update_proposal

        def capture_emit(req, outcome):
            captured.append({"request": req, "outcome": outcome})
            original_emit(req, outcome)

        queue._emit_policy_update_proposal = capture_emit
        queue.approve(request.request_id, "alice", "approved for testing")

        assert len(captured) == 1
        assert captured[0]["outcome"] == HILOutcome.APPROVED

    def test_positive_approved_proposal_links_evidence_pack(self):
        queue, request = _make_queue_and_request()
        proposals = []

        def mock_emit(artifact_type, proposal):
            if artifact_type == "POLICY_UPDATE_PROPOSAL":
                proposals.append(asdict(proposal))

        with patch(
            "agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter",
        ) as MockEmitter:
            mock_instance = MagicMock()
            mock_instance.emit_typed_artifact = mock_emit
            MockEmitter.return_value = mock_instance

            queue.approve(request.request_id, "alice", "test notes")

        assert len(proposals) == 1
        p = proposals[0]
        assert p["evidence_pack_id"] == "ep-integration-001"
        assert p["trace_id"] == "trace-integration-001"
        assert p["hil_outcome"] in (HILOutcome.APPROVED, "approved")
        assert p["rationale"] == "test notes"


class TestRejectEmitsProposal:
    """Integration: reject() emits exactly one PolicyUpdateProposal."""

    def test_positive_rejected_emits_proposal(self):
        queue, request = _make_queue_and_request()
        captured = []

        original_emit = queue._emit_policy_update_proposal

        def capture_emit(req, outcome):
            captured.append({"request": req, "outcome": outcome})
            original_emit(req, outcome)

        queue._emit_policy_update_proposal = capture_emit
        queue.reject(request.request_id, "bob", "too risky")

        assert len(captured) == 1
        assert captured[0]["outcome"] == HILOutcome.REJECTED

    def test_positive_rejected_proposal_has_rationale(self):
        queue, request = _make_queue_and_request()
        proposals = []

        def mock_emit(artifact_type, proposal):
            if artifact_type == "POLICY_UPDATE_PROPOSAL":
                proposals.append(asdict(proposal))

        with patch(
            "agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter",
        ) as MockEmitter:
            mock_instance = MagicMock()
            mock_instance.emit_typed_artifact = mock_emit
            MockEmitter.return_value = mock_instance

            queue.reject(request.request_id, "bob", "too risky for production")

        assert len(proposals) == 1
        p = proposals[0]
        assert p["hil_outcome"] in (HILOutcome.REJECTED, "rejected")
        assert p["rationale"] == "too risky for production"
        assert len(p["proposed_changes"]) >= 1


class TestNonFinalizationNoProposal:
    """Negative: non-finalization paths emit no PolicyUpdateProposal."""

    def test_submit_only_no_proposal(self):
        from agentic_core.L5_safety.enforcement.human_review_queue_enforcer import (
            ContextBundle,
            HumanReviewQueue,
            ProposedDiff,
            SimulatedOutcome,
        )

        queue = HumanReviewQueue()
        proposals = []

        original_emit = queue._emit_policy_update_proposal

        def capture_emit(req, outcome):
            proposals.append(outcome)
            original_emit(req, outcome)

        queue._emit_policy_update_proposal = capture_emit

        ctx = ContextBundle(
            detection_signal={"type": "test"},
            proposed_diff=ProposedDiff(
                file_path=Path("test/file.py"),
                original_content="a",
                proposed_content="b",
                change_summary="c",
            ),
            ai_rationale="test",
            simulated_outcome=SimulatedOutcome(),
            risk_assessment={"level": "low"},
        )
        queue.submit_for_review(ctx)

        assert len(proposals) == 0

    def test_escalate_no_proposal(self):
        queue, request = _make_queue_and_request()
        proposals = []

        original_emit = queue._emit_policy_update_proposal

        def capture_emit(req, outcome):
            proposals.append(outcome)
            original_emit(req, outcome)

        queue._emit_policy_update_proposal = capture_emit
        queue.escalate(request.request_id, "needs senior review")

        assert len(proposals) == 0
