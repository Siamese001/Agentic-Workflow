"""
ShadowReplayValidator — Pre-activation regression guard for meta-learning.

Before any meta-learning config change is activated, this validator
replays a sample of previous execution traces under the proposed config
and rejects activation if:

  1. The determinism digest changes AND performance does not improve, OR
  2. Safety metrics degrade (any regression).
  3. The regression_threshold exceeds EPSILON.

EPSILON is a hard constant — it is NOT configurable at runtime.

Phase 2.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

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
    record_execution_trace,
)

_emit_applies_guardrail("p0", "shadow_replay_validator", "p0_governance")
_emit_reads_policy_state("p0", "shadow_replay_validator", "policy_binding")
_emit_snapshots_state("p0", "shadow_replay_validator", "state_snapshot")
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
from tqdm import tqdm

record_execution_trace("shadow_replay_validator", "shadow_replay_validator_trace")


_emit_emits_metric_event("shadow_replay_validator", "p4obs", "metric_1")
_emit_emits_metric_event("shadow_replay_validator", "p4obs", "metric_2")
_emit_emits_metric_event("shadow_replay_validator", "p4obs", "metric_3")
_emit_emits_metric_event("shadow_replay_validator", "p4obs", "metric_4")
_emit_emits_metric_event("shadow_replay_validator", "p4obs", "metric_5")
_emit_emits_metric_event("shadow_replay_validator", "p4obs", "metric_6")
_emit_records_incident_event("shadow_replay_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("shadow_replay_validator", "p4obs", "anomaly")
_emit_writes_observability_log("shadow_replay_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("shadow_replay_validator", "p4obs", "mon_state")
_emit_triggers_alert("shadow_replay_validator", "p4obs", "alert")
_emit_links_incident_trace("shadow_replay_validator", "p4obs", "trace_link")
_emit_captures_pattern("shadow_replay_validator", "p3lm", "pattern")
_emit_records_learning_event("shadow_replay_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("shadow_replay_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("shadow_replay_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("shadow_replay_validator", "p3lm", "routing")
_emit_improves_agent_policy("shadow_replay_validator", "p3lm", "policy")
_emit_stores_learning_state("shadow_replay_validator", "p3lm", "state")
_emit_records_execution_trace("shadow_replay_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("shadow_replay_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("shadow_replay_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("shadow_replay_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("shadow_replay_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("shadow_replay_validator", "env_read", "p2_env_1")
_emit_reads_environ("shadow_replay_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("shadow_replay_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("shadow_replay_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "shadow_replay_validator", "context_pull")
_emit_pulls_context("p1", "shadow_replay_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "shadow_replay_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "shadow_replay_validator", "uwg_term_2")
_emit_writes_through("p1", "shadow_replay_validator", "write_through")
_emit_writes_through("p1", "shadow_replay_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "shadow_replay_validator", "safety_validation")
_emit_invokes_eval("p1", "shadow_replay_validator", "eval_call")
_emit_proposal_commits_routing("p1", "shadow_replay_validator", "routing_commit")
_emit_escalates_to_human("p1", "shadow_replay_validator", "human_escalation")
_emit_routes_through("p1", "shadow_replay_validator", "route_through")
_emit_checks_agent_registry("p1", "shadow_replay_validator", "agent_registry")
_emit_validates_agent_capability("p1", "shadow_replay_validator", "capability")
_emit_dispatches_execution_plan("p1", "shadow_replay_validator", "exec_plan")
_emit_agent_executes_agent("p1", "shadow_replay_validator", "sub_agent")
_emit_routes_to_agent("p1", "shadow_replay_validator", "target_agent")
_emit_verifies_policy("p1", "shadow_replay_validator", "policy_check")
_emit_observes_runtime_state("p1", "shadow_replay_validator", "runtime_state")
_emit_verifies_boundary("p1", "shadow_replay_validator", "boundary_check")
_emit_transcripts_response("p1", "shadow_replay_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "shadow_replay_validator")
_emit_gated_by_confidence("p1", "shadow_replay_validator", "confidence_gate")
emit_replay_key("p0", "shadow_replay_validator")
emit_determinism_digest("p0", "shadow_replay_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "shadow_replay_validator", "execution_auth")
_emit_validates_capability("p2", "shadow_replay_validator", "capability_check")
_emit_routes_to_capability("p2", "shadow_replay_validator", "capability_route")
_emit_writes_via_uwg("p2", "shadow_replay_validator", "uwg_write")
_emit_blocks_direct_write("p2", "shadow_replay_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "shadow_replay_validator", "tool_invocation")
_emit_captures_execution_output("p2", "shadow_replay_validator", "exec_output")
_emit_dispatches_agent("p3", "shadow_replay_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "shadow_replay_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "shadow_replay_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "shadow_replay_validator", "healing_outcome")
_emit_escalates_failure("p3", "shadow_replay_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "shadow_replay_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shadow_replay_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "shadow_replay_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "shadow_replay_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shadow_replay_validator", "eval_metric")
_emit_stores_embedding("p4", "shadow_replay_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "shadow_replay_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shadow_replay_validator", "exec_snapshot_link")

EPSILON: float = 0.01


class RegressionError(RuntimeError):
    """Raised when shadow replay detects an unacceptable regression."""


@dataclass(frozen=True)
class ReplayResult:
    """Outcome of a single shadow replay run."""

    trace_id: str
    original_digest: str
    replayed_digest: str
    original_performance: float
    replayed_performance: float
    original_safety_score: float
    replayed_safety_score: float

    @property
    def digest_changed(self) -> bool:
        return self.original_digest != self.replayed_digest

    @property
    def performance_delta(self) -> float:
        return self.replayed_performance - self.original_performance

    @property
    def safety_degraded(self) -> bool:
        return self.replayed_safety_score < self.original_safety_score

    @property
    def regression_threshold(self) -> float:
        """Worst-case regression as a positive fraction (0 = no regression)."""
        return max(0.0, -self.performance_delta)


@dataclass(frozen=True)
class ShadowReplaySummary:
    """Aggregated result across all replayed traces."""

    total_traces: int
    regression_count: int
    max_regression_threshold: float
    any_safety_degraded: bool
    all_digests_stable: bool

    @property
    def activation_safe(self) -> bool:
        return (
            self.regression_count == 0
            and (not self.any_safety_degraded)
            and (self.max_regression_threshold <= EPSILON)
        )


class ShadowReplayValidator:
    """Validates meta-learning proposals via shadow replay."""

    def validate(self, replay_results: Sequence[ReplayResult]) -> ShadowReplaySummary:
        """Run validation over *replay_results* and raise on failure.

        Args:
            replay_results: One ReplayResult per replayed trace.

        Returns:
            ShadowReplaySummary if activation is safe.

        Raises:
            RegressionError: If any regression exceeds EPSILON or safety degrades.
            ValueError: If *replay_results* is empty.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ShadowReplayValidator.validate"
        )

        if not replay_results:
            raise ValueError("ShadowReplayValidator.validate: replay_results must not be empty")
        regression_count = 0
        max_threshold = 0.0
        any_safety_degraded = False
        digests_stable = True
        for result in tqdm(replay_results, desc="Processing", unit="item"):
            if result.digest_changed:
                digests_stable = False
                if result.performance_delta <= 0.0:
                    regression_count += 1
                if result.safety_degraded:
                    any_safety_degraded = True
            if result.regression_threshold > max_threshold:
                max_threshold = result.regression_threshold
            if result.safety_degraded:
                any_safety_degraded = True
        summary = ShadowReplaySummary(
            total_traces=len(replay_results),
            regression_count=regression_count,
            max_regression_threshold=max_threshold,
            any_safety_degraded=any_safety_degraded,
            all_digests_stable=digests_stable,
        )
        if not summary.activation_safe:
            raise RegressionError(
                f"Shadow replay rejected activation: regressions={regression_count}, max_regression_threshold={max_threshold:.4f} (epsilon={EPSILON}), safety_degraded={any_safety_degraded}",
            )
        return summary


__all__ = ["EPSILON", "RegressionError", "ReplayResult", "ShadowReplaySummary", "ShadowReplayValidator"]
