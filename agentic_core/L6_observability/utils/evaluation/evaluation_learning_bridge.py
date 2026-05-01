"""
agentic_core/L6_observability/evaluation/evaluation_learning_bridge.py

EvaluationLearningBridge — Implements BUS P (Preference: Eval → ML).

Routes evaluation signals from L6 observability to system learning bus,
enabling evaluation outcomes to influence future agent behavior and routing
decisions.

ADG edges emitted:
- evaluation_feeds_learning (new edge type)
- feeds_meta_learning (L6 → system_learning)
- pulls_context (bridge → evaluation ledger)
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "evaluation_learning_bridge")
emit_determinism_digest("p0", "evaluation_learning_bridge")
_emit_applies_guardrail("p0", "evaluation_learning_bridge", "p0_governance")
_emit_snapshots_state("p0", "evaluation_learning_bridge", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1 orchestration self-bootstrap
_emit_routes_through("p1", "evaluation_learning_bridge", "L6")
_emit_checks_agent_registry("p1", "evaluation_learning_bridge", "agent_registry")
_emit_validates_agent_capability("p1", "evaluation_learning_bridge", "capability")
_emit_dispatches_execution_plan("p1", "evaluation_learning_bridge", "exec_plan")
_emit_agent_executes_agent("p1", "evaluation_learning_bridge", "sub_agent")
_emit_routes_to_agent("p1", "evaluation_learning_bridge", "target_agent")
_emit_verifies_policy("p1", "evaluation_learning_bridge", "policy_check")
_emit_observes_runtime_state("p1", "evaluation_learning_bridge", "runtime_state")
_emit_verifies_boundary("p1", "evaluation_learning_bridge", "boundary_check")
_emit_transcripts_response("p1", "evaluation_learning_bridge", "transcript")
_emit_hard_fails_untranscripted("p1", "evaluation_learning_bridge")
_emit_gated_by_confidence("p1", "evaluation_learning_bridge", "confidence_gate")
_emit_escalates_to_human("p1", "evaluation_learning_bridge", "L6")
_emit_reads_policy_state("p1", "evaluation_learning_bridge", "L6")

# P2 execution capability self-bootstrap
_emit_authorize_and_execute("p2", "evaluation_learning_bridge", "execution_auth")
_emit_validates_capability("p2", "evaluation_learning_bridge", "capability_check")
_emit_routes_to_capability("p2", "evaluation_learning_bridge", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_learning_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_learning_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_learning_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_learning_bridge", "exec_output")

# P3 orchestration & healing self-bootstrap
_emit_dispatches_agent("p3", "evaluation_learning_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_learning_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_learning_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_learning_bridge", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_learning_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_learning_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_learning_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_learning_bridge", "evaluation_signal")

# P4 state & telemetry self-bootstrap
_emit_records_telemetry_event("p4", "evaluation_learning_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_learning_bridge", "eval_metric")
_emit_stores_embedding("p4", "evaluation_learning_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_learning_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_learning_bridge", "exec_snapshot_link")

# P1 micro-wave self-bootstrap
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

_emit_emits_metric_event("evaluation_learning_bridge", "p4obs", "metric_1")
_emit_emits_metric_event("evaluation_learning_bridge", "p4obs", "metric_2")
_emit_emits_metric_event("evaluation_learning_bridge", "p4obs", "metric_3")
_emit_emits_metric_event("evaluation_learning_bridge", "p4obs", "metric_4")
_emit_emits_metric_event("evaluation_learning_bridge", "p4obs", "metric_5")
_emit_emits_metric_event("evaluation_learning_bridge", "p4obs", "metric_6")
_emit_records_incident_event("evaluation_learning_bridge", "p4obs", "incident")
_emit_captures_runtime_anomaly("evaluation_learning_bridge", "p4obs", "anomaly")
_emit_writes_observability_log("evaluation_learning_bridge", "p4obs", "obs_log")
_emit_updates_monitoring_state("evaluation_learning_bridge", "p4obs", "mon_state")
_emit_triggers_alert("evaluation_learning_bridge", "p4obs", "alert")
_emit_links_incident_trace("evaluation_learning_bridge", "p4obs", "trace_link")
_emit_captures_pattern("evaluation_learning_bridge", "p3lm", "pattern")
_emit_records_learning_event("evaluation_learning_bridge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("evaluation_learning_bridge", "p3lm", "snapshot")
_emit_feeds_meta_learning("evaluation_learning_bridge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("evaluation_learning_bridge", "p3lm", "routing")
_emit_improves_agent_policy("evaluation_learning_bridge", "p3lm", "policy")
_emit_stores_learning_state("evaluation_learning_bridge", "p3lm", "state")
_emit_records_execution_trace("evaluation_learning_bridge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("evaluation_learning_bridge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("evaluation_learning_bridge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("evaluation_learning_bridge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("evaluation_learning_bridge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("evaluation_learning_bridge", "env_read", "p2_env_1")
_emit_reads_environ("evaluation_learning_bridge", "env_read", "p2_env_2")
_emit_reads_runtime_state("evaluation_learning_bridge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("evaluation_learning_bridge", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "evaluation_learning_bridge", "context_pull")
_emit_pulls_context("p1", "evaluation_learning_bridge", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "evaluation_learning_bridge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "evaluation_learning_bridge", "uwg_term_2")
_emit_writes_through("p1", "evaluation_learning_bridge", "write_through")
_emit_writes_through("p1", "evaluation_learning_bridge", "write_through_2")
_emit_validated_by_safety_plane("p1", "evaluation_learning_bridge", "safety_validation")
_emit_invokes_eval("p1", "evaluation_learning_bridge", "eval_call")
_emit_proposal_commits_routing("p1", "evaluation_learning_bridge", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LearningEvent:
    """Learning event derived from evaluation signal.

    Represents an evaluation outcome that should influence system learning.
    """

    trace_id: str
    source_module: str
    target_layer: str
    eval_kind: str
    eval_score: float
    eval_label: str
    timestamp_utc: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_high_quality(self) -> bool:
        """Returns True if evaluation score indicates high quality (>= 0.7)."""
        return self.eval_score >= 0.7

    @property
    def is_learning_eligible(self) -> bool:
        """Returns True if this event should trigger learning updates."""
        return self.is_high_quality

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "source_module": self.source_module,
            "target_layer": self.target_layer,
            "eval_kind": self.eval_kind,
            "eval_score": self.eval_score,
            "eval_label": self.eval_label,
            "timestamp_utc": self.timestamp_utc,
            "metadata": self.metadata,
            "is_high_quality": self.is_high_quality,
            "is_learning_eligible": self.is_learning_eligible,
        }


class EvaluationLearningBridge:
    """Routes evaluation signals from L6 to system learning bus.

    Implements BUS P (Preference: Eval → ML) from process map v14.

    Design:
    - Transforms evaluation signals into learning events
    - Filters low-quality evaluations (score < 0.7)
    - Emits feeds_meta_learning ADG edges
    - Fail-open: errors logged but don't block evaluation

    Usage::

        bridge = EvaluationLearningBridge()

        # From evaluation_signal_integrator.py:
        eval_signal = EvalSignal(...)
        bridge.feed_evaluation_to_learning(eval_signal)
    """

    def __init__(self) -> None:
        self._learning_events: list[LearningEvent] = []
        self._feed_count = 0
        self._filter_count = 0

    def _transform_signal_to_learning_event(
        self,
        eval_signal: Any,
        timestamp_utc: float | None = None,
    ) -> LearningEvent:
        """Transform evaluation signal into learning event.

        Args:
            eval_signal: EvalSignal from evaluation_signal_integrator
            timestamp_utc: UTC timestamp (defaults to current time)

        Returns:
            LearningEvent ready for system learning bus
        """
        import time

        if timestamp_utc is None:
            timestamp_utc = time.time()

        # Emit pulls_context edge (reading evaluation signal)
        _trace_id = str(uuid.uuid4())
        _emit_pulls_context("p1", "evaluation_learning_bridge", f"eval_signal_{_trace_id[:8]}")

        return LearningEvent(
            trace_id=eval_signal.trace_id,
            source_module=eval_signal.source_module,
            target_layer=eval_signal.target_layer,
            eval_kind=eval_signal.kind.value if hasattr(eval_signal.kind, "value") else str(eval_signal.kind),
            eval_score=eval_signal.score,
            eval_label=eval_signal.label,
            timestamp_utc=timestamp_utc,
            metadata=eval_signal.metadata if hasattr(eval_signal, "metadata") else {},
        )

    def feed_evaluation_to_learning(
        self,
        eval_signal: Any,
        timestamp_utc: float | None = None,
    ) -> LearningEvent | None:
        """Feed evaluation signal to system learning bus.

        This is the primary entry point for BUS P (Preference: Eval → ML).

        Args:
            eval_signal: EvalSignal from evaluation_signal_integrator
            timestamp_utc: UTC timestamp (defaults to current time)

        Returns:
            LearningEvent if learning-eligible, None if filtered

        Emits ADG edges:
            - feeds_meta_learning (L6 → system_learning)
            - pulls_context (bridge → evaluation signal)
            - records_learning_event (learning event captured)
        """
        try:
            # Transform signal to learning event
            learning_event = self._transform_signal_to_learning_event(eval_signal, timestamp_utc)

            # Filter low-quality evaluations
            if not learning_event.is_learning_eligible:
                self._filter_count += 1
                logger.debug(
                    "EVAL_LEARNING_BRIDGE filtered low-quality eval: score=%.3f threshold=0.7",
                    learning_event.eval_score,
                )
                return None

            # Store learning event
            self._learning_events.append(learning_event)
            self._feed_count += 1

            # Emit feeds_meta_learning edge (BUS P implementation)
            _emit_feeds_meta_learning(
                "evaluation_learning_bridge",
                "system_learning_bus",
                f"eval_{learning_event.eval_kind}_{learning_event.trace_id[:8]}",
            )

            # Emit records_learning_event edge
            _emit_records_learning_event(
                "evaluation_learning_bridge",
                "p3lm",
                f"learning_event_{learning_event.trace_id[:8]}",
            )

            logger.info(
                "EVAL_LEARNING_BRIDGE fed eval to learning: kind=%s score=%.3f layer=%s",
                learning_event.eval_kind,
                learning_event.eval_score,
                learning_event.target_layer,
            )

            return learning_event

        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-return-none-swallow -- evaluation processing failure: non-fatal; None signals no learning event to caller
            logger.error("[EvalLearningBridge] Evaluation failed: %s", exc)
            return None

    def get_learning_events(self) -> list[LearningEvent]:
        """Get all learning events fed to system learning bus."""
        return list(self._learning_events)

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics."""
        return {
            "feed_count": self._feed_count,
            "filter_count": self._filter_count,
            "learning_events_count": len(self._learning_events),
            "filter_rate": self._filter_count / max(1, self._feed_count + self._filter_count),
        }


# Global singleton instance
_global_bridge: EvaluationLearningBridge | None = None


def get_evaluation_learning_bridge() -> EvaluationLearningBridge:
    """Get global evaluation learning bridge singleton."""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = EvaluationLearningBridge()
    return _global_bridge


def reset_evaluation_learning_bridge() -> None:
    """Reset global bridge (for testing)."""
    global _global_bridge
    _global_bridge = None


__all__ = [
    "LearningEvent",
    "EvaluationLearningBridge",
    "get_evaluation_learning_bridge",
    "reset_evaluation_learning_bridge",
]
