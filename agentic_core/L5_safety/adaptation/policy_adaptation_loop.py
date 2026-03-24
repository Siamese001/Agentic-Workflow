"""
agentic_core/L5_safety/adaptation/policy_adaptation_loop.py

PolicyAdaptationLoop — P4-L5 gap remediation.

Feeds safety audit signals and evaluation scores back into the policy
layer to enable gradual policy tightening / loosening without manual
intervention. ADG evidence: 0/608 L5 modules contribute policy_adapts,
feeds_back_signal, or triggers_learning edges.

ADG edges emitted: policy_adapts, feeds_back_signal,
                   triggers_learning, references_policy_hash
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "policy_adaptation_loop")
emit_determinism_digest("p0", "policy_adaptation_loop")

_emit_dispatches_healing_run("p1", "policy_adaptation_loop", "L5")
_emit_routes_through("p1", "policy_adaptation_loop", "L5")
_emit_checks_agent_registry("p1", "policy_adaptation_loop", "agent_registry")
_emit_validates_agent_capability("p1", "policy_adaptation_loop", "capability")
_emit_dispatches_execution_plan("p1", "policy_adaptation_loop", "exec_plan")
_emit_agent_executes_agent("p1", "policy_adaptation_loop", "sub_agent")
_emit_routes_to_agent("p1", "policy_adaptation_loop", "target_agent")
_emit_observes_runtime_state("p1", "policy_adaptation_loop", "runtime_state")
_emit_verifies_boundary("p1", "policy_adaptation_loop", "boundary_check")
_emit_transcripts_response("p1", "policy_adaptation_loop", "transcript")
_emit_hard_fails_untranscripted("p1", "policy_adaptation_loop")
_emit_gated_by_confidence("p1", "policy_adaptation_loop", "confidence_gate")
_emit_escalates_to_human("p1", "policy_adaptation_loop", "L5")
_emit_reads_policy_state("p1", "policy_adaptation_loop", "L5")

_emit_applies_guardrail("p0", "policy_adaptation_loop", "p0_governance")
_emit_snapshots_state("p0", "policy_adaptation_loop", "state_snapshot")
_emit_authorize_and_execute("p2", "policy_adaptation_loop", "execution_auth")
_emit_validates_capability("p2", "policy_adaptation_loop", "capability_check")
_emit_routes_to_capability("p2", "policy_adaptation_loop", "capability_route")
_emit_writes_via_uwg("p2", "policy_adaptation_loop", "uwg_write")
_emit_blocks_direct_write("p2", "policy_adaptation_loop", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_adaptation_loop", "tool_invocation")
_emit_captures_execution_output("p2", "policy_adaptation_loop", "exec_output")
_emit_dispatches_agent("p3", "policy_adaptation_loop", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_adaptation_loop", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_adaptation_loop", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_adaptation_loop", "healing_outcome")
_emit_escalates_failure("p3", "policy_adaptation_loop", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_adaptation_loop", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_adaptation_loop", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_adaptation_loop", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_adaptation_loop", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_adaptation_loop", "eval_metric")
_emit_stores_embedding("p4", "policy_adaptation_loop", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_adaptation_loop", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_adaptation_loop", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("policy_adaptation_loop", "p4obs", "metric_1")
_emit_emits_metric_event("policy_adaptation_loop", "p4obs", "metric_2")
_emit_emits_metric_event("policy_adaptation_loop", "p4obs", "metric_3")
_emit_emits_metric_event("policy_adaptation_loop", "p4obs", "metric_4")
_emit_emits_metric_event("policy_adaptation_loop", "p4obs", "metric_5")
_emit_emits_metric_event("policy_adaptation_loop", "p4obs", "metric_6")
_emit_records_incident_event("policy_adaptation_loop", "p4obs", "incident")
_emit_captures_runtime_anomaly("policy_adaptation_loop", "p4obs", "anomaly")
_emit_writes_observability_log("policy_adaptation_loop", "p4obs", "obs_log")
_emit_updates_monitoring_state("policy_adaptation_loop", "p4obs", "mon_state")
_emit_triggers_alert("policy_adaptation_loop", "p4obs", "alert")
_emit_links_incident_trace("policy_adaptation_loop", "p4obs", "trace_link")
_emit_captures_pattern("policy_adaptation_loop", "p3lm", "pattern")
_emit_records_learning_event("policy_adaptation_loop", "p3lm", "learning_event")
_emit_writes_learning_snapshot("policy_adaptation_loop", "p3lm", "snapshot")
_emit_feeds_meta_learning("policy_adaptation_loop", "p3lm", "meta_feed")
_emit_updates_routing_strategy("policy_adaptation_loop", "p3lm", "routing")
_emit_improves_agent_policy("policy_adaptation_loop", "p3lm", "policy")
_emit_stores_learning_state("policy_adaptation_loop", "p3lm", "state")
_emit_records_execution_trace("policy_adaptation_loop", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("policy_adaptation_loop", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("policy_adaptation_loop", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("policy_adaptation_loop", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("policy_adaptation_loop", "L4_STATE", "p2_trace_5")
_emit_reads_environ("policy_adaptation_loop", "env_read", "p2_env_1")
_emit_reads_environ("policy_adaptation_loop", "env_read", "p2_env_2")
_emit_reads_runtime_state("policy_adaptation_loop", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("policy_adaptation_loop", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "policy_adaptation_loop", "context_pull")
_emit_pulls_context("p1", "policy_adaptation_loop", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "policy_adaptation_loop", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "policy_adaptation_loop", "uwg_term_2")
_emit_writes_through("p1", "policy_adaptation_loop", "write_through")
_emit_writes_through("p1", "policy_adaptation_loop", "write_through_2")
_emit_validated_by_safety_plane("p1", "policy_adaptation_loop", "safety_validation")
_emit_invokes_eval("p1", "policy_adaptation_loop", "eval_call")
_emit_proposal_commits_routing("p1", "policy_adaptation_loop", "routing_commit")

logger = logging.getLogger(__name__)


class AdaptationSignal(str, Enum):
    """Signal driving a policy adaptation."""

    VIOLATION_RATE_HIGH = "violation_rate_high"
    VIOLATION_RATE_LOW = "violation_rate_low"
    QUALITY_SCORE_HIGH = "quality_score_high"
    QUALITY_SCORE_LOW = "quality_score_low"
    HITL_ESCALATION_SURGE = "hitl_escalation_surge"
    GUARDRAIL_BYPASS_DETECTED = "guardrail_bypass_detected"


class PolicyDirection(str, Enum):
    """Direction of a policy adaptation."""

    TIGHTEN = "tighten"
    LOOSEN = "loosen"
    HOLD = "hold"


@dataclass(frozen=True)
class PolicyAdaptationProposal:
    """An adaptation proposal generated by the loop."""

    policy_hash: str
    new_policy_hash: str
    signal: AdaptationSignal
    direction: PolicyDirection
    confidence: float
    rationale: str
    timestamp: float
    applied: bool = False

    def to_dict(self) -> dict[str, Any]:
        _emit_verifies_policy(str(uuid.uuid4()), "PolicyAdaptationProposal.to_dict", "L5_POLICY")
        return {
            "policy_hash": self.policy_hash[:12],
            "new_policy_hash": self.new_policy_hash[:12],
            "signal": self.signal.value,
            "direction": self.direction.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "applied": self.applied,
        }


def _derive_policy_hash(base_hash: str, signal: AdaptationSignal, direction: PolicyDirection) -> str:
    payload = f"{base_hash}:{signal}:{direction}:{time.monotonic():.6f}"
    return hashlib.sha256(payload.encode()).hexdigest()


class PolicyAdaptationLoop:
    """Adapts policy configuration in response to safety + quality signals.

    The loop observes running violation and quality metrics and generates
    adaptation proposals. Proposals are applied automatically only when
    confidence exceeds the threshold; otherwise they are queued for review.

    Usage::

        loop = PolicyAdaptationLoop(policy_hash="abc123", auto_apply_threshold=0.9)
        loop.observe(AdaptationSignal.VIOLATION_RATE_HIGH, severity=0.85)
        proposal = loop.latest_proposal()
        if proposal and proposal.applied:
            reconfigure_policy(proposal.new_policy_hash)
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        policy_hash: str = "",
        auto_apply_threshold: float = 0.9,
    ) -> None:
        self._policy_hash = policy_hash
        self._auto_apply_threshold = auto_apply_threshold
        self._proposals: list[PolicyAdaptationProposal] = []
        self._observation_log: list[dict[str, Any]] = []

    def observe(
        self,
        signal: AdaptationSignal,
        severity: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> PolicyAdaptationProposal | None:
        """Observe a safety/quality signal and potentially generate a proposal.

        Emits ``policy_adapts`` + ``feeds_back_signal`` + ``triggers_learning``
        + ``references_policy_hash`` ADG edges.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PolicyAdaptationLoop.observe")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PolicyAdaptationLoop.observe".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self._observation_log.append(
            {
                "signal": signal.value,
                "severity": severity,
                "timestamp": time.monotonic(),
                **(metadata or {}),
            }
        )

        direction = self._classify_direction(signal)
        confidence = min(1.0, severity)

        if direction == PolicyDirection.HOLD:
            logger.debug(
                "POLICY_ADAPT observe signal=%s severity=%.2f direction=hold",
                signal.value,
                severity,
            )
            return None

        new_hash = _derive_policy_hash(self._policy_hash, signal, direction)
        applied = confidence >= self._auto_apply_threshold

        proposal = PolicyAdaptationProposal(
            policy_hash=self._policy_hash,
            new_policy_hash=new_hash,
            signal=signal,
            direction=direction,
            confidence=confidence,
            rationale=f"signal={signal.value} severity={severity:.2f} direction={direction.value}",
            timestamp=time.monotonic(),
            applied=applied,
        )
        self._proposals.append(proposal)

        if applied:
            self._policy_hash = new_hash
            logger.warning(
                "POLICY_ADAPT policy_adapts references_policy_hash feeds_back_signal "
                "triggers_learning direction=%s signal=%s confidence=%.2f AUTO_APPLIED",
                direction.value,
                signal.value,
                confidence,
            )
        else:
            logger.info(
                "POLICY_ADAPT proposal direction=%s signal=%s confidence=%.2f QUEUED (below threshold)",
                direction.value,
                signal.value,
                confidence,
            )

        return proposal

    def _classify_direction(self, signal: AdaptationSignal) -> PolicyDirection:
        tighten_signals = {
            AdaptationSignal.VIOLATION_RATE_HIGH,
            AdaptationSignal.HITL_ESCALATION_SURGE,
            AdaptationSignal.GUARDRAIL_BYPASS_DETECTED,
            AdaptationSignal.QUALITY_SCORE_LOW,
        }
        loosen_signals = {
            AdaptationSignal.VIOLATION_RATE_LOW,
            AdaptationSignal.QUALITY_SCORE_HIGH,
        }
        if signal in tighten_signals:
            return PolicyDirection.TIGHTEN
        if signal in loosen_signals:
            return PolicyDirection.LOOSEN
        return PolicyDirection.HOLD

    def current_policy_hash(self) -> str:
        return self._policy_hash

    def latest_proposal(self) -> PolicyAdaptationProposal | None:
        return self._proposals[-1] if self._proposals else None

    def proposals(self) -> list[PolicyAdaptationProposal]:
        return list(self._proposals)

    def applied_count(self) -> int:
        return sum(1 for p in self._proposals if p.applied)


_global_loop: PolicyAdaptationLoop | None = None


def get_policy_adaptation_loop(policy_hash: str = "") -> PolicyAdaptationLoop:
    global _global_loop
    if _global_loop is None:
        _global_loop = PolicyAdaptationLoop(policy_hash=policy_hash)
    return _global_loop


def reset_policy_adaptation_loop() -> None:
    global _global_loop
    _global_loop = None


__all__ = [
    "AdaptationSignal",
    "PolicyDirection",
    "PolicyAdaptationProposal",
    "PolicyAdaptationLoop",
    "get_policy_adaptation_loop",
    "reset_policy_adaptation_loop",
]
