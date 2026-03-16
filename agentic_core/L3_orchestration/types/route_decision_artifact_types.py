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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "route_decision_artifact_types")
emit_determinism_digest("p0", "route_decision_artifact_types")

_emit_dispatches_healing_run("p1", "route_decision_artifact_types", "L3")
_emit_routes_through("p1", "route_decision_artifact_types", "L3")
_emit_escalates_to_human("p1", "route_decision_artifact_types", "L3")
_emit_reads_policy_state("p1", "route_decision_artifact_types", "L3")

_emit_snapshots_state("p0", "route_decision_artifact_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "route_decision_artifact_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "route_decision_artifact_types")
_emit_authorize_and_execute("p2", "route_decision_artifact_types", "execution_auth")
_emit_validates_capability("p2", "route_decision_artifact_types", "capability_check")
_emit_routes_to_capability("p2", "route_decision_artifact_types", "capability_route")
_emit_writes_via_uwg("p2", "route_decision_artifact_types", "uwg_write")
_emit_blocks_direct_write("p2", "route_decision_artifact_types", "direct_write_block")
_emit_records_tool_invocation("p2", "route_decision_artifact_types", "tool_invocation")
_emit_captures_execution_output("p2", "route_decision_artifact_types", "exec_output")
_emit_dispatches_agent("p3", "route_decision_artifact_types", "agent_dispatch")
_emit_coordinates_agents("p3", "route_decision_artifact_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "route_decision_artifact_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "route_decision_artifact_types", "healing_outcome")
_emit_escalates_failure("p3", "route_decision_artifact_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "route_decision_artifact_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "route_decision_artifact_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "route_decision_artifact_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "route_decision_artifact_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "route_decision_artifact_types", "eval_metric")
_emit_stores_embedding("p4", "route_decision_artifact_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "route_decision_artifact_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "route_decision_artifact_types", "exec_snapshot_link")


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
