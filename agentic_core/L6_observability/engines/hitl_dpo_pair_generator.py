"""DPO Pair Generator - deterministic human-in-the-loop feedback processing.

Converts APPROVE/REJECT decisions into DPO pairs with stable hashing.
"""

from __future__ import annotations

import hashlib
from typing import Protocol

from agentic_core.L6_observability.types.dpo_types import DPOExampleId, DPOPair
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("hitl_dpo_pair_generator", "hitl_dpo_pair_generator_trace")


class DPOPairGenerator(Protocol):
    """Protocol for generating DPO pairs from human feedback."""

    def generate(
        self,
        *,
        control_output_bytes: bytes,
        candidate_output_bytes: bytes,
        human_decision: str,
        reason_codes: tuple[str, ...],
    ) -> DPOPair:
        """Generate a DPO pair from human feedback.

        Parameters:
            control_output_bytes: Raw bytes of control output.
            candidate_output_bytes: Raw bytes of candidate output.
            human_decision: Human decision ("APPROVE" or "REJECT").
            reason_codes: Tuple of short deterministic reason codes.

        Returns:
            DPOPair with deterministic hashing.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DPOPairGenerator.generate", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DPOPairGenerator.generate", "p0_governance")
        ...


class DefaultDeterministicDPOPairGenerator:
    """Default deterministic DPO pair generator.

    Generates stable DPO pairs with SHA-256 hashing and no side effects.
    """

    def generate(
        self,
        *,
        control_output_bytes: bytes,
        candidate_output_bytes: bytes,
        human_decision: str,
        reason_codes: tuple[str, ...],
    ) -> DPOPair:
        """Generate a DPO pair with deterministic behavior.

        Args:
            control_output_bytes: Raw bytes of control output.
            candidate_output_bytes: Raw bytes of candidate output.
            human_decision: Human decision ("APPROVE" or "REJECT").
            reason_codes: Tuple of short deterministic reason codes.

        Returns:
            DPOPair with stable example_id and content_hash.

        Raises:
            ValueError: If human_decision is not "APPROVE" or "REJECT".
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "DefaultDeterministicDPOPairGenerator.generate"
        )

        if human_decision not in {"APPROVE", "REJECT"}:
            raise ValueError(f"human_decision must be 'APPROVE' or 'REJECT', got: {human_decision}")
        control_hash = hashlib.sha256(control_output_bytes).hexdigest()
        candidate_hash = hashlib.sha256(candidate_output_bytes).hexdigest()
        example_id = DPOExampleId(control_hash=control_hash, candidate_hash=candidate_hash)
        pair = DPOPair(
            example_id=example_id,
            control_output_hash=control_hash,
            candidate_output_hash=candidate_hash,
            human_decision=human_decision,
            reasons=reason_codes,
        )
        return pair
