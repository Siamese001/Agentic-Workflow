"""Tests for governance_contracts.py module."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from agentic_core.L0_routing.enforcement.governance_contracts import (
    EvidencePackError,
    PolicyExceptionError,
    PolicyUpdateError,
    _make_proposal_id,
    build_evidence_pack,
    validate_evidence_pack,
    build_hil_evidence_pack,
    emit_policy_exception,
    validate_policy_exception_tick,
    propose_policy_update,
    validate_proposal,
    build_hil_policy_proposal,
)
from agentic_core.L0_routing.types.governance_types import (
    EvidencePack,
    PolicyExceptionArtifact,
    PolicyUpdateProposal,
    HILOutcome,
    ExceptionScope,
    RouteDecisionRef,
    PolicySnapshot,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot


class TestMakeProposalId:
    """Tests for _make_proposal_id helper function."""

    def test_make_proposal_id_deterministic(self):
        """Test _make_proposal_id produces deterministic ID from trace_id."""
        id1 = _make_proposal_id("test_trace")
        id2 = _make_proposal_id("test_trace")
        
        assert id1 == id2
        assert id1.startswith("PROP-")
        assert len(id1) == 20  # "PROP-" + 16 hex chars

    def test_make_proposal_id_different_traces(self):
        """Test _make_proposal_id produces different IDs for different traces."""
        id1 = _make_proposal_id("trace1")
        id2 = _make_proposal_id("trace2")
        
        assert id1 != id2


class TestEvidencePackError:
    """Tests for EvidencePackError exception."""

    def test_evidence_pack_error_creation(self):
        """Test EvidencePackError can be raised and caught."""
        with pytest.raises(EvidencePackError) as exc_info:
            raise EvidencePackError("Test error")
        
        assert "Test error" in str(exc_info.value)


class TestBuildEvidencePack:
    """Tests for build_evidence_pack function."""

    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_snapshots_state")
    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_signs_execution_trace")
    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_records_execution_trace")
    def test_build_evidence_pack_success(self, _mock_emit_snapshots, _mock_emit_signs, _mock_emit_records):
        """Test build_evidence_pack creates valid EvidencePack."""
        pack = build_evidence_pack(
            trace_id="trace123",
            action_trace=("action1", "action2"),
            policy_evals=("eval1", "eval2"),
            risk_score=0.5,
            budget_breach_data={"token_limit": 1000},
            boundary_snapshot_hash="hash123",
        )
        
        assert pack.trace_id == "trace123"
        assert pack.action_trace == ("action1", "action2")
        assert pack.policy_evals == ("eval1", "eval2")
        assert pack.risk_score == 0.5
        assert pack.budget_breach_data == {"token_limit": 1000}
        assert pack.boundary_snapshot_hash == "hash123"

    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_snapshots_state")
    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_signs_execution_trace")
    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_records_execution_trace")
    def test_build_evidence_pack_invalid_field(self, _mock_emit_snapshots, _mock_emit_signs, _mock_emit_records):
        """Test build_evidence_pack raises EvidencePackError on invalid field."""
        with pytest.raises(EvidencePackError) as exc_info:
            build_evidence_pack(
                trace_id="trace123",
                action_trace=("action1",),
                policy_evals=(),  # Invalid: should be tuple
                risk_score=0.5,
                budget_breach_data={},
                boundary_snapshot_hash="hash123",
            )
        
        assert "construction failed" in str(exc_info.value)


class TestValidateEvidencePack:
    """Tests for validate_evidence_pack function."""

    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_verifies_policy")
    def test_validate_evidence_pack_valid(self, _mock_emit_verifies):
        """Test validate_evidence_pack returns valid EvidencePack."""
        pack = EvidencePack(
            trace_id="trace123",
            action_trace=("action1",),
            policy_evals=("eval1",),
            risk_score=0.5,
            budget_breach_data={},
            boundary_snapshot_hash="hash123",
        )
        
        result = validate_evidence_pack(pack)
        
        assert result is pack

    @patch("agentic_core.L0_routing.enforcement.governance_contracts._emit_verifies_policy")
    def test_validate_evidence_pack_invalid_type(self, _mock_emit_verifies):
        """Test validate_evidence_pack raises on invalid type."""
        with pytest.raises(EvidencePackError) as exc_info:
            validate_evidence_pack("not_a_pack")
        
        assert "Expected EvidencePack" in str(exc_info.value)


class TestBuildHilEvidencePack:
    """Tests for build_hil_evidence_pack function."""

    def test_build_hil_evidence_pack_success(self):
        """Test build_hil_evidence_pack creates valid EvidencePack."""
        route_ref = RouteDecisionRef(
            trace_id="trace123",
            decision="R1A",
            agent_name="agent1",
            reason="reason1",
        )
        policy_snapshot = PolicySnapshot(
            security_level="high",
            risk_tier="TIER_1",
            laws_applied=("law1", "law2"),
            policy_hash="hash123",
        )
        
        pack = build_hil_evidence_pack(
            trace_id="trace123",
            escalation_reason="high_risk",
            route_decision_ref=route_ref,
            policy_snapshot_data=policy_snapshot,
            risk_score=0.8,
            action_trace=("action1",),
            policy_evals=("eval1",),
            guardian_results=("guard1",),
            ssot_hash="ssot123",
            attachments=("attachment1",),
        )
        
        assert pack.trace_id == "trace123"
        assert pack.escalation_reason == "high_risk"
        assert pack.risk_score == 0.8
        assert pack.evidence_id.startswith("PROP-")
        assert pack.timestamp_utc is not None
        assert pack.ssot_hash == "ssot123"

    def test_build_hil_evidence_pack_defaults(self):
        """Test build_hil_evidence_pack with default parameters."""
        route_ref = RouteDecisionRef(
            trace_id="trace123",
            decision="R1A",
            agent_name="agent1",
            reason="reason1",
        )
        policy_snapshot = PolicySnapshot(
            security_level="high",
            risk_tier="TIER_1",
            laws_applied=("law1",),
            policy_hash="hash123",
        )
        
        pack = build_hil_evidence_pack(
            trace_id="trace123",
            escalation_reason="test",
            route_decision_ref=route_ref,
            policy_snapshot_data=policy_snapshot,
        )
        
        assert pack.action_trace == ()
        assert pack.policy_evals == ()
        assert pack.guardian_results == ()
        assert pack.attachments == ()
        assert pack.risk_score == 0.8
        assert pack.ssot_hash == ""


class TestPolicyExceptionError:
    """Tests for PolicyExceptionError exception."""

    def test_policy_exception_error_creation(self):
        """Test PolicyExceptionError can be raised and caught."""
        with pytest.raises(PolicyExceptionError) as exc_info:
            raise PolicyExceptionError("Test error")
        
        assert "Test error" in str(exc_info.value)


class TestEmitPolicyException:
    """Tests for emit_policy_exception function."""

    def test_emit_policy_exception_with_nonce(self):
        """Test emit_policy_exception with provided nonce."""
        artifact = emit_policy_exception(
            trace_id="trace123",
            exception_scope=ExceptionScope.SINGLE_AGENT,
            semantic_clock_tick=5,
            issuer_signature="sig123",
            nonce="custom_nonce",
        )
        
        assert artifact.trace_id == "trace123"
        assert artifact.nonce == "custom_nonce"
        assert artifact.exception_scope == ExceptionScope.SINGLE_AGENT
        assert artifact.semantic_clock_tick == 5
        assert artifact.issuer_signature == "sig123"

    def test_emit_policy_exception_auto_nonce(self):
        """Test emit_policy_exception generates nonce if not provided."""
        artifact = emit_policy_exception(
            trace_id="trace123",
            exception_scope=ExceptionScope.HEALING_WAVE,
            semantic_clock_tick=5,
            issuer_signature="sig123",
        )
        
        assert artifact.nonce is not None
        assert len(artifact.nonce) == 32  # 16 hex bytes = 32 chars

    def test_emit_policy_exception_invalid_field(self):
        """Test emit_policy_exception raises on invalid field."""
        with pytest.raises(PolicyExceptionError) as exc_info:
            emit_policy_exception(
                trace_id="",  # Invalid: empty trace_id
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=5,
                issuer_signature="sig123",
            )
        
        assert "construction failed" in str(exc_info.value)


class TestValidatePolicyExceptionTick:
    """Tests for validate_policy_exception_tick function."""

    def test_validate_policy_exception_tick_valid(self):
        """Test validate_policy_exception_tick returns True for valid tick."""
        artifact = PolicyExceptionArtifact(
            trace_id="trace123",
            nonce="nonce123",
            exception_scope=ExceptionScope.FULL_PIPELINE,
            semantic_clock_tick=5,
            issuer_signature="sig123",
        )
        
        result = validate_policy_exception_tick(artifact, current_tick=5)
        
        assert result is True

    def test_validate_policy_exception_tick_expired(self):
        """Test validate_policy_exception_tick raises when expired."""
        artifact = PolicyExceptionArtifact(
            trace_id="trace123",
            nonce="nonce123",
            exception_scope=ExceptionScope.SINGLE_AGENT,
            semantic_clock_tick=5,
            issuer_signature="sig123",
        )
        
        with pytest.raises(PolicyExceptionError) as exc_info:
            validate_policy_exception_tick(artifact, current_tick=10)
        
        assert "expired" in str(exc_info.value).lower()
        assert "Issued at tick 5, current tick 10" in str(exc_info.value)


class TestPolicyUpdateError:
    """Tests for PolicyUpdateError exception."""

    def test_policy_update_error_creation(self):
        """Test PolicyUpdateError can be raised and caught."""
        with pytest.raises(PolicyUpdateError) as exc_info:
            raise PolicyUpdateError("Test error")
        
        assert "Test error" in str(exc_info.value)


class TestProposePolicyUpdate:
    """Tests for propose_policy_update function."""

    def test_propose_policy_update_success(self):
        """Test propose_policy_update creates valid PolicyUpdateProposal."""
        proposal = propose_policy_update(
            trace_id="trace123",
            override_id="override123",
            proposed_policy_diff="diff_content",
            originating_agent="agent1",
            semantic_clock_tick=10,
        )
        
        assert proposal.trace_id == "trace123"
        assert proposal.override_id == "override123"
        assert proposal.proposed_policy_diff == "diff_content"
        assert proposal.originating_agent == "agent1"
        assert proposal.semantic_clock_tick == 10

    def test_propose_policy_update_invalid_field(self):
        """Test propose_policy_update raises on invalid field."""
        with pytest.raises(PolicyUpdateError) as exc_info:
            propose_policy_update(
                trace_id="",  # Invalid: empty trace_id
                override_id="override123",
                proposed_policy_diff="diff",
                originating_agent="agent1",
                semantic_clock_tick=10,
            )
        
        assert "construction failed" in str(exc_info.value)


class TestValidateProposal:
    """Tests for validate_proposal function."""

    def test_validate_proposal_valid(self):
        """Test validate_proposal returns valid PolicyUpdateProposal."""
        proposal = PolicyUpdateProposal(
            trace_id="trace123",
            override_id="override123",
            proposed_policy_diff="diff",
            originating_agent="agent1",
            semantic_clock_tick=10,
        )
        
        result = validate_proposal(proposal)
        
        assert result is proposal

    def test_validate_proposal_invalid_type(self):
        """Test validate_proposal raises on invalid type."""
        with pytest.raises(PolicyUpdateError) as exc_info:
            validate_proposal("not_a_proposal")
        
        assert "Expected PolicyUpdateProposal" in str(exc_info.value)


class TestBuildHilPolicyProposal:
    """Tests for build_hil_policy_proposal function."""

    def test_build_hil_policy_proposal_approved(self):
        """Test build_hil_policy_proposal with APPROVED outcome."""
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="reviewer1",
            review_notes="Action approved after review",
        )
        
        assert proposal.trace_id == "trace123"
        assert proposal.evidence_pack_id == "evidence123"
        assert proposal.hil_outcome == HILOutcome.APPROVED
        assert proposal.originating_agent == "HIL/reviewer1"
        assert proposal.proposer == "SYSTEM"
        assert len(proposal.proposed_changes) == 1
        assert proposal.proposed_changes[0].action.value == "ADJUST"
        assert "approved" in proposal.rationale.lower()

    def test_build_hil_policy_proposal_rejected(self):
        """Test build_hil_policy_proposal with REJECTED outcome."""
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.REJECTED,
            reviewer_id="reviewer1",
            review_notes="Action rejected due to risk",
        )
        
        assert proposal.hil_outcome == HILOutcome.REJECTED
        assert len(proposal.proposed_changes) == 1
        assert proposal.proposed_changes[0].action.value == "ADD"
        assert "rejected" in proposal.rationale.lower()

    def test_build_hil_policy_proposal_overridden(self):
        """Test build_hil_policy_proposal with OVERRIDDEN outcome."""
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.OVERRIDDEN,
            reviewer_id="reviewer1",
            review_notes="System decision overridden",
        )
        
        assert proposal.hil_outcome == HILOutcome.OVERRIDDEN
        assert len(proposal.proposed_changes) == 1
        assert proposal.proposed_changes[0].action.value == "ADJUST"
        assert "override" in proposal.rationale.lower()

    def test_build_hil_policy_proposal_needs_more_info(self):
        """Test build_hil_policy_proposal with NEEDS_MORE_INFO outcome."""
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.NEEDS_MORE_INFO,
            reviewer_id="reviewer1",
            review_notes="More information needed",
        )
        
        assert proposal.hil_outcome == HILOutcome.NEEDS_MORE_INFO
        assert len(proposal.proposed_changes) == 0
        assert "needs_more_info" in proposal.rationale.lower()

    def test_build_hil_policy_proposal_with_file_scope(self):
        """Test build_hil_policy_proposal with file scope override."""
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="reviewer1",
            review_notes="Approved",
            file_scope="L2_execution/tools",
        )
        
        assert len(proposal.proposed_changes) == 1
        assert proposal.proposed_changes[0].scope == "L2_execution/tools"

    def test_build_hil_policy_proposal_with_custom_params(self):
        """Test build_hil_policy_proposal with custom parameters."""
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="reviewer1",
            review_notes="Approved",
            request_id="req123",
            file_scope="L2",
            confidence=0.85,
        )
        
        assert proposal.override_id == "req123"
        assert proposal.confidence == 0.85
        assert proposal.proposal_id.startswith("PROP-")
        assert proposal.timestamp_utc is not None

    def test_build_hil_policy_proposal_with_semantic_clock(self):
        """Test build_hil_policy_proposal with semantic clock."""
        semantic_clock = SemanticClockSnapshot(
            tick=10,
            vector_clock=(("L0", 5), ("L1", 3)),
        )
        
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="reviewer1",
            review_notes="Approved",
            semantic_clock=semantic_clock,
        )
        
        assert proposal.semantic_clock == semantic_clock

    def test_build_hil_policy_proposal_invalid_field(self):
        """Test build_hil_policy_proposal raises on invalid field."""
        with pytest.raises(PolicyUpdateError) as exc_info:
            build_hil_policy_proposal(
                trace_id="",  # Invalid: empty trace_id
                evidence_pack_id="evidence123",
                hil_outcome=HILOutcome.APPROVED,
                reviewer_id="reviewer1",
                review_notes="Approved",
            )
        
        assert "construction failed" in str(exc_info.value)

    def test_build_hil_policy_proposal_rationale_truncation(self):
        """Test build_hil_policy_proposal truncates long rationale."""
        long_notes = "x" * 300
        proposal = build_hil_policy_proposal(
            trace_id="trace123",
            evidence_pack_id="evidence123",
            hil_outcome=HILOutcome.APPROVED,
            reviewer_id="reviewer1",
            review_notes=long_notes,
        )
        
        # Rationale should be truncated to 200 chars in proposed_policy_diff
        assert len(proposal.proposed_policy_diff) < 250  # prefix + truncated rationale
