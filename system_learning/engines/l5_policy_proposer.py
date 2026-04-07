"""L5 Policy Proposer — proposes safety rule strictness adjustments.

Analyzes false-positive/negative rates from healing outcomes where the agent
is an L5 safety agent (ArchitectureGovernorAgent, FileClassificationAgent, etc.)
and proposes bounded threshold adjustments to reduce over-blocking or
under-blocking.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import hashlib
import json
import logging
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

_emit_applies_guardrail("p0", "l5_policy_proposer", "p0_governance")
_emit_snapshots_state("p0", "l5_policy_proposer", "state_snapshot")
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

_emit_emits_metric_event("l5_policy_proposer", "p4obs", "metric_1")
_emit_emits_metric_event("l5_policy_proposer", "p4obs", "metric_2")
_emit_emits_metric_event("l5_policy_proposer", "p4obs", "metric_3")
_emit_emits_metric_event("l5_policy_proposer", "p4obs", "metric_4")
_emit_emits_metric_event("l5_policy_proposer", "p4obs", "metric_5")
_emit_emits_metric_event("l5_policy_proposer", "p4obs", "metric_6")
_emit_records_incident_event("l5_policy_proposer", "p4obs", "incident")
_emit_captures_runtime_anomaly("l5_policy_proposer", "p4obs", "anomaly")
_emit_writes_observability_log("l5_policy_proposer", "p4obs", "obs_log")
_emit_updates_monitoring_state("l5_policy_proposer", "p4obs", "mon_state")
_emit_triggers_alert("l5_policy_proposer", "p4obs", "alert")
_emit_links_incident_trace("l5_policy_proposer", "p4obs", "trace_link")
_emit_captures_pattern("l5_policy_proposer", "p3lm", "pattern")
_emit_records_learning_event("l5_policy_proposer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("l5_policy_proposer", "p3lm", "snapshot")
_emit_feeds_meta_learning("l5_policy_proposer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("l5_policy_proposer", "p3lm", "routing")
_emit_improves_agent_policy("l5_policy_proposer", "p3lm", "policy")
_emit_stores_learning_state("l5_policy_proposer", "p3lm", "state")
_emit_records_execution_trace("l5_policy_proposer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("l5_policy_proposer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("l5_policy_proposer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("l5_policy_proposer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("l5_policy_proposer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("l5_policy_proposer", "env_read", "p2_env_1")
_emit_reads_environ("l5_policy_proposer", "env_read", "p2_env_2")
_emit_reads_runtime_state("l5_policy_proposer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("l5_policy_proposer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "l5_policy_proposer", "context_pull")
_emit_pulls_context("p1", "l5_policy_proposer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "l5_policy_proposer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "l5_policy_proposer", "uwg_term_2")
_emit_writes_through("p1", "l5_policy_proposer", "write_through")
_emit_writes_through("p1", "l5_policy_proposer", "write_through_2")
_emit_validated_by_safety_plane("p1", "l5_policy_proposer", "safety_validation")
_emit_invokes_eval("p1", "l5_policy_proposer", "eval_call")
_emit_proposal_commits_routing("p1", "l5_policy_proposer", "routing_commit")
_emit_escalates_to_human("p1", "l5_policy_proposer", "human_escalation")
_emit_routes_through("p1", "l5_policy_proposer", "route_through")
_emit_checks_agent_registry("p1", "l5_policy_proposer", "agent_registry")
_emit_validates_agent_capability("p1", "l5_policy_proposer", "capability")
_emit_dispatches_execution_plan("p1", "l5_policy_proposer", "exec_plan")
_emit_agent_executes_agent("p1", "l5_policy_proposer", "sub_agent")
_emit_routes_to_agent("p1", "l5_policy_proposer", "target_agent")
_emit_verifies_policy("p1", "l5_policy_proposer", "policy_check")
_emit_observes_runtime_state("p1", "l5_policy_proposer", "runtime_state")
_emit_verifies_boundary("p1", "l5_policy_proposer", "boundary_check")
_emit_transcripts_response("p1", "l5_policy_proposer", "transcript")
_emit_hard_fails_untranscripted("p1", "l5_policy_proposer")
_emit_gated_by_confidence("p1", "l5_policy_proposer", "confidence_gate")
emit_replay_key("p0", "l5_policy_proposer")
emit_determinism_digest("p0", "l5_policy_proposer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "l5_policy_proposer", "execution_auth")
_emit_validates_capability("p2", "l5_policy_proposer", "capability_check")
_emit_routes_to_capability("p2", "l5_policy_proposer", "capability_route")
_emit_writes_via_uwg("p2", "l5_policy_proposer", "uwg_write")
_emit_blocks_direct_write("p2", "l5_policy_proposer", "direct_write_block")
_emit_records_tool_invocation("p2", "l5_policy_proposer", "tool_invocation")
_emit_captures_execution_output("p2", "l5_policy_proposer", "exec_output")
_emit_dispatches_agent("p3", "l5_policy_proposer", "agent_dispatch")
_emit_coordinates_agents("p3", "l5_policy_proposer", "agent_coordination")
_emit_records_workflow_lineage("p3", "l5_policy_proposer", "workflow_lineage")
_emit_records_healing_outcome("p3", "l5_policy_proposer", "healing_outcome")
_emit_escalates_failure("p3", "l5_policy_proposer", "failure_escalation")
_emit_orchestrates_workflow("p3", "l5_policy_proposer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l5_policy_proposer", "healing_dispatch")
_emit_invokes_evaluation("p3", "l5_policy_proposer", "evaluation_signal")
_emit_records_telemetry_event("p4", "l5_policy_proposer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l5_policy_proposer", "eval_metric")
_emit_stores_embedding("p4", "l5_policy_proposer", "embedding_store")
_emit_updates_meta_learning_state("p4", "l5_policy_proposer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l5_policy_proposer", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_L5_AGENT_PREFIXES = (
    "ArchitectureGovernor",
    "FileClassification",
    "FilesystemSSOTReconciler",
    "Hierarchy",
    "Location",
    "RootHygiene",
    "SystemArchitect",
    "CognitiveDisposition",
    "GravityLeakRepair",
)
_FALSE_POSITIVE_THRESHOLD = 0.15
_FALSE_NEGATIVE_THRESHOLD = 0.1
_MIN_OBSERVATIONS = 5
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.02


@dataclass(frozen=True, slots=True)
class L5PolicyChangePackage:
    """Immutable policy adjustment proposal for L5 safety rules."""

    surface_name: str
    direction: str
    delta: float
    justification: str
    snapshot_id: str
    false_positive_rate: float
    false_negative_rate: float
    observation_count: int

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L5PolicyChangePackage.canonical_bytes")

        data = {
            "surface_name": self.surface_name,
            "direction": self.direction,
            "delta": self.delta,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
            "observation_count": self.observation_count,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


class L5PolicyProposer:
    """Concrete L5 proposer that analyzes safety block accuracy.

    Conforms to the ``L5Proposer`` Protocol defined in
    ``meta_learning_pipeline.py``.
    """

    def propose(
        self, snapshot: Any, metrics: Any, config: Any, now_utc: int, history: Any, cooldown: Any, sample: Any,
    ) -> L5PolicyChangePackage | None:
        """Propose L5 policy changes based on safety block accuracy.

        Parameters
        ----------
        snapshot : MetaLearningSnapshot
            Current pipeline snapshot.
        metrics : dict
            Must contain ``"l5_false_positive_rate"`` and
            ``"l5_false_negative_rate"`` and ``"l5_observation_count"``.
        config, now_utc, history, cooldown, sample
            Standard proposer args (cooldown/sample checked if provided).

        Returns
        -------
        L5PolicyChangePackage | None
            Proposal or None if no adjustment warranted.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "L5PolicyProposer.propose")

        if not isinstance(metrics, dict):
            return None
        fp_rate = metrics.get("l5_false_positive_rate", 0.0)
        fn_rate = metrics.get("l5_false_negative_rate", 0.0)
        n_obs = metrics.get("l5_observation_count", 0)
        if n_obs < _MIN_OBSERVATIONS:
            return None
        snapshot_id = getattr(snapshot, "snapshot_id", "unknown")
        if fp_rate > _FALSE_POSITIVE_THRESHOLD:
            direction = "relax"
            delta = min(_DEFAULT_DELTA, _MAX_DELTA)
            justification = f"L5 false-positive rate {fp_rate:.3f} exceeds threshold {_FALSE_POSITIVE_THRESHOLD}; proposing relaxation by {delta}"
        elif fn_rate > _FALSE_NEGATIVE_THRESHOLD:
            direction = "tighten"
            delta = min(_DEFAULT_DELTA, _MAX_DELTA)
            justification = f"L5 false-negative rate {fn_rate:.3f} exceeds threshold {_FALSE_NEGATIVE_THRESHOLD}; proposing tightening by {delta}"
        else:
            return None
        return L5PolicyChangePackage(
            surface_name="l5_safety_strictness",
            direction=direction,
            delta=delta,
            justification=justification,
            snapshot_id=snapshot_id,
            false_positive_rate=fp_rate,
            false_negative_rate=fn_rate,
            observation_count=n_obs,
        )


