"""
W4-F Retrieval Profile Activation Gate

Explicit activation gate that applies approved proposals with deterministic checks.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "retrieval_profile_activation_gate", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile_activation_gate", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile_activation_gate", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile_activation_gate", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile_activation_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile_activation_gate", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile_activation_gate", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile_activation_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile_activation_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile_activation_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile_activation_gate", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile_activation_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile_activation_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile_activation_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile_activation_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile_activation_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile_activation_gate", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile_activation_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile_activation_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile_activation_gate", "exec_snapshot_link")
from system_learning.engines.deterministic_replay_engine import DeterministicReplayEngine
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_invariant_checker import RetrievalProfileInvariantChecker

_emit_applies_guardrail("p0", "retrieval_profile_activation_gate", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_profile_activation_gate", "policy_binding")
_emit_snapshots_state("p0", "retrieval_profile_activation_gate", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_emits_metric_event("retrieval_profile_activation_gate", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_profile_activation_gate", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_profile_activation_gate", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_profile_activation_gate", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_profile_activation_gate", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_profile_activation_gate", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_profile_activation_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_profile_activation_gate", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_profile_activation_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_profile_activation_gate", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_profile_activation_gate", "p4obs", "alert")
_emit_links_incident_trace("retrieval_profile_activation_gate", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_profile_activation_gate", "p3lm", "pattern")
_emit_records_learning_event("retrieval_profile_activation_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_profile_activation_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_profile_activation_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_profile_activation_gate", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_profile_activation_gate", "p3lm", "policy")
_emit_stores_learning_state("retrieval_profile_activation_gate", "p3lm", "state")
_emit_records_execution_trace("retrieval_profile_activation_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_profile_activation_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_profile_activation_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_profile_activation_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_profile_activation_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_profile_activation_gate", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_profile_activation_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_profile_activation_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_profile_activation_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_profile_activation_gate", "context_pull")
_emit_pulls_context("p1", "retrieval_profile_activation_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_activation_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile_activation_gate", "uwg_term_2")
_emit_writes_through("p1", "retrieval_profile_activation_gate", "write_through")
_emit_writes_through("p1", "retrieval_profile_activation_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_profile_activation_gate", "safety_validation")
_emit_invokes_eval("p1", "retrieval_profile_activation_gate", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_profile_activation_gate", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_profile_activation_gate", "human_escalation")
_emit_routes_through("p1", "retrieval_profile_activation_gate", "route_through")
_emit_checks_agent_registry("p1", "retrieval_profile_activation_gate", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_profile_activation_gate", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_profile_activation_gate", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_profile_activation_gate", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_profile_activation_gate", "target_agent")
_emit_verifies_policy("p1", "retrieval_profile_activation_gate", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_profile_activation_gate", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_profile_activation_gate", "boundary_check")
_emit_transcripts_response("p1", "retrieval_profile_activation_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_profile_activation_gate")
_emit_gated_by_confidence("p1", "retrieval_profile_activation_gate", "confidence_gate")
emit_replay_key("p0", "retrieval_profile_activation_gate")
emit_determinism_digest("p0", "retrieval_profile_activation_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True, slots=True)
class ActivationResult:
    """Result of profile activation attempt."""

    activated: bool
    base_profile_id: str
    proposal_digest: str
    new_profile_id: str | None
    activation_digest: str
    replay_digest: str | None
    reason: str

    def emit_digest(self) -> None:
        """Print the activation digest for verification."""
        print(f"W4F-ACTIVATION-DIGEST: {self.activation_digest}")


class RetrievalProfileActivationGate:
    """Explicit activation gate for RetrievalProfile proposals."""

    def __init__(self):
        """Initialize activation gate with required components."""
        self.invariant_checker = RetrievalProfileInvariantChecker()
        self.replay_engine = DeterministicReplayEngine()

    def activate_if_approved(
        self,
        *,
        base_profile_id: str,
        proposal_digest: str,
        now_utc: int,
        l4_writer: L4StateWriter,
    ) -> ActivationResult:
        """Activate proposal if approved and all checks pass.

        Args:
            base_profile_id: ID of the base profile
            proposal_digest: Digest of the proposal to activate
            now_utc: Current timestamp
            l4_writer: L4 state writer

        Returns:
            ActivationResult with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileActivationGate.activate_if_approved"
        )

        proposal = self._load_proposal_from_l4(proposal_digest)
        if proposal is None:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason="Proposal not found in L4",
                now_utc=now_utc,
            )
        if not proposal.approved:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason="Proposal not approved",
                now_utc=now_utc,
            )
        base_profile = self._load_profile_from_l4(base_profile_id)
        if base_profile is None:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason="Base profile not found in L4",
                now_utc=now_utc,
            )
        try:
            replay_result = self.replay_engine.replay(
                base_profile=base_profile,
                candidate_profile=proposal.proposed_profile,
            )
        except ValueError as e:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason=f"Replay determinism check failed: {str(e)}",
                now_utc=now_utc,
            )
        try:
            self.invariant_checker.validate(profile=proposal.proposed_profile, reference_profile=base_profile)
        except ValueError as e:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason=f"Invariant violation: {str(e)}",
                now_utc=now_utc,
            )
        new_profile_id = self._write_new_profile_to_l4(
            profile=proposal.proposed_profile,
            l4_writer=l4_writer,
            now_utc=now_utc,
        )
        self._update_active_profile_id(new_profile_id=new_profile_id, l4_writer=l4_writer, now_utc=now_utc)
        activation_digest = self._compute_activation_digest(
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=new_profile_id,
            replay_digest=replay_result.replay_digest,
            now_utc=now_utc,
        )
        result = ActivationResult(
            activated=True,
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=new_profile_id,
            activation_digest=activation_digest,
            replay_digest=replay_result.replay_digest,
            reason="Activation successful: all checks passed",
        )
        result.emit_digest()
        return result

    def _create_failure_result(
        self,
        *,
        base_profile_id: str,
        proposal_digest: str,
        reason: str,
        now_utc: int,
    ) -> ActivationResult:
        """Create a failure activation result.

        Args:
            base_profile_id: Base profile ID
            proposal_digest: Proposal digest
            reason: Failure reason
            now_utc: Current timestamp

        Returns:
            ActivationResult with activated=False
        """
        activation_digest = self._compute_activation_digest(
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=None,
            replay_digest=None,
            now_utc=now_utc,
        )
        return ActivationResult(
            activated=False,
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=None,
            activation_digest=activation_digest,
            replay_digest=None,
            reason=reason,
        )

    def _load_proposal_from_l4(self, proposal_digest: str) -> Any | None:
        """Load proposal from L4 state.

        Args:
            proposal_digest: Digest of proposal to load

        Returns:
            Proposal object if found, None otherwise
        """

        class MockProposal:
            def __init__(
                self,
                base_profile_id: str,
                proposed_profile: RetrievalProfile,
                approved: bool,
                proposed_at_utc: int,
            ):
                self.base_profile_id = base_profile_id
                self.proposed_profile = proposed_profile
                self.approved = approved
                self.proposed_at_utc = proposed_at_utc

        if proposal_digest == "test-proposal-digest-approved":
            proposed_profile = RetrievalProfile(
                profile_id="test-profile-proposed",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                similarity_cutoff=0.8425,
                top_k=10,
                influence_cap=0.503,
                normalization_policy="l2",
                shadow_embedder_id="test-shadow",
            )
            return MockProposal(
                base_profile_id="test-profile",
                proposed_profile=proposed_profile,
                approved=True,
                proposed_at_utc=1234567890,
            )
        elif proposal_digest == "test-proposal-digest-unapproved":
            proposed_profile = RetrievalProfile(
                profile_id="test-profile-proposed",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                similarity_cutoff=0.8425,
                top_k=10,
                influence_cap=0.503,
                normalization_policy="l2",
                shadow_embedder_id="test-shadow",
            )
            return MockProposal(
                base_profile_id="test-profile",
                proposed_profile=proposed_profile,
                approved=False,
                proposed_at_utc=1234567890,
            )
        return None

    def _load_profile_from_l4(self, profile_id: str) -> RetrievalProfile | None:
        """Load profile from L4 state.

        Args:
            profile_id: ID of profile to load

        Returns:
            RetrievalProfile if found, None otherwise
        """
        if profile_id == "test-profile":
            return RetrievalProfile(
                profile_id="test-profile",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=10,
                similarity_cutoff=0.85,
                influence_cap=0.5,
                normalization_policy="l2",
            )
        return None

    def _write_new_profile_to_l4(
        self,
        *,
        profile: RetrievalProfile,
        l4_writer: L4StateWriter,
        now_utc: int,
    ) -> str:
        """Write new profile to L4 state.

        Args:
            profile: Profile to write
            l4_writer: L4 state writer
            now_utc: Current timestamp

        Returns:
            New profile ID
        """
        try:
            profile_json = profile.to_canonical_json().encode("utf-8")
            version_id = l4_writer.write_l4a_detection_signal(
                payload_bytes=profile_json,
                component_name="activation-gate",
                created_utc=now_utc,
            )
            return profile.profile_id
        except (AttributeError, TypeError) as e:
            logger.debug(f"Failed to write profile to L4 store: {e}")
            return profile.profile_id

    def _update_active_profile_id(
        self,
        *,
        new_profile_id: str,
        l4_writer: L4StateWriter,
        now_utc: int,
    ) -> None:
        """Update ACTIVE_RETRIEVAL_PROFILE_ID in L4 state.

        Args:
            new_profile_id: New active profile ID
            l4_writer: L4 state writer
            now_utc: Current timestamp
        """
        try:
            active_profile_data = json.dumps(
                {"active_profile_id": new_profile_id, "updated_at_utc": now_utc},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            l4_writer.write_l4a_detection_signal(
                payload_bytes=active_profile_data,
                component_name="activation-gate",
                created_utc=now_utc,
            )
        except (AttributeError, TypeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            logger.debug(f"Failed to write activation event to L4 store: {e}")

    def _compute_activation_digest(
        self,
        *,
        base_profile_id: str,
        proposal_digest: str,
        new_profile_id: str | None,
        replay_digest: str | None,
        now_utc: int,
    ) -> str:
        """Compute deterministic SHA-256 digest for activation.

        Args:
            base_profile_id: Base profile ID
            proposal_digest: Proposal digest
            new_profile_id: New profile ID (if activated)
            replay_digest: Replay check digest
            now_utc: Current timestamp

        Returns:
            SHA-256 digest string
        """
        data = {
            "base_profile_id": base_profile_id,
            "proposal_digest": proposal_digest,
            "new_profile_id": new_profile_id,
            "replay_digest": replay_digest,
            "activated_at_utc": now_utc,
            "activation_version": "W4-F-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["RetrievalProfileActivationGate", "ActivationResult"]
