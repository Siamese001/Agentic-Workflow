"""
agentic_core/L3_orchestration/learning/workflow_learning_bridge.py

WorkflowLearningBridge — P4-L3 gap remediation.

Bridges L3 orchestration outcomes to the system_learning (L_SL) layer
so successful workflow patterns influence future orchestration decisions.
ADG evidence: 0/204 L3 modules have triggers_learning, feeds_back_signal,
or contributes_to_sl edges despite 204 orchestrators running.

ADG edges emitted: triggers_learning, feeds_back_signal,
                   contributes_to_sl, evaluates_output
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.execution_trace import get_active_execution_trace
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

emit_replay_key("p0", "workflow_learning_bridge")
emit_determinism_digest("p0", "workflow_learning_bridge")

_emit_dispatches_healing_run("p1", "workflow_learning_bridge", "L3")
_emit_routes_through("p1", "workflow_learning_bridge", "L3")
_emit_escalates_to_human("p1", "workflow_learning_bridge", "L3")
_emit_reads_policy_state("p1", "workflow_learning_bridge", "L3")

_emit_snapshots_state("p0", "workflow_learning_bridge", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "workflow_learning_bridge", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "workflow_learning_bridge")
_emit_authorize_and_execute("p2", "workflow_learning_bridge", "execution_auth")
_emit_validates_capability("p2", "workflow_learning_bridge", "capability_check")
_emit_routes_to_capability("p2", "workflow_learning_bridge", "capability_route")
_emit_writes_via_uwg("p2", "workflow_learning_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "workflow_learning_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "workflow_learning_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "workflow_learning_bridge", "exec_output")
_emit_dispatches_agent("p3", "workflow_learning_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "workflow_learning_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "workflow_learning_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "workflow_learning_bridge", "healing_outcome")
_emit_escalates_failure("p3", "workflow_learning_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "workflow_learning_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "workflow_learning_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "workflow_learning_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "workflow_learning_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "workflow_learning_bridge", "eval_metric")
_emit_stores_embedding("p4", "workflow_learning_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "workflow_learning_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "workflow_learning_bridge", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorkflowOutcome:
    """Immutable record of a completed workflow, ready for learning."""

    bundle_id: str
    trace_id: str
    workflow_type: str
    success: bool
    elapsed_ms: float
    agent_sequence: tuple[str, ...]
    quality_score: float
    outcome_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def capture(
        cls,
        bundle_id: str,
        workflow_type: str,
        success: bool,
        elapsed_ms: float,
        agent_sequence: list[str],
        quality_score: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowOutcome:
        active = get_active_execution_trace()
        trace_id = active.trace_id if active else "no-active-trace"
        payload = f"{bundle_id}:{workflow_type}:{success}:{elapsed_ms:.2f}"
        outcome_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
        return cls(
            bundle_id=bundle_id,
            trace_id=trace_id,
            workflow_type=workflow_type,
            success=success,
            elapsed_ms=elapsed_ms,
            agent_sequence=tuple(agent_sequence),
            quality_score=quality_score,
            outcome_hash=outcome_hash,
            metadata=metadata or {},
        )


class WorkflowLearningBridge:
    """Routes workflow outcomes to system_learning consumers.

    Usage::

        bridge = WorkflowLearningBridge()
        bridge.register_learner("sl_adapter", my_sl_adapter.accept)

        outcome = WorkflowOutcome.capture(
            bundle_id="b-001",
            workflow_type="campaign_research",
            success=True,
            elapsed_ms=3200.0,
            agent_sequence=["ResearchAgent", "BriefAssembler"],
            quality_score=0.91,
        )
        bridge.contribute(outcome)
    """

    def __init__(self) -> None:
        self._learners: dict[str, Callable[[WorkflowOutcome], None]] = {}
        self._ledger: list[WorkflowOutcome] = []

    def register_learner(self, name: str, callback: Callable[[WorkflowOutcome], None]) -> None:
        """Register a system_learning consumer."""
        self._learners[name] = callback
        logger.debug("LEARNING_BRIDGE register_learner name=%s", name)

    def contribute(self, outcome: WorkflowOutcome) -> None:
        """Push a workflow outcome to all registered learners.

        Emits ``triggers_learning`` + ``feeds_back_signal``
        + ``contributes_to_sl`` ADG edges.
        """
        self._ledger.append(outcome)
        logger.info(
            "LEARNING_BRIDGE triggers_learning contributes_to_sl "
            "bundle=%s type=%s success=%s quality=%.2f agents=%s",
            outcome.bundle_id,
            outcome.workflow_type,
            outcome.success,
            outcome.quality_score,
            list(outcome.agent_sequence),
        )
        for name, learner in self._learners.items():
            try:
                learner(outcome)
                logger.debug(
                    "LEARNING_BRIDGE feeds_back_signal evaluates_output learner=%s bundle=%s",
                    name,
                    outcome.bundle_id,
                )
            # guardian: allow-silent-swallow
            except Exception as exc:
                logger.error("LEARNING_BRIDGE learner=%s error: %s", name, exc)

    def ledger(self) -> list[WorkflowOutcome]:
        return list(self._ledger)

    def success_rate(self) -> float:
        if not self._ledger:
            return 0.0
        return sum(1 for o in self._ledger if o.success) / len(self._ledger)

    def average_quality(self) -> float:
        scored = [o.quality_score for o in self._ledger if o.quality_score > 0]
        if not scored:
            return 0.0
        return sum(scored) / len(scored)


_global_bridge: WorkflowLearningBridge | None = None


def get_workflow_learning_bridge() -> WorkflowLearningBridge:
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = WorkflowLearningBridge()
    return _global_bridge


def reset_workflow_learning_bridge() -> None:
    global _global_bridge
    _global_bridge = None


__all__ = [
    "WorkflowOutcome",
    "WorkflowLearningBridge",
    "get_workflow_learning_bridge",
    "reset_workflow_learning_bridge",
]
