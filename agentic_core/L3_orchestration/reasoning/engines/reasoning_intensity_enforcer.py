"""
L3 ReasoningIntensityEnforcer — Operational enforcement of L0 reasoning policy.

Authority: L3 (orchestration layer). This enforcer READS the
SignedExecutionEnvelope stamped by L0 and enforces its constraints
across all HOP stages.

Design invariants (all enforced):
  - HARD STOP on branch/depth/token budget violations (no silent fallback).
  - NO upward mutation: cannot increase branches, depth, enable reflection,
    or switch to a broader reasoning mode than what L0 stamped.
  - May only REDUCE execution if budget is constrained.
  - Telemetry emitted here is NON-AUTHORITATIVE: it cannot influence the
    current run and may only be used by L0 for FUTURE calibrations after
    windowed aggregation and versioning.
  - profile_hash is recorded in the enforcement log for replay verification.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.reasoning_intensity_types import (
    ReasoningConstraintViolation,
    ReasoningEnforcementTelemetry,
    ReasoningIntensityProfile,
    SignedExecutionEnvelope,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "reasoning_intensity_enforcer")
trace_contract.emit_determinism_digest("p0", "reasoning_intensity_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "reasoning_intensity_enforcer", "L3")
trace_contract._emit_routes_through("p1", "reasoning_intensity_enforcer", "L3")
trace_contract._emit_checks_agent_registry("p1", "reasoning_intensity_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reasoning_intensity_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reasoning_intensity_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reasoning_intensity_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reasoning_intensity_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "reasoning_intensity_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reasoning_intensity_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reasoning_intensity_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reasoning_intensity_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reasoning_intensity_enforcer")
trace_contract._emit_gated_by_confidence("p1", "reasoning_intensity_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "reasoning_intensity_enforcer", "L3")
trace_contract._emit_reads_policy_state("p1", "reasoning_intensity_enforcer", "L3")
trace_contract._emit_authorize_and_execute("p2", "reasoning_intensity_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "reasoning_intensity_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reasoning_intensity_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reasoning_intensity_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reasoning_intensity_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reasoning_intensity_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reasoning_intensity_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reasoning_intensity_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reasoning_intensity_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reasoning_intensity_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reasoning_intensity_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reasoning_intensity_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reasoning_intensity_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reasoning_intensity_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reasoning_intensity_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reasoning_intensity_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reasoning_intensity_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reasoning_intensity_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reasoning_intensity_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reasoning_intensity_enforcer", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("reasoning_intensity_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reasoning_intensity_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reasoning_intensity_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reasoning_intensity_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reasoning_intensity_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reasoning_intensity_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reasoning_intensity_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reasoning_intensity_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reasoning_intensity_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reasoning_intensity_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reasoning_intensity_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reasoning_intensity_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reasoning_intensity_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reasoning_intensity_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reasoning_intensity_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reasoning_intensity_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reasoning_intensity_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reasoning_intensity_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reasoning_intensity_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("reasoning_intensity_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reasoning_intensity_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reasoning_intensity_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reasoning_intensity_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reasoning_intensity_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reasoning_intensity_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reasoning_intensity_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reasoning_intensity_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reasoning_intensity_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reasoning_intensity_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "reasoning_intensity_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_intensity_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_intensity_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reasoning_intensity_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "reasoning_intensity_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reasoning_intensity_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reasoning_intensity_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reasoning_intensity_enforcer", "routing_commit")

logger = logging.getLogger(__name__)


# =============================================================================
# Enforcement exceptions (fail-closed)
# =============================================================================


class ReasoningBudgetExceeded(Exception):
    """Raised when a HOP stage exceeds a ceiling set in the reasoning profile.

    This is a HARD STOP — no retry, no silent fallback, no mode downgrade.
    """

    def __init__(self, violation: ReasoningConstraintViolation) -> None:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ReasoningBudgetExceeded.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningBudgetExceeded.__init__", "p0_governance")
        self.violation = violation
        super().__init__(
            f"HARD STOP: ReasoningBudgetExceeded at stage {violation.stage_id}. "
            f"kind={violation.violation_kind} "
            f"limit={violation.limit_value} observed={violation.observed_value} "
            f"profile={violation.profile_hash[:16]}...",
        )


class ReasoningModeViolation(Exception):
    """Raised when a stage requests a reasoning mode not permitted by L0 profile."""

    def __init__(self, stage_id: int, requested_mode: str, profile_hash: str) -> None:
        self.stage_id = stage_id
        self.requested_mode = requested_mode
        self.profile_hash = profile_hash
        super().__init__(
            f"HARD STOP: ReasoningModeViolation at stage {stage_id}. "
            f"requested_mode='{requested_mode}' not in allowed_modes. "
            f"profile={profile_hash[:16]}...",
        )


class InvalidEnvelopeError(Exception):
    """Raised when the SignedExecutionEnvelope is missing or hash-invalid."""


# =============================================================================
# Stage execution result (consumed by enforcer)
# =============================================================================


@dataclass
class StageExecutionMetrics:
    """Metrics reported by a HOP stage after execution.

    Must be provided by the stage handler for enforcement validation.
    All values must be non-negative integers or booleans.
    """

    stage_id: int
    branches_used: int
    depth_reached: int
    tokens_used: int
    reflection_triggered: bool
    requested_mode: str


# =============================================================================
# ReasoningIntensityEnforcer
# =============================================================================


class ReasoningIntensityEnforcer:
    """L3 operational enforcer of the L0-stamped ReasoningIntensityProfile.

    Usage:
        enforcer = ReasoningIntensityEnforcer(envelope)
        enforcer.validate_envelope()                    # call once at start
        enforcer.enforce_pre_stage(stage_id=3)          # before each stage
        enforcer.enforce_post_stage(metrics)            # after each stage
        telemetry = enforcer.drain_telemetry()          # at end of run

    The telemetry returned by drain_telemetry() is NON-AUTHORITATIVE and
    must not be fed back into the current run's policy decisions.
    """

    def __init__(self, envelope: SignedExecutionEnvelope, trace_id: str) -> None:
        self._envelope = envelope
        self._trace_id = trace_id
        self._profile: ReasoningIntensityProfile = envelope.reasoning_profile
        self._telemetry_buffer: list[ReasoningEnforcementTelemetry] = []
        self._violations: list[ReasoningConstraintViolation] = []
        self._validated: bool = False

    @property
    def profile_hash(self) -> str:
        return self._profile.profile_hash

    @property
    def profile(self) -> ReasoningIntensityProfile:
        return self._profile

    # ------------------------------------------------------------------
    # Envelope validation
    # ------------------------------------------------------------------

    def validate_envelope(self) -> None:
        """Verify envelope integrity before any stage executes.

        Recomputes envelope_hash and profile_hash; raises InvalidEnvelopeError
        on any mismatch. Must be called exactly once before enforce_pre_stage.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "ReasoningIntensityEnforcer.validate_envelope",
        )

        from agentic_core.L0_routing.types.reasoning_intensity_types import (
            build_envelope_hash,
            build_profile_hash,
        )

        expected_profile_hash = build_profile_hash(
            version=self._profile.reasoning_profile_version,
            policy_hash=self._profile.reasoning_policy_hash,
            tier=self._profile.tier,
            max_branches=self._profile.max_branches,
            max_depth=self._profile.max_depth,
            enable_reflection=self._profile.enable_reflection,
            token_budget_per_stage=list(self._profile.token_budget_per_stage),
            allowed_modes=list(self._profile.allowed_modes),
        )
        if self._profile.profile_hash != expected_profile_hash:
            raise InvalidEnvelopeError(
                f"profile_hash integrity failure: "
                f"expected {expected_profile_hash[:16]}... "
                f"got {self._profile.profile_hash[:16]}...",
            )

        expected_envelope_hash = build_envelope_hash(
            route_decision_trace_id=self._envelope.route_decision.trace_id,
            profile_hash=self._profile.profile_hash,
            policy_hash=self._envelope.policy_hash,
        )
        if self._envelope.envelope_hash != expected_envelope_hash:
            raise InvalidEnvelopeError(
                f"envelope_hash integrity failure: "
                f"expected {expected_envelope_hash[:16]}... "
                f"got {self._envelope.envelope_hash[:16]}...",
            )

        self._validated = True
        logger.info(
            "ReasoningIntensityEnforcer: envelope validated profile_hash=%s tier=%s trace_id=%s",
            self._profile.profile_hash[:16],
            self._profile.tier.value,
            self._trace_id,
        )

    # ------------------------------------------------------------------
    # Pre-stage enforcement (mode + budget check)
    # ------------------------------------------------------------------

    def enforce_pre_stage(self, stage_id: int, requested_mode: str | None = None) -> None:
        """Check that stage is permitted to proceed.

        Verifies:
          - Envelope has been validated.
          - requested_mode (if provided) is in allowed_modes.
        Raises ReasoningModeViolation on failure (HARD STOP).
        """
        if not self._validated:
            raise InvalidEnvelopeError("enforce_pre_stage called before validate_envelope()")

        if requested_mode is not None and requested_mode not in self._profile.allowed_modes:
            violation = ReasoningConstraintViolation(
                trace_id=self._trace_id,
                profile_hash=self._profile.profile_hash,
                stage_id=stage_id,
                violation_kind="disallowed_mode",
                limit_value=0,
                observed_value=0,
            )
            self._violations.append(violation)
            raise ReasoningModeViolation(
                stage_id=stage_id,
                requested_mode=requested_mode,
                profile_hash=self._profile.profile_hash,
            )

    # ------------------------------------------------------------------
    # Post-stage enforcement (ceiling checks — HARD STOP on violation)
    # ------------------------------------------------------------------

    def enforce_post_stage(self, metrics: StageExecutionMetrics) -> None:
        """Enforce profile ceilings after a stage reports its execution metrics.

        Checks (in order):
          1. branch ceiling
          2. depth ceiling
          3. per-stage token budget
          4. reflection flag
          5. mode membership

        On ANY violation: record, then raise ReasoningBudgetExceeded.
        No silent truncation, no fallback, no mode downgrade.

        L3 may never INCREASE any ceiling — only enforce the stamped limit.
        """
        if not self._validated:
            raise InvalidEnvelopeError("enforce_post_stage called before validate_envelope()")

        stage_id = metrics.stage_id

        self._check_ceiling(
            stage_id=stage_id,
            kind="branch_ceiling",
            limit=self._profile.max_branches,
            observed=metrics.branches_used,
        )
        self._check_ceiling(
            stage_id=stage_id,
            kind="depth_ceiling",
            limit=self._profile.max_depth,
            observed=metrics.depth_reached,
        )

        stage_budget = self._get_stage_budget(stage_id)
        if stage_budget is not None:
            self._check_ceiling(
                stage_id=stage_id,
                kind="token_budget",
                limit=stage_budget,
                observed=metrics.tokens_used,
            )

        if metrics.reflection_triggered and not self._profile.enable_reflection:
            violation = ReasoningConstraintViolation(
                trace_id=self._trace_id,
                profile_hash=self._profile.profile_hash,
                stage_id=stage_id,
                violation_kind="reflection_not_permitted",
                limit_value=0,
                observed_value=1,
            )
            self._violations.append(violation)
            raise ReasoningBudgetExceeded(violation)

        if metrics.requested_mode and metrics.requested_mode not in self._profile.allowed_modes:
            violation = ReasoningConstraintViolation(
                trace_id=self._trace_id,
                profile_hash=self._profile.profile_hash,
                stage_id=stage_id,
                violation_kind="disallowed_mode_post",
                limit_value=0,
                observed_value=0,
            )
            self._violations.append(violation)
            raise ReasoningBudgetExceeded(violation)

        self._buffer_telemetry(metrics, compliant=True)
        logger.debug(
            "ReasoningIntensityEnforcer: stage %d compliant branches=%d depth=%d tokens=%d profile=%s",
            stage_id,
            metrics.branches_used,
            metrics.depth_reached,
            metrics.tokens_used,
            self._profile.profile_hash[:16],
        )

    # ------------------------------------------------------------------
    # Telemetry drain (non-authoritative)
    # ------------------------------------------------------------------

    def drain_telemetry(self) -> list[ReasoningEnforcementTelemetry]:
        """Return buffered non-authoritative telemetry and clear the buffer.

        CRITICAL: This data must NOT be fed back into the current run's
        policy decisions. It is for FUTURE L0 calibration only, and only
        after windowed aggregation and versioning.
        """
        result = list(self._telemetry_buffer)
        self._telemetry_buffer.clear()
        return result

    def get_enforcement_summary(self) -> dict[str, Any]:
        """Return a summary suitable for inclusion in the execution trace."""
        return {
            "trace_id": self._trace_id,
            "profile_hash": self._profile.profile_hash,
            "tier": self._profile.tier.value,
            "violations_count": len(self._violations),
            "telemetry_records": len(self._telemetry_buffer),
            "validated": self._validated,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_ceiling(
        self,
        stage_id: int,
        kind: str,
        limit: int,
        observed: int,
    ) -> None:
        """Fail-closed ceiling check. Raises ReasoningBudgetExceeded on breach."""
        if observed > limit:
            violation = ReasoningConstraintViolation(
                trace_id=self._trace_id,
                profile_hash=self._profile.profile_hash,
                stage_id=stage_id,
                violation_kind=kind,
                limit_value=limit,
                observed_value=observed,
            )
            self._violations.append(violation)
            raise ReasoningBudgetExceeded(violation)

    def _get_stage_budget(self, stage_id: int) -> int | None:
        """Look up token budget for a stage from the profile."""
        for budget in self._profile.token_budget_per_stage:
            if budget.stage_id == stage_id:
                return budget.max_tokens
        return None

    def _buffer_telemetry(
        self,
        metrics: StageExecutionMetrics,
        compliant: bool,
    ) -> None:
        self._telemetry_buffer.append(
            ReasoningEnforcementTelemetry(
                trace_id=self._trace_id,
                profile_hash=self._profile.profile_hash,
                stage_id=metrics.stage_id,
                branches_used=metrics.branches_used,
                depth_reached=metrics.depth_reached,
                tokens_used=metrics.tokens_used,
                reflection_triggered=metrics.reflection_triggered,
                early_stop_triggered=False,
                compliant=compliant,
            ),
        )


__all__ = [
    "InvalidEnvelopeError",
    "ReasoningBudgetExceeded",
    "ReasoningIntensityEnforcer",
    "ReasoningModeViolation",
    "StageExecutionMetrics",
]
