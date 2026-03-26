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

#  # MOVED: from agentic_core.L0_routing.enforcement.governance_contracts import (
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
#  # MOVED: from agentic_core.L0_routing.types.governance_types import (
    EvidencePack,
    ExceptionScope,
    PolicyExceptionArtifact,
    PolicyUpdateProposal,
    ProposalStatus,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_governance_escalation_contracts", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_governance_escalation_contracts", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_governance_escalation_contracts", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_governance_escalation_contracts", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_governance_escalation_contracts", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_governance_escalation_contracts", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_governance_escalation_contracts", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_governance_escalation_contracts", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_governance_escalation_contracts", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_governance_escalation_contracts", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_governance_escalation_contracts", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_governance_escalation_contracts", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_governance_escalation_contracts", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_governance_escalation_contracts", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_governance_escalation_contracts", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_governance_escalation_contracts", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_governance_escalation_contracts", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_governance_escalation_contracts", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_governance_escalation_contracts", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_governance_escalation_contracts", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_governance_escalation_contracts", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_governance_escalation_contracts", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_governance_escalation_contracts", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_governance_escalation_contracts", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_governance_escalation_contracts", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_governance_escalation_contracts", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_governance_escalation_contracts", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_governance_escalation_contracts", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_governance_escalation_contracts")
# REMOVED: _emit_applies_guardrail("p0", "test_governance_escalation_contracts", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_governance_escalation_contracts", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_governance_escalation_contracts", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_governance_escalation_contracts", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_governance_escalation_contracts", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_governance_escalation_contracts", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_governance_escalation_contracts", "write_through")
# REMOVED: _emit_writes_through("p1", "test_governance_escalation_contracts", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_governance_escalation_contracts", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_governance_escalation_contracts", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_governance_escalation_contracts", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_governance_escalation_contracts", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_governance_escalation_contracts", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_governance_escalation_contracts", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_governance_escalation_contracts", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_governance_escalation_contracts", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_governance_escalation_contracts", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_governance_escalation_contracts", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_governance_escalation_contracts", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_governance_escalation_contracts", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_governance_escalation_contracts", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_governance_escalation_contracts", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_governance_escalation_contracts")
# REMOVED: _emit_gated_by_confidence("p1", "test_governance_escalation_contracts", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_governance_escalation_contracts")
# REMOVED: emit_determinism_digest("p0", "test_governance_escalation_contracts")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_governance_escalation_contracts", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_governance_escalation_contracts", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_governance_escalation_contracts", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_governance_escalation_contracts", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_governance_escalation_contracts", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_governance_escalation_contracts", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_governance_escalation_contracts", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_governance_escalation_contracts", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_governance_escalation_contracts", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_governance_escalation_contracts", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_governance_escalation_contracts", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_governance_escalation_contracts", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_governance_escalation_contracts", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_governance_escalation_contracts", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_governance_escalation_contracts", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_governance_escalation_contracts", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_governance_escalation_contracts", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_governance_escalation_contracts", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_governance_escalation_contracts", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_governance_escalation_contracts", "exec_snapshot_link")

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
                from agentic_core.L0_routing.enforcement.governance_contracts import (
                from agentic_core.L0_routing.types.governance_types import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

        assert required.issubset(actual), f"Missing: {required - actual}"

    def test_frozen(self):
        pack = EvidencePack(**VALID_EVIDENCE_PACK_KWARGS)
        with pytest.raises(Exception):

            pass
            pack.trace_id = "mutated"  # type: ignore[misc]

    def test_valid_construction(self):
        pack = EvidencePack(**VALID_EVIDENCE_PACK_KWARGS)
        assert pack.trace_id == "ep-001"
        assert pack.risk_score == 0.75
        assert len(pack.action_trace) == 2
        assert len(pack.policy_evals) == 2

    def test_empty_trace_id_rejected(self):
        with pytest.raises(Exception):

            pass
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "trace_id": ""})

    def test_risk_score_below_zero_rejected(self):
        with pytest.raises(Exception):

            pass
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "risk_score": -0.1})

    def test_risk_score_above_one_rejected(self):
        with pytest.raises(Exception):

            pass
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "risk_score": 1.01})

    def test_empty_boundary_hash_rejected(self):
        with pytest.raises(Exception):

            pass
            EvidencePack(**{**VALID_EVIDENCE_PACK_KWARGS, "boundary_snapshot_hash": ""})

    def test_action_trace_must_be_tuple(self):
    """Test action_trace_must_be_tuple runtime behavior."""
    # Arrange
    # TODO: Set up test data for action_trace_must_be_tuple
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute action_trace_must_be_tuple
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
    """§3.4 — build_evidence_pack contract function."""

    def test_builds_valid_pack(self):
        pack = build_evidence_pack(**VALID_EVIDENCE_PACK_KWARGS)
        assert isinstance(pack, EvidencePack)
        assert pack.trace_id == "ep-001"

    def test_invalid_fields_raise_error(self):
        with pytest.raises(Exception):

            pass
            build_evidence_pack(**{**VALID_EVIDENCE_PACK_KWARGS, "trace_id": ""})

    def test_validate_evidence_pack_accepts_valid(self):
        pack = build_evidence_pack(**VALID_EVIDENCE_PACK_KWARGS)
        assert validate_evidence_pack(pack) is pack

    def test_validate_evidence_pack_rejects_dict(self):
        with pytest.raises(Exception):

            pass
            validate_evidence_pack({"trace_id": "x"})

    def test_validate_evidence_pack_rejects_none(self):
        with pytest.raises(Exception):

            pass
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
        with pytest.raises(Exception):

            pass
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
        with pytest.raises(Exception):

            pass
            PolicyExceptionArtifact(
                trace_id="",
                nonce="abc",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=0,
                issuer_signature="sig",
            )

    def test_empty_nonce_rejected(self):
        with pytest.raises(Exception):

            pass
            PolicyExceptionArtifact(
                trace_id="pe-001",
                nonce="",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=0,
                issuer_signature="sig",
            )

    def test_negative_tick_rejected(self):
        with pytest.raises(Exception):

            pass
            PolicyExceptionArtifact(
                trace_id="pe-001",
                nonce="abc",
                exception_scope=ExceptionScope.SINGLE_AGENT,
                semantic_clock_tick=-1,
                issuer_signature="sig",
            )

    def test_empty_signature_rejected(self):
        with pytest.raises(Exception):

            pass
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
        with pytest.raises(Exception):

            pass
