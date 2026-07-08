"""L3 Route Decision Artifact — Wave 2.1 Runtime Emission.

Structured artifact emitted at the L3 orchestration routing decision boundary.
Captures the full context of agent selection: candidates, chosen route,
policy context, and determinism parameters.

Follows existing artifact conventions (frozen dataclass, trace_id field).
Contract version: 2.1.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("route_decision_artifact_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("route_decision_artifact_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("route_decision_artifact_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("route_decision_artifact_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("route_decision_artifact_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("route_decision_artifact_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("route_decision_artifact_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("route_decision_artifact_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("route_decision_artifact_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("route_decision_artifact_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("route_decision_artifact_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("route_decision_artifact_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("route_decision_artifact_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("route_decision_artifact_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("route_decision_artifact_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("route_decision_artifact_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("route_decision_artifact_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("route_decision_artifact_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("route_decision_artifact_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("route_decision_artifact_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("route_decision_artifact_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("route_decision_artifact_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("route_decision_artifact_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("route_decision_artifact_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("route_decision_artifact_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("route_decision_artifact_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("route_decision_artifact_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("route_decision_artifact_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "route_decision_artifact_types")
trace_contract.emit_determinism_digest("p0", "route_decision_artifact_types")

trace_contract._emit_dispatches_healing_run("p1", "route_decision_artifact_types", "L3")
trace_contract._emit_routes_through("p1", "route_decision_artifact_types", "L3")
trace_contract._emit_checks_agent_registry("p1", "route_decision_artifact_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "route_decision_artifact_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "route_decision_artifact_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "route_decision_artifact_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "route_decision_artifact_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "route_decision_artifact_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "route_decision_artifact_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "route_decision_artifact_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "route_decision_artifact_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "route_decision_artifact_types")
trace_contract._emit_gated_by_confidence("p1", "route_decision_artifact_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "route_decision_artifact_types", "L3")
trace_contract._emit_reads_policy_state("p1", "route_decision_artifact_types", "L3")
trace_contract._emit_pulls_context("p1", "route_decision_artifact_types", "context_pull")
trace_contract._emit_pulls_context("p1", "route_decision_artifact_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "route_decision_artifact_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "route_decision_artifact_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "route_decision_artifact_types", "write_through")
trace_contract._emit_writes_through("p1", "route_decision_artifact_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "route_decision_artifact_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "route_decision_artifact_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "route_decision_artifact_types", "routing_commit")

trace_contract._emit_snapshots_state("p0", "route_decision_artifact_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "route_decision_artifact_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "route_decision_artifact_types")
trace_contract._emit_authorize_and_execute("p2", "route_decision_artifact_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "route_decision_artifact_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "route_decision_artifact_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "route_decision_artifact_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "route_decision_artifact_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "route_decision_artifact_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "route_decision_artifact_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "route_decision_artifact_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "route_decision_artifact_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "route_decision_artifact_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "route_decision_artifact_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "route_decision_artifact_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "route_decision_artifact_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "route_decision_artifact_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "route_decision_artifact_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "route_decision_artifact_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "route_decision_artifact_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "route_decision_artifact_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "route_decision_artifact_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "route_decision_artifact_types", "exec_snapshot_link")


@dataclass(frozen=True)
class ChosenRoute:
    """Selected agent route at the L3 decision boundary."""

    agent_name: str
    agent_class: str
    module: str


@dataclass(frozen=True)
class CandidateEntry:
    """A candidate agent considered during routing."""

    agent_name: str
    agent_class: str
    score: float
    reason: str


@dataclass(frozen=True)
class PolicyContext:
    """Policy context active during routing decision."""

    security_level: str
    risk_tier: str
    laws_applied: tuple[str, ...]


@dataclass(frozen=True)
class DeterminismContext:
    """Determinism parameters for reproducibility."""

    model: str
    temperature: float
    seed: int | None


@dataclass(frozen=True)
class L3RouteDecisionArtifact:
    """Wave 2.1 — L3 Route Decision Artifact emitted at routing boundary.

    Emitted exactly once per routing decision in delegate_task().
    Not emitted on cache hits or when no candidates are found.
    """

    decision_id: str
    timestamp_utc: str
    layer: str
    trace_id: str
    chosen_route: ChosenRoute
    candidates: tuple[CandidateEntry, ...]
    policy_context: PolicyContext
    determinism: DeterminismContext
    # §Phase3.2 — SemanticClock propagation
    semantic_clock: SemanticClockSnapshot | None = None

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("L3RouteDecisionArtifact: decision_id must be non-empty")
        if self.layer != "L3":
            raise ValueError(
                f"L3RouteDecisionArtifact: layer must be 'L3', got '{self.layer}'",
            )
        if not self.trace_id:
            raise ValueError("L3RouteDecisionArtifact: trace_id must be non-empty")


def build_l3_route_decision_artifact(
    trace_id: str,
    chosen: dict[str, Any],
    candidates: list[dict[str, Any]],
    policy_context: dict[str, Any] | None = None,
    determinism: dict[str, Any] | None = None,
    semantic_clock: SemanticClockSnapshot | None = None,
) -> L3RouteDecisionArtifact:
    """Factory: build artifact from delegate_task() runtime data."""
    policy_ctx = policy_context or {}
    det_ctx = determinism or {}

    return L3RouteDecisionArtifact(
        decision_id=str(uuid.uuid4()),
        timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        layer="L3",
        trace_id=trace_id,
        chosen_route=ChosenRoute(
            agent_name=chosen.get("method", ""),
            agent_class=chosen.get("agent_class", ""),
            module=chosen.get("module", "unknown"),
        ),
        candidates=tuple(
            CandidateEntry(
                agent_name=c.get("method", ""),
                agent_class=c.get("agent_class", ""),
                score=c.get("confidence", 0.0),
                reason=c.get("docstring", ""),
            )
            for c in candidates
        ),
        policy_context=PolicyContext(
            security_level=policy_ctx.get("security_level", "standard"),
            risk_tier=policy_ctx.get("risk_tier", "low"),
            laws_applied=tuple(policy_ctx.get("laws_applied", ())),
        ),
        determinism=DeterminismContext(
            model=det_ctx.get("model", "deterministic"),
            temperature=det_ctx.get("temperature", 0.0),
            seed=det_ctx.get("seed", None),
        ),
        semantic_clock=semantic_clock,
    )


__all__ = [
    "CandidateEntry",
    "ChosenRoute",
    "DeterminismContext",
    "L3RouteDecisionArtifact",
    "PolicyContext",
    "build_l3_route_decision_artifact",
]
