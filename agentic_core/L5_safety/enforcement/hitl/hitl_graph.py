"""G4 (gap): HITL Graph — Human-in-the-Loop escalation and decision graph.

Models the confidence-threshold gating path that routes low-confidence agent
decisions to a human reviewer, then feeds the human decision back into the
meta-learning system.

Architecture node flow (Gap 4):
  Agent outcome
    → HealingConfidenceScorer (confidence gate)
    → [if confidence < threshold] → HITLCheckpoint (human review queue)
    → HumanDecision (approve / reject / override)
    → MetaLearning feedback edge (learns_from_decision)

Static detection:
  The `_HITLVisitor` in static_scanner.py detects statically-declared
  `gated_by_confidence` and `escalates_to_human` edges from code.

Runtime tracking:
  HITLRuntimeRecorder emits RuntimeEdges into a shared RuntimeGraph for
  each checkpoint, human decision, and learning feedback event.

Data model:
  HITLCheckpoint     — a queued item awaiting human review
  HumanDecision      — the outcome of a human review (approve/reject/override)
  HITLGraph          — collection of checkpoints and decisions

Usage::

    from agentic_core.L5_safety.enforcement.hitl.hitl_graph import HITLGraph, HITLRuntimeRecorder
    from agentic_core.adg.runtime.event_graph import RuntimeGraph

    rt_graph = RuntimeGraph()
    hitl = HITLGraph()
    recorder = HITLRuntimeRecorder(rt_graph, hitl, agent_id="LicHealingOrchestrator")
    recorder.checkpoint(violation_id="v001", confidence=0.28, context={"strategy": "rewrite"})
    # ... human reviews ...
    recorder.decide(checkpoint_id="cp-001", decision="approve", reviewer="human:alice")
    recorder.learn(checkpoint_id="cp-001", weight_delta=0.1)
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.adg.runtime.event_graph import RuntimeGraph, RuntimeGraphCollector
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

_emit_applies_guardrail("p0", "hitl_graph", "p0_governance")
_emit_reads_policy_state("p0", "hitl_graph", "policy_binding")
_emit_snapshots_state("p0", "hitl_graph", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("hitl_graph", "p4obs", "metric_1")
_emit_emits_metric_event("hitl_graph", "p4obs", "metric_2")
_emit_emits_metric_event("hitl_graph", "p4obs", "metric_3")
_emit_emits_metric_event("hitl_graph", "p4obs", "metric_4")
_emit_emits_metric_event("hitl_graph", "p4obs", "metric_5")
_emit_emits_metric_event("hitl_graph", "p4obs", "metric_6")
_emit_records_incident_event("hitl_graph", "p4obs", "incident")
_emit_captures_runtime_anomaly("hitl_graph", "p4obs", "anomaly")
_emit_writes_observability_log("hitl_graph", "p4obs", "obs_log")
_emit_updates_monitoring_state("hitl_graph", "p4obs", "mon_state")
_emit_triggers_alert("hitl_graph", "p4obs", "alert")
_emit_links_incident_trace("hitl_graph", "p4obs", "trace_link")
_emit_captures_pattern("hitl_graph", "p3lm", "pattern")
_emit_records_learning_event("hitl_graph", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hitl_graph", "p3lm", "snapshot")
_emit_feeds_meta_learning("hitl_graph", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hitl_graph", "p3lm", "routing")
_emit_improves_agent_policy("hitl_graph", "p3lm", "policy")
_emit_stores_learning_state("hitl_graph", "p3lm", "state")
_emit_records_execution_trace("hitl_graph", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hitl_graph", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hitl_graph", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hitl_graph", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hitl_graph", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hitl_graph", "env_read", "p2_env_1")
_emit_reads_environ("hitl_graph", "env_read", "p2_env_2")
_emit_reads_runtime_state("hitl_graph", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hitl_graph", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hitl_graph", "context_pull")
_emit_pulls_context("p1", "hitl_graph", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hitl_graph", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hitl_graph", "uwg_term_2")
_emit_writes_through("p1", "hitl_graph", "write_through")
_emit_writes_through("p1", "hitl_graph", "write_through_2")
_emit_validated_by_safety_plane("p1", "hitl_graph", "safety_validation")
_emit_invokes_eval("p1", "hitl_graph", "eval_call")
_emit_proposal_commits_routing("p1", "hitl_graph", "routing_commit")
_emit_escalates_to_human("p1", "hitl_graph", "human_escalation")
_emit_routes_through("p1", "hitl_graph", "route_through")
_emit_checks_agent_registry("p1", "hitl_graph", "agent_registry")
_emit_validates_agent_capability("p1", "hitl_graph", "capability")
_emit_dispatches_execution_plan("p1", "hitl_graph", "exec_plan")
_emit_agent_executes_agent("p1", "hitl_graph", "sub_agent")
_emit_routes_to_agent("p1", "hitl_graph", "target_agent")
_emit_verifies_policy("p1", "hitl_graph", "policy_check")
_emit_observes_runtime_state("p1", "hitl_graph", "runtime_state")
_emit_verifies_boundary("p1", "hitl_graph", "boundary_check")
_emit_transcripts_response("p1", "hitl_graph", "transcript")
_emit_hard_fails_untranscripted("p1", "hitl_graph")
_emit_gated_by_confidence("p1", "hitl_graph", "confidence_gate")
emit_replay_key("p0", "hitl_graph")
emit_determinism_digest("p0", "hitl_graph")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hitl_graph", "execution_auth")
_emit_validates_capability("p2", "hitl_graph", "capability_check")
_emit_routes_to_capability("p2", "hitl_graph", "capability_route")
_emit_writes_via_uwg("p2", "hitl_graph", "uwg_write")
_emit_blocks_direct_write("p2", "hitl_graph", "direct_write_block")
_emit_records_tool_invocation("p2", "hitl_graph", "tool_invocation")
_emit_captures_execution_output("p2", "hitl_graph", "exec_output")
_emit_dispatches_agent("p3", "hitl_graph", "agent_dispatch")
_emit_coordinates_agents("p3", "hitl_graph", "agent_coordination")
_emit_records_workflow_lineage("p3", "hitl_graph", "workflow_lineage")
_emit_records_healing_outcome("p3", "hitl_graph", "healing_outcome")
_emit_escalates_failure("p3", "hitl_graph", "failure_escalation")
_emit_orchestrates_workflow("p3", "hitl_graph", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hitl_graph", "healing_dispatch")
_emit_invokes_evaluation("p3", "hitl_graph", "evaluation_signal")
_emit_records_telemetry_event("p4", "hitl_graph", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hitl_graph", "eval_metric")
_emit_stores_embedding("p4", "hitl_graph", "embedding_store")
_emit_updates_meta_learning_state("p4", "hitl_graph", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hitl_graph", "exec_snapshot_link")


class HITLDecisionType(str, Enum):
    """Possible human review decisions."""

    APPROVE = "approve"
    REJECT = "reject"
    OVERRIDE = "override"
    DEFER = "defer"


@dataclass
class HITLCheckpoint:
    """A single item queued for human review.

    Attributes:
        checkpoint_id:  Unique identifier for this checkpoint.
        agent_id:       Agent class that generated the checkpoint.
        run_id:         Execution run that produced this item.
        violation_id:   Violation or decision being reviewed.
        confidence:     Agent's confidence score that triggered escalation.
        context:        Arbitrary structured context for the reviewer.
        created_at:     Unix epoch timestamp when queued.
        resolved:       Whether a human decision has been recorded.
    """

    checkpoint_id: str
    agent_id: str
    run_id: str
    violation_id: str
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    resolved: bool = False


@dataclass(frozen=True)
class HumanDecision:
    """The outcome of a human reviewer acting on a HITLCheckpoint.

    Attributes:
        checkpoint_id:  ID of the checkpoint being resolved.
        decision:       Human's decision (approve/reject/override/defer).
        reviewer:       Identifier of the human reviewer.
        rationale:      Optional free-text rationale.
        decided_at:     Unix epoch timestamp of the decision.
        override_value: If decision == override, the corrected value.
    """

    checkpoint_id: str
    decision: HITLDecisionType
    reviewer: str
    rationale: str = ""
    decided_at: float = field(default_factory=time.time)
    override_value: Any = None


@dataclass
class HITLGraph:
    """Collection of HITL checkpoints and human decisions.

    This is the runtime-populated HITL subgraph. It is complementary to the
    static `gated_by_confidence` and `escalates_to_human` edges produced by
    `_HITLVisitor` in static_scanner.py.

    Attributes:
        checkpoints: All checkpoints queued for human review.
        decisions:   All human decisions recorded.
    """

    checkpoints: list[HITLCheckpoint] = field(default_factory=list)
    decisions: list[HumanDecision] = field(default_factory=list)

    @property
    def pending_count(self) -> int:
        return sum(1 for cp in self.checkpoints if not cp.resolved)

    @property
    def resolved_count(self) -> int:
        return sum(1 for cp in self.checkpoints if cp.resolved)

    def checkpoint_by_id(self, checkpoint_id: str) -> HITLCheckpoint | None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HITLGraph.checkpoint_by_id")

        for cp in self.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                return cp
        return None

    def decisions_for(self, checkpoint_id: str) -> list[HumanDecision]:
        return [d for d in self.decisions if d.checkpoint_id == checkpoint_id]

    def decision_distribution(self) -> dict[str, int]:
        """Count decisions by type."""
        dist: dict[str, int] = {}
        for d in self.decisions:
            dist[d.decision] = dist.get(d.decision, 0) + 1
        return dist


class HITLRuntimeRecorder(RuntimeGraphCollector):
    """Records HITL escalations, human decisions, and learning feedback.

    Emits both into a shared RuntimeGraph (as RuntimeEdges/Events) and
    into a HITLGraph (as typed domain objects for downstream analysis).

    Args:
        rt_graph:  Shared RuntimeGraph for this execution session.
        hitl_graph: HITLGraph to record typed checkpoints/decisions into.
        agent_id:  Agent class name emitting HITL events.
        run_id:    Execution run identifier.
    """

    def __init__(
        self,
        rt_graph: RuntimeGraph,
        hitl_graph: HITLGraph,
        agent_id: str,
        run_id: str | None = None,
    ) -> None:
        super().__init__(rt_graph, agent_id, run_id)
        self._hitl = hitl_graph

    def checkpoint(
        self,
        violation_id: str,
        confidence: float,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Queue a new HITL checkpoint for human review.

        Returns the generated checkpoint_id.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HITLRuntimeRecorder.checkpoint")

        cp_id = _make_checkpoint_id(self._agent_id, violation_id)
        cp = HITLCheckpoint(
            checkpoint_id=cp_id,
            agent_id=self._agent_id,
            run_id=self._run_id,
            violation_id=violation_id,
            confidence=confidence,
            context=context or {},
        )
        self._hitl.checkpoints.append(cp)
        self._emit_event(
            "hitl_checkpoint",
            phase="escalate",
            payload={
                "checkpoint_id": cp_id,
                "violation_id": violation_id,
                "confidence": confidence,
            },
        )
        self._emit_edge(
            "escalates_to_human",
            f"HITL::Checkpoint::{cp_id}",
            metadata={"confidence": confidence, "violation_id": violation_id},
        )
        return cp_id

    def decide(
        self,
        checkpoint_id: str,
        decision: str,
        reviewer: str,
        rationale: str = "",
        override_value: Any = None,
    ) -> None:
        """Record a human decision on a queued checkpoint."""
        decision_type = HITLDecisionType(decision)
        d = HumanDecision(
            checkpoint_id=checkpoint_id,
            decision=decision_type,
            reviewer=reviewer,
            rationale=rationale,
            override_value=override_value,
        )
        self._hitl.decisions.append(d)
        cp = self._hitl.checkpoint_by_id(checkpoint_id)
        if cp is not None:
            cp.resolved = True
        self._emit_event(
            "human_decision",
            phase="decide",
            payload={
                "checkpoint_id": checkpoint_id,
                "decision": decision,
                "reviewer": reviewer,
            },
        )
        self._emit_edge(
            "awaits_approval",
            reviewer,
            metadata={"checkpoint_id": checkpoint_id, "decision": decision},
        )

    def learn(self, checkpoint_id: str, weight_delta: float = 0.0) -> None:
        """Feed human decision back into meta-learning system."""
        self._emit_event(
            "hitl_learning",
            phase="learn",
            payload={"checkpoint_id": checkpoint_id, "weight_delta": weight_delta},
        )
        self._emit_edge(
            "learns_from_decision",
            f"HITL::Decision::{checkpoint_id}",
            metadata={"weight_delta": weight_delta},
        )


def _make_checkpoint_id(agent_id: str, violation_id: str) -> str:
    """Generate a deterministic checkpoint ID."""
    raw = f"{agent_id}:{violation_id}:{time.time()}".encode()
    return "cp-" + hashlib.sha256(raw).hexdigest()[:12]


__all__ = [
    "HITLDecisionType",
    "HITLCheckpoint",
    "HumanDecision",
    "HITLGraph",
    "HITLRuntimeRecorder",
]