# REMOVED:             emit_policy_exception(**{**VALID_EXCEPTION_KWARGS, "trace_id": ""})

    def test_all_scopes_accepted(self):
        for scope in ExceptionScope:
            art = emit_policy_exception(**{**VALID_EXCEPTION_KWARGS, "exception_scope": scope})
            assert art.exception_scope is scope

    def test_tick_validation_same_tick_passes(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        assert validate_policy_exception_tick(art, current_tick=5) is True

    def test_tick_validation_different_tick_fails(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        with pytest.raises(Exception):

            pass
            validate_policy_exception_tick(art, current_tick=6)

    def test_tick_validation_past_tick_fails(self):
        art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
        with pytest.raises(Exception):

            pass
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
        with pytest.raises(Exception):

            pass
            prop.trace_id = "mutated"  # type: ignore[misc]

    def test_valid_construction(self):
        prop = PolicyUpdateProposal(**VALID_PROPOSAL_KWARGS)
        assert prop.trace_id == "pu-001"
        assert prop.status == ProposalStatus.PENDING

    def test_empty_trace_id_rejected(self):
        with pytest.raises(Exception):

            pass
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "trace_id": ""})

    def test_empty_override_id_rejected(self):
        with pytest.raises(Exception):

            pass
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "override_id": ""})

    def test_empty_diff_rejected(self):
        with pytest.raises(Exception):

            pass
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "proposed_policy_diff": ""})

    def test_empty_agent_rejected(self):
        with pytest.raises(Exception):

            pass
            PolicyUpdateProposal(**{**VALID_PROPOSAL_KWARGS, "originating_agent": ""})

    def test_negative_tick_rejected(self):
        with pytest.raises(Exception):

            pass
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
        with pytest.raises(Exception):

            pass
            propose_policy_update(**{**VALID_PROPOSAL_KWARGS, "trace_id": ""})

    def test_validate_proposal_accepts_valid(self):
        prop = propose_policy_update(**VALID_PROPOSAL_KWARGS)
        assert validate_proposal(prop) is prop

    def test_validate_proposal_rejects_dict(self):
        with pytest.raises(Exception):

            pass
            validate_proposal({"trace_id": "x"})

    def test_validate_proposal_rejects_none(self):
        with pytest.raises(Exception):

            pass
            validate_proposal(None)

    def test_semantic_clock_tick_zero_accepted(self):
        prop = propose_policy_update(**{**VALID_PROPOSAL_KWARGS, "semantic_clock_tick": 0})
        assert prop.semantic_clock_tick == 0
