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
