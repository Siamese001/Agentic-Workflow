"""
V15 P3 Compliance Tests — Governance & Human Escalation.

Regression tests proving all 3 P3 items are COMPLIANT:
  §3.4 — EvidencePack (Human Escalation)
  §3.7 — PolicyExceptionArtifact (Policy Challenge Protocol)
  §3.5 — PolicyUpdateProposal (Bidirectional Feedback)

Each test class covers:
  - required fields exist and are immutable/frozen
  - invalid/missing fields fail closed
  - contract functions produce correct typed artifacts
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.enforcement.governance_contracts import (
    EvidencePackError,
    PolicyExceptionError,
    PolicyUpdateError,
    build_evidence_pack,
    emit_policy_exception,
    propose_policy_update,
    validate_evidence_pack,
    validate_policy_exception_tick,
    validate_proposal,
)
from agentic_core.L0_routing.types.governance_types import (
    EvidencePack,
    ExceptionScope,
    PolicyExceptionArtifact,
    PolicyUpdateProposal,
    ProposalStatus,
)

# ---- helpers ----------------------------------------------------------------

VALID_EVIDENCE_PACK_KWARGS = {
    "trace_id": "ep-001",
    "action_trace": ("L0:scan", "L0:classify"),
    "policy_evals": ("L5:gravity_pass", "L5:naming_fail"),
    "risk_score": 0.75,
    "budget_breach_data": {"tokens_used": 1200, "budget_limit": 1000},
    "boundary_snapshot_hash": "abc123def456",
}

VALID_EXCEPTION_KWARGS = {
    "trace_id": "pe-001",
    "exception_scope": ExceptionScope.SINGLE_AGENT,
    "semantic_clock_tick": 5,
    "issuer_signature": "sig-human-reviewer-001",
}

VALID_PROPOSAL_KWARGS = {
    "trace_id": "pu-001",
    "override_id": "ovr-001",
    "proposed_policy_diff": "- max_retries: 3\n+ max_retries: 5",
    "originating_agent": "StructureHealerAgent",
    "semantic_clock_tick": 5,
}


# =============================================================================
# §3.4 — EvidencePack
# =============================================================================


class TestP3_34_EvidencePackArtifact:
    """§3.4 — EvidencePack typed artifact validation."""

    def test_all_required_fields_present(self):
        required = {
            "trace_id",
            "action_trace",
            "policy_evals",
            "risk_score",
            "budget_breach_data",
            "boundary_snapshot_hash",
        }
        actual = {f.name for f in dataclasses.fields(EvidencePack)}
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_frozen(self):
        pack = EvidencePack(**VALID_EVIDENCE_PACK_KWARGS)
        with pytest.raises(dataclasses.FrozenInstanceError):
            pack.trace_id = "mutated"  # type: ignore[misc]

    def test_valid_construction(self):
        pack = EvidencePack(**VALID_EVIDENCE_PACK_KWARGS)
        assert pack.trace_id == "ep-001"
        assert pack.risk_score == 0.75
        assert len(pack.action_trace) == 2
        assert len(pack.policy_evals) == 2

    def test_empty_trace_id_rejected(self):
        with pytest.raises(ValueError, match="trace_id"):
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "trace_id": ""})

    def test_risk_score_below_zero_rejected(self):
        with pytest.raises(ValueError, match="risk_score"):
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "risk_score": -0.1})

    def test_risk_score_above_one_rejected(self):
        with pytest.raises(ValueError, match="risk_score"):
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "risk_score": 1.01})

    def test_empty_boundary_hash_rejected(self):
        with pytest.raises(ValueError, match="boundary_snapshot_hash"):
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "boundary_snapshot_hash": ""})

    def test_action_trace_must_be_tuple(self):
        with pytest.raises(TypeError, match="action_trace"):
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "action_trace": ["a", "b"]})

    def test_policy_evals_must_be_tuple(self):
        with pytest.raises(TypeError, match="policy_evals"):
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "policy_evals": ["a"]})


class TestP3_34_BuildEvidencePack:
    """§3.4 — build_evidence_pack contract function."""

    def test_builds_valid_pack(self):
        pack = build_evidence_pack(**VALID_EVIDENCE_PACK_KWARGS)
        assert isinstance(pack, EvidencePack)
        assert pack.trace_id == "ep-001"

    def test_invalid_fields_raise_error(self):
        with pytest.raises(EvidencePackError, match="FAIL"):
            build_evidence_pack(**{**VALID_EVIDENCE_PACK_KWARGS, "trace_id": ""})

    def test_validate_evidence_pack_accepts_valid(self):
        pack = build_evidence_pack(**VALID_EVIDENCE_PACK_KWARGS)
        assert validate_evidence_pack(pack) is pack

    def test_validate_evidence_pack_rejects_dict(self):
        with pytest.raises(EvidencePackError, match="dict"):
            validate_evidence_pack({"trace_id": "x"})

    def test_validate_evidence_pack_rejects_none(self):
        with pytest.raises(EvidencePackError, match="NoneType"):
            validate_evidence_pack(None)

    def test_risk_score_boundary_zero(self):
        pack = build_evidence_pack(**{**VALID_EVIDENCE_PACK_KWARGS, "risk_score": 0.0})
        assert pack.risk_score == 0.0

    def test_risk_score_boundary_one(self):
        pack = build_evidence_pack(**{**VALID_EVIDENCE_PACK_KWARGS, "risk_score": 1.0})
        assert pack.risk_score == 1.0


# =============================================================================
# §3.7 — PolicyExceptionArtifact
# =============================================================================


class TestP3_37_PolicyExceptionArtifact:
    """§3.7 — PolicyExceptionArtifact typed artifact validation."""

    def test_all_required_fields_present(self):
        required = {
            "trace_id",
            "nonce",
            "exception_scope",
            "semantic_clock_tick",
            "issuer_signature",
        }
        actual = {f.name for f in dataclasses.fields(PolicyExceptionArtifact)}
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_frozen(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        with pytest.raises(dataclasses.FrozenInstanceError):
            art.trace_id = "mutated"  # type: ignore[misc]

    def test_valid_construction(self):
        art = PolicyExceptionArtifact(
            trace_id="pe-001",
            nonce="abc123",
            exception_scope=ExceptionScope.SINGLE_AGENT,
            semantic_clock_tick=5,
            issuer_signature="sig-001",
        )
        assert art.trace_id == "pe-001"
        assert art.semantic_clock_tick == 5

    def test_empty_trace_id_rejected(self):
        with pytest.raises(ValueError, match="trace_id"):
            PolicyExceptionArtifact(
                trace_id="",
                nonce="abc",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=0,
                issuer_signature="sig",
            )

    def test_empty_nonce_rejected(self):
        with pytest.raises(ValueError, match="nonce"):
            PolicyExceptionArtifact(
                trace_id="pe-001",
                nonce="",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=0,
                issuer_signature="sig",
            )

    def test_negative_tick_rejected(self):
        with pytest.raises(ValueError, match="semantic_clock_tick"):
            PolicyExceptionArtifact(
                trace_id="pe-001",
                nonce="abc",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=-1,
                issuer_signature="sig",
            )

    def test_empty_signature_rejected(self):
        with pytest.raises(ValueError, match="issuer_signature"):
            PolicyExceptionArtifact(
                trace_id="pe-001",
                nonce="abc",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=0,
                issuer_signature="",
            )

    def test_exception_scope_enum_values(self):
        assert ExceptionScope.SINGLE_AGENT.value == "single_agent"
        assert ExceptionScope.HEALING_WAVE.value == "healing_wave"
        assert ExceptionScope.FULL_PIPELINE.value == "full_pipeline"


class TestP3_37_EmitPolicyException:
    """§3.7 — emit_policy_exception contract function."""

    def test_emits_valid_artifact(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        assert isinstance(art, PolicyExceptionArtifact)
        assert art.trace_id == "pe-001"
        assert len(art.nonce) == 32  # secrets.token_hex(16)

    def test_custom_nonce_accepted(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS, nonce="custom-nonce")
        assert art.nonce == "custom-nonce"

    def test_invalid_fields_raise_error(self):
        with pytest.raises(PolicyExceptionError, match="FAIL"):
            emit_policy_exception(**{**VALID_EXCEPTION_KWARGS, "trace_id": ""})

    def test_all_scopes_accepted(self):
        for scope in ExceptionScope:
            art = emit_policy_exception(**{**VALID_EXCEPTION_KWARGS, "exception_scope": scope})
            assert art.exception_scope is scope

    def test_tick_validation_same_tick_passes(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        assert validate_policy_exception_tick(art, current_tick=5) is True

    def test_tick_validation_different_tick_fails(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        with pytest.raises(PolicyExceptionError, match="expired"):
            validate_policy_exception_tick(art, current_tick=6)

    def test_tick_validation_past_tick_fails(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        with pytest.raises(PolicyExceptionError, match="expired"):
            validate_policy_exception_tick(art, current_tick=4)


# =============================================================================
# §3.5 — PolicyUpdateProposal
# =============================================================================


class TestP3_35_PolicyUpdateProposal:
    """§3.5 — PolicyUpdateProposal typed artifact validation."""

    def test_all_required_fields_present(self):
        required = {
            "trace_id",
            "override_id",
            "proposed_policy_diff",
            "originating_agent",
            "semantic_clock_tick",
        }
        actual = {f.name for f in dataclasses.fields(PolicyUpdateProposal)}
        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_frozen(self):
        prop = propose_policy_update(**VALID_PROPOSAL_KWARGS)
        with pytest.raises(dataclasses.FrozenInstanceError):
            prop.trace_id = "mutated"  # type: ignore[misc]

    def test_valid_construction(self):
        prop = PolicyUpdateProposal(**VALID_PROPOSAL_KWARGS)
        assert prop.trace_id == "pu-001"
        assert prop.status == ProposalStatus.PENDING

    def test_empty_trace_id_rejected(self):
        with pytest.raises(ValueError, match="trace_id"):
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "trace_id": ""})

    def test_empty_override_id_rejected(self):
        with pytest.raises(ValueError, match="override_id"):
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "override_id": ""})

    def test_empty_diff_rejected(self):
        with pytest.raises(ValueError, match="proposed_policy_diff"):
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "proposed_policy_diff": ""})

    def test_empty_agent_rejected(self):
        with pytest.raises(ValueError, match="originating_agent"):
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "originating_agent": ""})

    def test_negative_tick_rejected(self):
        with pytest.raises(ValueError, match="semantic_clock_tick"):
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "semantic_clock_tick": -1})

    def test_proposal_status_enum_values(self):
        assert ProposalStatus.PENDING.value == "pending"
        assert ProposalStatus.ACCEPTED.value == "accepted"
        assert ProposalStatus.REJECTED.value == "rejected"

    def test_default_status_is_pending(self):
        prop = PolicyUpdateProposal(**VALID_PROPOSAL_KWARGS)
        assert prop.status == ProposalStatus.PENDING


class TestP3_35_ProposePolicyUpdate:
    """§3.5 — propose_policy_update contract function."""

    def test_proposes_valid_update(self):
        prop = propose_policy_update(**VALID_PROPOSAL_KWARGS)
        assert isinstance(prop, PolicyUpdateProposal)
        assert prop.override_id == "ovr-001"

    def test_invalid_fields_raise_error(self):
        with pytest.raises(PolicyUpdateError, match="FAIL"):
            propose_policy_update(**{**VALID_PROPOSAL_KWARGS, "trace_id": ""})

    def test_validate_proposal_accepts_valid(self):
        prop = propose_policy_update(**VALID_PROPOSAL_KWARGS)
        assert validate_proposal(prop) is prop

    def test_validate_proposal_rejects_dict(self):
        with pytest.raises(PolicyUpdateError, match="dict"):
            validate_proposal({"trace_id": "x"})

    def test_validate_proposal_rejects_none(self):
        with pytest.raises(PolicyUpdateError, match="NoneType"):
            validate_proposal(None)

    def test_semantic_clock_tick_zero_accepted(self):
        prop = propose_policy_update(**{**VALID_PROPOSAL_KWARGS, "semantic_clock_tick": 0})
        assert prop.semantic_clock_tick == 0