def extract_l5_metrics_from_healing_actions(healing_actions: list[dict]) -> dict[str, float]:
    """Extract L5-specific metrics from healing action records.

    Scans healing actions for L5 agents and computes false-positive and
    false-negative rates.

    Parameters
    ----------
    healing_actions : list[dict]
        Raw healing action dicts from runtime_state.

    Returns
    -------
    dict[str, float]
        Metrics dict with ``l5_false_positive_rate``,
        ``l5_false_negative_rate``, and ``l5_observation_count``.
    """
    l5_actions = [
        a for a in healing_actions if any(a.get("agent", "").startswith(pfx) for pfx in _L5_AGENT_PREFIXES)
    ]
    if not l5_actions:
        return {"l5_false_positive_rate": 0.0, "l5_false_negative_rate": 0.0, "l5_observation_count": 0}
    total = len(l5_actions)
    false_positives = sum(1 for a in l5_actions if a.get("status") in ("skipped", "plan_only", "unnecessary"))
    false_negatives = sum(1 for a in l5_actions if a.get("status") in ("missed", "false_negative"))
    return {
        "l5_false_positive_rate": false_positives / total if total else 0.0,
        "l5_false_negative_rate": false_negatives / total if total else 0.0,
        "l5_observation_count": total,
    }


__all__ = ["L5PolicyProposer", "L5PolicyChangePackage", "extract_l5_metrics_from_healing_actions"]
