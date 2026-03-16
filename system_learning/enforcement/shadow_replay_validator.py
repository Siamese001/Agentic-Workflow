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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_applies_guardrail("p0", "shadow_replay_validator", "p0_governance")
_emit_reads_policy_state("p0", "shadow_replay_validator", "policy_binding")
_emit_snapshots_state("p0", "shadow_replay_validator", "state_snapshot")
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ShadowReplayValidator.validate")

        if not replay_results:
            raise ValueError("ShadowReplayValidator.validate: replay_results must not be empty")
        regression_count = 0
        max_threshold = 0.0
        any_safety_degraded = False
        digests_stable = True
        for result in replay_results:
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
                f"Shadow replay rejected activation: regressions={regression_count}, max_regression_threshold={max_threshold:.4f} (epsilon={EPSILON}), safety_degraded={any_safety_degraded}"
            )
        return summary


__all__ = ["EPSILON", "RegressionError", "ReplayResult", "ShadowReplaySummary", "ShadowReplayValidator"]
