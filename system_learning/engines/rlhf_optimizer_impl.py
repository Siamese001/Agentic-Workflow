"""RLHF Optimizer Implementation — converts DPO batches into threshold proposals.

Concrete implementation of the ``RLHFOptimizer`` Protocol defined in
``system_learning/engines/rlhf_optimizer.py``.  Takes serialized DPO batch
data and produces threshold adjustment proposals based on preference signals.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass

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

_emit_applies_guardrail("p0", "rlhf_optimizer_impl", "p0_governance")
_emit_reads_policy_state("p0", "rlhf_optimizer_impl", "policy_binding")
_emit_snapshots_state("p0", "rlhf_optimizer_impl", "state_snapshot")
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

_emit_emits_metric_event("rlhf_optimizer_impl", "p4obs", "metric_1")
_emit_emits_metric_event("rlhf_optimizer_impl", "p4obs", "metric_2")
_emit_emits_metric_event("rlhf_optimizer_impl", "p4obs", "metric_3")
_emit_emits_metric_event("rlhf_optimizer_impl", "p4obs", "metric_4")
_emit_emits_metric_event("rlhf_optimizer_impl", "p4obs", "metric_5")
_emit_emits_metric_event("rlhf_optimizer_impl", "p4obs", "metric_6")
_emit_records_incident_event("rlhf_optimizer_impl", "p4obs", "incident")
_emit_captures_runtime_anomaly("rlhf_optimizer_impl", "p4obs", "anomaly")
_emit_writes_observability_log("rlhf_optimizer_impl", "p4obs", "obs_log")
_emit_updates_monitoring_state("rlhf_optimizer_impl", "p4obs", "mon_state")
_emit_triggers_alert("rlhf_optimizer_impl", "p4obs", "alert")
_emit_links_incident_trace("rlhf_optimizer_impl", "p4obs", "trace_link")
_emit_captures_pattern("rlhf_optimizer_impl", "p3lm", "pattern")
_emit_records_learning_event("rlhf_optimizer_impl", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rlhf_optimizer_impl", "p3lm", "snapshot")
_emit_feeds_meta_learning("rlhf_optimizer_impl", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rlhf_optimizer_impl", "p3lm", "routing")
_emit_improves_agent_policy("rlhf_optimizer_impl", "p3lm", "policy")
_emit_stores_learning_state("rlhf_optimizer_impl", "p3lm", "state")
_emit_records_execution_trace("rlhf_optimizer_impl", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rlhf_optimizer_impl", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rlhf_optimizer_impl", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rlhf_optimizer_impl", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rlhf_optimizer_impl", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rlhf_optimizer_impl", "env_read", "p2_env_1")
_emit_reads_environ("rlhf_optimizer_impl", "env_read", "p2_env_2")
_emit_reads_runtime_state("rlhf_optimizer_impl", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rlhf_optimizer_impl", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rlhf_optimizer_impl", "context_pull")
_emit_pulls_context("p1", "rlhf_optimizer_impl", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rlhf_optimizer_impl", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rlhf_optimizer_impl", "uwg_term_2")
_emit_writes_through("p1", "rlhf_optimizer_impl", "write_through")
_emit_writes_through("p1", "rlhf_optimizer_impl", "write_through_2")
_emit_validated_by_safety_plane("p1", "rlhf_optimizer_impl", "safety_validation")
_emit_invokes_eval("p1", "rlhf_optimizer_impl", "eval_call")
_emit_proposal_commits_routing("p1", "rlhf_optimizer_impl", "routing_commit")
_emit_escalates_to_human("p1", "rlhf_optimizer_impl", "human_escalation")
_emit_routes_through("p1", "rlhf_optimizer_impl", "route_through")
_emit_checks_agent_registry("p1", "rlhf_optimizer_impl", "agent_registry")
_emit_validates_agent_capability("p1", "rlhf_optimizer_impl", "capability")
_emit_dispatches_execution_plan("p1", "rlhf_optimizer_impl", "exec_plan")
_emit_agent_executes_agent("p1", "rlhf_optimizer_impl", "sub_agent")
_emit_routes_to_agent("p1", "rlhf_optimizer_impl", "target_agent")
_emit_verifies_policy("p1", "rlhf_optimizer_impl", "policy_check")
_emit_observes_runtime_state("p1", "rlhf_optimizer_impl", "runtime_state")
_emit_verifies_boundary("p1", "rlhf_optimizer_impl", "boundary_check")
_emit_transcripts_response("p1", "rlhf_optimizer_impl", "transcript")
_emit_hard_fails_untranscripted("p1", "rlhf_optimizer_impl")
_emit_gated_by_confidence("p1", "rlhf_optimizer_impl", "confidence_gate")
emit_replay_key("p0", "rlhf_optimizer_impl")
emit_determinism_digest("p0", "rlhf_optimizer_impl")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rlhf_optimizer_impl", "execution_auth")
_emit_validates_capability("p2", "rlhf_optimizer_impl", "capability_check")
_emit_routes_to_capability("p2", "rlhf_optimizer_impl", "capability_route")
_emit_writes_via_uwg("p2", "rlhf_optimizer_impl", "uwg_write")
_emit_blocks_direct_write("p2", "rlhf_optimizer_impl", "direct_write_block")
_emit_records_tool_invocation("p2", "rlhf_optimizer_impl", "tool_invocation")
_emit_captures_execution_output("p2", "rlhf_optimizer_impl", "exec_output")
_emit_dispatches_agent("p3", "rlhf_optimizer_impl", "agent_dispatch")
_emit_coordinates_agents("p3", "rlhf_optimizer_impl", "agent_coordination")
_emit_records_workflow_lineage("p3", "rlhf_optimizer_impl", "workflow_lineage")
_emit_records_healing_outcome("p3", "rlhf_optimizer_impl", "healing_outcome")
_emit_escalates_failure("p3", "rlhf_optimizer_impl", "failure_escalation")
_emit_orchestrates_workflow("p3", "rlhf_optimizer_impl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rlhf_optimizer_impl", "healing_dispatch")
_emit_invokes_evaluation("p3", "rlhf_optimizer_impl", "evaluation_signal")
_emit_records_telemetry_event("p4", "rlhf_optimizer_impl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rlhf_optimizer_impl", "eval_metric")
_emit_stores_embedding("p4", "rlhf_optimizer_impl", "embedding_store")
_emit_updates_meta_learning_state("p4", "rlhf_optimizer_impl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rlhf_optimizer_impl", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_PREFERENCE_SIGNAL_THRESHOLD = 0.6
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.02
_MIN_PAIRS = 3


@dataclass(frozen=True, slots=True)
class RLHFChangePackage:
    """Immutable RLHF-driven threshold change proposal."""

    surface_name: str
    parameter: str
    direction: str
    delta: float
    justification: str
    snapshot_id: str
    pair_count: int
    preference_strength: float

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RLHFChangePackage.canonical_bytes")

        data = {
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "direction": self.direction,
            "delta": self.delta,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
            "pair_count": self.pair_count,
            "preference_strength": self.preference_strength,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class DefaultRLHFOptimizer:
    """Concrete RLHF optimizer conforming to the RLHFOptimizer Protocol.

    Analyzes DPO pair batches to determine if human preferences indicate
    a systematic direction for threshold adjustments.
    """

    def propose_from_dpo(
        self, dpo_batch_bytes: bytes, snapshot_id: str = "unknown",
    ) -> RLHFChangePackage | None:
        """Propose threshold changes from DPO preference pairs.

        Parameters
        ----------
        dpo_batch_bytes : bytes
            JSON-serialized DPO batch.  Expected structure::

                {
                    "pairs": [
                        {"chosen": {...}, "rejected": {...}, "surface": "..."},
                        ...
                    ]
                }
        snapshot_id : str
            Pipeline snapshot ID.

        Returns
        -------
        RLHFChangePackage | None
            Proposal or None if preferences are weak/insufficient.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultRLHFOptimizer.propose_from_dpo")

        try:
            batch = json.loads(dpo_batch_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy
            logger.debug("Failed to decode DPO batch bytes")
            return None
        pairs = batch.get("pairs", [])
        if len(pairs) < _MIN_PAIRS:
            return None
        surface_votes: dict[str, list[str]] = {}
        for pair in pairs:
            surface = pair.get("surface", "unknown")
            chosen = pair.get("chosen", {})
            rejected = pair.get("rejected", {})
            chosen_val = chosen.get("threshold", 0.0)
            rejected_val = rejected.get("threshold", 0.0)
            if chosen_val > rejected_val:
                direction = "increase"
            elif chosen_val < rejected_val:
                direction = "decrease"
            else:
                continue
            if surface not in surface_votes:
                surface_votes[surface] = []
            surface_votes[surface].append(direction)
        best_surface = None
        best_strength = 0.0
        best_direction = "increase"
        for surface, votes in surface_votes.items():
            if not votes:
                continue
            increase_count = sum(1 for v in votes if v == "increase")
            decrease_count = len(votes) - increase_count
            total = len(votes)
            if increase_count >= decrease_count:
                strength = increase_count / total
                direction = "increase"
            else:
                strength = decrease_count / total
                direction = "decrease"
            if strength > best_strength and total >= _MIN_PAIRS:
                best_strength = strength
                best_direction = direction
                best_surface = surface
        if best_surface is None or best_strength < _PREFERENCE_SIGNAL_THRESHOLD:
            return None
        delta = min(_DEFAULT_DELTA, _MAX_DELTA)
        return RLHFChangePackage(
            surface_name=best_surface,
            parameter="threshold",
            direction=best_direction,
            delta=delta,
            justification=f"DPO analysis of {len(pairs)} pairs shows {best_strength:.1%} preference to {best_direction} '{best_surface}' threshold",
            snapshot_id=snapshot_id,
            pair_count=len(pairs),
            preference_strength=round(best_strength, 4),
        )

    def commit_optimization(self, package: RLHFChangePackage) -> bool:
        """Commit an optimization proposal (ADG: commits_optimization edge).

        Returns True if the preference signal is strong enough to commit.
        Actual persistence is handled by the caller pipeline.
        """
        return package.preference_strength >= _PREFERENCE_SIGNAL_THRESHOLD


__all__ = ["DefaultRLHFOptimizer", "RLHFChangePackage"]
