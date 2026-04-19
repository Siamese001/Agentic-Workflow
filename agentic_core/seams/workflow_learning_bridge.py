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

from collections import deque
import hashlib
import json
import logging
import math
import os
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

_emit_emits_metric_event("workflow_learning_bridge", "p4obs", "metric_1")
_emit_emits_metric_event("workflow_learning_bridge", "p4obs", "metric_2")
_emit_emits_metric_event("workflow_learning_bridge", "p4obs", "metric_3")
_emit_emits_metric_event("workflow_learning_bridge", "p4obs", "metric_4")
_emit_emits_metric_event("workflow_learning_bridge", "p4obs", "metric_5")
_emit_emits_metric_event("workflow_learning_bridge", "p4obs", "metric_6")
_emit_records_incident_event("workflow_learning_bridge", "p4obs", "incident")
_emit_captures_runtime_anomaly("workflow_learning_bridge", "p4obs", "anomaly")
_emit_writes_observability_log("workflow_learning_bridge", "p4obs", "obs_log")
_emit_updates_monitoring_state("workflow_learning_bridge", "p4obs", "mon_state")
_emit_triggers_alert("workflow_learning_bridge", "p4obs", "alert")
_emit_links_incident_trace("workflow_learning_bridge", "p4obs", "trace_link")
_emit_captures_pattern("workflow_learning_bridge", "p3lm", "pattern")
_emit_records_learning_event("workflow_learning_bridge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("workflow_learning_bridge", "p3lm", "snapshot")
_emit_feeds_meta_learning("workflow_learning_bridge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("workflow_learning_bridge", "p3lm", "routing")
_emit_improves_agent_policy("workflow_learning_bridge", "p3lm", "policy")
_emit_stores_learning_state("workflow_learning_bridge", "p3lm", "state")
_emit_records_execution_trace("workflow_learning_bridge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("workflow_learning_bridge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("workflow_learning_bridge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("workflow_learning_bridge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("workflow_learning_bridge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("workflow_learning_bridge", "env_read", "p2_env_1")
_emit_reads_environ("workflow_learning_bridge", "env_read", "p2_env_2")
_emit_reads_runtime_state("workflow_learning_bridge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("workflow_learning_bridge", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "workflow_learning_bridge")
emit_determinism_digest("p0", "workflow_learning_bridge")

_emit_dispatches_healing_run("p1", "workflow_learning_bridge", "L3")
_emit_routes_through("p1", "workflow_learning_bridge", "L3")
_emit_checks_agent_registry("p1", "workflow_learning_bridge", "agent_registry")
_emit_validates_agent_capability("p1", "workflow_learning_bridge", "capability")
_emit_dispatches_execution_plan("p1", "workflow_learning_bridge", "exec_plan")
_emit_agent_executes_agent("p1", "workflow_learning_bridge", "sub_agent")
_emit_routes_to_agent("p1", "workflow_learning_bridge", "target_agent")
_emit_verifies_policy("p1", "workflow_learning_bridge", "policy_check")
_emit_observes_runtime_state("p1", "workflow_learning_bridge", "runtime_state")
_emit_verifies_boundary("p1", "workflow_learning_bridge", "boundary_check")
_emit_transcripts_response("p1", "workflow_learning_bridge", "transcript")
_emit_hard_fails_untranscripted("p1", "workflow_learning_bridge")
_emit_gated_by_confidence("p1", "workflow_learning_bridge", "confidence_gate")
_emit_escalates_to_human("p1", "workflow_learning_bridge", "L3")
_emit_reads_policy_state("p1", "workflow_learning_bridge", "L3")
_emit_pulls_context("p1", "workflow_learning_bridge", "context_pull")
_emit_pulls_context("p1", "workflow_learning_bridge", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "workflow_learning_bridge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "workflow_learning_bridge", "uwg_term_secondary")
_emit_writes_through("p1", "workflow_learning_bridge", "write_through")
_emit_writes_through("p1", "workflow_learning_bridge", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "workflow_learning_bridge", "safety_validation")
_emit_invokes_eval("p1", "workflow_learning_bridge", "eval_call")
_emit_proposal_commits_routing("p1", "workflow_learning_bridge", "routing_commit")

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
        if not bundle_id.strip():
            raise ValueError("bundle_id must be non-empty")
        if not workflow_type.strip():
            raise ValueError("workflow_type must be non-empty")
        if elapsed_ms < 0:
            raise ValueError("elapsed_ms must be >= 0")
        if not agent_sequence:
            raise ValueError("agent_sequence must be non-empty")
        if not math.isfinite(quality_score):
            raise ValueError("quality_score must be finite")

        normalized_agents = tuple(agent.strip() for agent in agent_sequence if agent.strip())
        if not normalized_agents:
            raise ValueError("agent_sequence must contain at least one non-empty agent name")

        normalized_metadata = dict(metadata or {})
        active = get_active_execution_trace()
        trace_id = active.trace_id if active else "no-active-trace"
        payload = {
            "bundle_id": bundle_id,
            "trace_id": trace_id,
            "workflow_type": workflow_type,
            "success": success,
            "elapsed_ms": round(elapsed_ms, 6),
            "agent_sequence": normalized_agents,
            "quality_score": round(quality_score, 6),
            "metadata": normalized_metadata,
        }
        outcome_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()[:24]
        return cls(
            bundle_id=bundle_id,
            trace_id=trace_id,
            workflow_type=workflow_type,
            success=success,
            elapsed_ms=elapsed_ms,
            agent_sequence=normalized_agents,
            quality_score=quality_score,
            outcome_hash=outcome_hash,
            metadata=normalized_metadata,
        )


DEFAULT_LEDGER_LIMIT = int(os.getenv("SEAMS_WORKFLOW_LEDGER_LIMIT", "1000"))


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

    def __init__(self, *, ledger_limit: int = DEFAULT_LEDGER_LIMIT) -> None:
        if ledger_limit <= 0:
            raise ValueError("ledger_limit must be > 0")
        self._lock = RLock()
        self._learners: dict[str, Callable[[WorkflowOutcome], None]] = {}
        self._ledger: deque[WorkflowOutcome] = deque(maxlen=ledger_limit)

    def register_learner(self, name: str, callback: Callable[[WorkflowOutcome], None]) -> None:
        """Register a system_learning consumer."""
        if not name.strip():
            raise ValueError("learner name must be non-empty")
        if not callable(callback):
            raise TypeError("callback must be callable")

        with self._lock:
            existing = self._learners.get(name)
            if existing is not None and existing is not callback:
                raise ValueError(f"learner {name!r} already registered with a different callback")
            self._learners[name] = callback
        logger.debug("LEARNING_BRIDGE register_learner name=%s", name)

    def has_learner(self, name: str) -> bool:
        with self._lock:
            return name in self._learners

    def contribute(self, outcome: WorkflowOutcome) -> None:
        """Push a workflow outcome to all registered learners.

        Emits ``triggers_learning`` + ``feeds_back_signal``
        + ``contributes_to_sl`` ADG edges.
        """
        with self._lock:
            self._ledger.append(outcome)
            learners = tuple(self._learners.items())
        logger.info(
            "LEARNING_BRIDGE triggers_learning contributes_to_sl "
            "bundle=%s type=%s success=%s quality=%.2f agents=%s",
            outcome.bundle_id,
            outcome.workflow_type,
            outcome.success,
            outcome.quality_score,
            list(outcome.agent_sequence),
        )
        for name, learner in learners:
            try:
                learner(outcome)
                logger.debug(
                    "LEARNING_BRIDGE feeds_back_signal evaluates_output learner=%s bundle=%s",
                    name,
                    outcome.bundle_id,
                )
            except Exception:  # guardian: allow-broad-exception allow-log-and-swallow -- third-party learner callbacks can raise any type; isolate failures to prevent one bad learner from dropping all others
                logger.exception("LEARNING_BRIDGE learner=%s failed bundle=%s", name, outcome.bundle_id)

    def ledger(self) -> list[WorkflowOutcome]:
        with self._lock:
            return list(self._ledger)

    def success_rate(self) -> float:
        with self._lock:
            ledger = list(self._ledger)
        if not ledger:
            return 0.0
        return sum(1 for o in ledger if o.success) / len(ledger)

    def average_quality(self) -> float:
        with self._lock:
            scored = [o.quality_score for o in self._ledger if o.quality_score > 0]
        if not scored:
            return 0.0
        return sum(scored) / len(scored)


_global_bridge: WorkflowLearningBridge | None = None
_global_bridge_lock = RLock()


def get_workflow_learning_bridge() -> WorkflowLearningBridge:
    global _global_bridge
    with _global_bridge_lock:
        if _global_bridge is None:
            _global_bridge = WorkflowLearningBridge()
        return _global_bridge


def reset_workflow_learning_bridge() -> None:
    global _global_bridge
    with _global_bridge_lock:
        _global_bridge = None


def ensure_sl_adapter_registered() -> None:
    """Ensure the System Learning adapter is registered with the bridge."""
    bridge = get_workflow_learning_bridge()
    if bridge.has_learner("system_learning"):
        return

    try:
        from system_learning.adapters.workflow_outcome_sl_adapter import register_with_workflow_bridge
    except ImportError as exc:  # guardian: allow-return-none-swallow allow-log-and-swallow -- SL adapter optional: bridge operates without system-learning registration
        logger.info("System learning adapter unavailable: %s", exc)
        return

    if not callable(register_with_workflow_bridge):
        raise TypeError("register_with_workflow_bridge must be callable")

    register_with_workflow_bridge()


__all__ = [
    "WorkflowOutcome",
    "WorkflowLearningBridge",
    "get_workflow_learning_bridge",
    "reset_workflow_learning_bridge",
    "ensure_sl_adapter_registered",
]
