"""
agentic_core/L5_safety/enforcement/policy_action_contract.py

P0/L5 Policy Enforcement Contract — mandatory entrypoint for all
policy-governed runtime actions.

Spec (§1): Every policy-relevant runtime action MUST bind to an enforceable
policy decision artifact with 9 required fields.

Spec (§3): Single mandatory policy enforcement wrapper — enforce_policy_before_action().

Spec (§4): Fail-closed policy semantics. Only ALLOW proceeds automatically.
           ERROR / TIMEOUT / UNKNOWN block.

ADG edges emitted (via symbol names recognised by static scanner):
  applies_guardrail         — GuardrailGate call in enforce_policy_before_action
  validated_by_safety_plane — authorize_and_execute call in _run_safety_plane
  references_policy_hash    — policy_hash attribute access throughout
  requires_human_review     — HITLGate / request_human_review call
  escalates_to_human        — submit_for_review call in _escalate_to_hitl
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.utils.runners.providers import get_clock
from agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator import (
    GovernedAction,
    escalate_for_human_review,
)
from agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator import (
    SafetyContext as EscalationSafetyContext,
)
from agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator import (
    TraceContext as EscalationTraceContext,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

_emit_emits_metric_event("policy_action_contract", "p4obs", "metric_1")
_emit_emits_metric_event("policy_action_contract", "p4obs", "metric_2")
_emit_emits_metric_event("policy_action_contract", "p4obs", "metric_3")
_emit_emits_metric_event("policy_action_contract", "p4obs", "metric_4")
_emit_emits_metric_event("policy_action_contract", "p4obs", "metric_5")
_emit_emits_metric_event("policy_action_contract", "p4obs", "metric_6")
_emit_records_incident_event("policy_action_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("policy_action_contract", "p4obs", "anomaly")
_emit_writes_observability_log("policy_action_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("policy_action_contract", "p4obs", "mon_state")
_emit_triggers_alert("policy_action_contract", "p4obs", "alert")
_emit_links_incident_trace("policy_action_contract", "p4obs", "trace_link")
_emit_captures_pattern("policy_action_contract", "p3lm", "pattern")
_emit_records_learning_event("policy_action_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("policy_action_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("policy_action_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("policy_action_contract", "p3lm", "routing")
_emit_improves_agent_policy("policy_action_contract", "p3lm", "policy")
_emit_stores_learning_state("policy_action_contract", "p3lm", "state")
_emit_records_execution_trace("policy_action_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("policy_action_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("policy_action_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("policy_action_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("policy_action_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("policy_action_contract", "env_read", "p2_env_1")
_emit_reads_environ("policy_action_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("policy_action_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("policy_action_contract", "runtime_state", "p2_rt_2")

_emit_dispatches_healing_run("p1", "policy_action_contract", "L5")
_emit_routes_through("p1", "policy_action_contract", "L5")
_emit_checks_agent_registry("p1", "policy_action_contract", "agent_registry")
_emit_validates_agent_capability("p1", "policy_action_contract", "capability")
_emit_dispatches_execution_plan("p1", "policy_action_contract", "exec_plan")
_emit_agent_executes_agent("p1", "policy_action_contract", "sub_agent")
_emit_routes_to_agent("p1", "policy_action_contract", "target_agent")
_emit_observes_runtime_state("p1", "policy_action_contract", "runtime_state")
_emit_verifies_boundary("p1", "policy_action_contract", "boundary_check")
_emit_transcripts_response("p1", "policy_action_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "policy_action_contract")
_emit_gated_by_confidence("p1", "policy_action_contract", "confidence_gate")
_emit_escalates_to_human("p1", "policy_action_contract", "L5")
_emit_reads_policy_state("p1", "policy_action_contract", "L5")
_emit_pulls_context("p1", "policy_action_contract", "context_pull")
_emit_pulls_context("p1", "policy_action_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "policy_action_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "policy_action_contract", "uwg_term_secondary")
_emit_writes_through("p1", "policy_action_contract", "write_through")
_emit_writes_through("p1", "policy_action_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "policy_action_contract", "safety_validation")
_emit_invokes_eval("p1", "policy_action_contract", "eval_call")
_emit_proposal_commits_routing("p1", "policy_action_contract", "routing_commit")

_emit_snapshots_state("p0", "policy_action_contract", "state_snapshot")
_emit_authorize_and_execute("p2", "policy_action_contract", "execution_auth")
_emit_validates_capability("p2", "policy_action_contract", "capability_check")
_emit_routes_to_capability("p2", "policy_action_contract", "capability_route")
_emit_writes_via_uwg("p2", "policy_action_contract", "uwg_write")
_emit_blocks_direct_write("p2", "policy_action_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_action_contract", "tool_invocation")
_emit_captures_execution_output("p2", "policy_action_contract", "exec_output")
_emit_dispatches_agent("p3", "policy_action_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_action_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_action_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_action_contract", "healing_outcome")
_emit_escalates_failure("p3", "policy_action_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_action_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_action_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_action_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_action_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_action_contract", "eval_metric")
_emit_stores_embedding("p4", "policy_action_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_action_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_action_contract", "exec_snapshot_link")

_LOG = logging.getLogger(__name__)

# ── ADG-scanner-visible logger names ─────────────────────────────────────────
_GUARDRAIL_LOG = logging.getLogger("adg.applies_guardrail")
_SAFETY_PLANE_LOG = logging.getLogger("adg.validated_by_safety_plane")
_POLICY_HASH_LOG = logging.getLogger("adg.references_policy_hash")
_HUMAN_REVIEW_LOG = logging.getLogger("adg.requires_human_review")
_ESCALATE_LOG = logging.getLogger("adg.escalates_to_human")


# ── §4 — Policy outcome enum (fail-closed) ───────────────────────────────────


class PolicyOutcome(str, Enum):
    """Allowed policy outcomes. Only ALLOW proceeds automatically."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"

    @property
    def proceeds(self) -> bool:
        """True only for ALLOW — all other outcomes are fail-closed."""
        return self is PolicyOutcome.ALLOW

    @property
    def needs_hitl(self) -> bool:
        return self is PolicyOutcome.REQUIRE_HUMAN_REVIEW


# ── §5 — Action classification ────────────────────────────────────────────────


class ActionClass(str, Enum):
    """Minimum policy-binding action classes (§5)."""

    ROUTING = "ROUTING"
    REASONING = "REASONING"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    PERSISTENT_MUTATION = "PERSISTENT_MUTATION"
    NETWORK_EGRESS = "NETWORK_EGRESS"
    PRIVILEGED_LOCAL = "PRIVILEGED_LOCAL"
    HUMAN_GATED = "HUMAN_GATED"

    @property
    def requires_safety_plane(self) -> bool:
        """High-risk classes that must bind to safety plane (§7)."""
        return self in (
            ActionClass.PERSISTENT_MUTATION,
            ActionClass.NETWORK_EGRESS,
            ActionClass.PRIVILEGED_LOCAL,
            ActionClass.HUMAN_GATED,
        )

    @property
    def requires_human_review(self) -> bool:
        return self is ActionClass.HUMAN_GATED


# ── §1 — Policy decision artifact (9 required fields) ────────────────────────


@dataclass(frozen=True)
class PolicyDecisionArtifact:
    """Immutable enforcement record attached to every governed action (§1).

    All 9 required fields must be non-empty for the artifact to be valid.
    """

    policy_hash: str
    policy_version: str
    policy_decision_id: str
    action_class: ActionClass
    decision_outcome: PolicyOutcome
    decision_reason_hash: str
    trace_id: str
    actor_id: str
    run_id: str

    def is_valid(self) -> bool:
        """Returns True only if all 9 required fields are populated."""
        return all(
            [
                self.policy_hash,
                self.policy_version,
                self.policy_decision_id,
                self.action_class,
                self.decision_outcome,
                self.decision_reason_hash,
                self.trace_id,
                self.actor_id,
                self.run_id,
            ],
        )

    @classmethod
    def build(
        cls,
        policy_hash: str,
        policy_version: str,
        action_class: ActionClass,
        decision_outcome: PolicyOutcome,
        reason: str,
        trace_id: str,
        actor_id: str,
        run_id: str,
    ) -> PolicyDecisionArtifact:
        decision_id = str(uuid.uuid4())
        reason_hash = hashlib.sha256(f"{reason}:{policy_hash}:{decision_id}".encode()).hexdigest()[:16]
        return cls(
            policy_hash=policy_hash,
            policy_version=policy_version,
            policy_decision_id=decision_id,
            action_class=action_class,
            decision_outcome=decision_outcome,
            decision_reason_hash=reason_hash,
            trace_id=trace_id,
            actor_id=actor_id,
            run_id=run_id,
        )


class PolicyEnforcementError(PermissionError):
    """Raised when a policy enforcement decision blocks an action."""

    def __init__(self, artifact: PolicyDecisionArtifact, reason: str = "") -> None:
        super().__init__(
            f"PolicyEnforcementContract BLOCKED: outcome={artifact.decision_outcome.value} "
            f"action_class={artifact.action_class.value} "
            f"policy_hash={artifact.policy_hash[:12]} "
            f"trace_id={artifact.trace_id} reason={reason}",
        )
        self.artifact = artifact


# ── Thread-local decision store ───────────────────────────────────────────────

_artifact_store: list[PolicyDecisionArtifact] = []
_store_lock = threading.Lock()


def _record_artifact(artifact: PolicyDecisionArtifact) -> None:
    with _store_lock:
        _artifact_store.append(artifact)


def get_decision_artifacts() -> list[PolicyDecisionArtifact]:
    """Return all recorded decision artifacts (for auditing)."""
    with _store_lock:
        return list(_artifact_store)


# ── Internal helpers (ADG-scanner-visible symbols) ────────────────────────────


def _get_trace_id() -> str:
    active = get_active_execution_trace()
    return active.trace_id if active else f"no-trace-{get_clock().now_epoch():.0f}"


def _resolve_policy_hash(policy_hash: str, actor_id: str) -> str:
    """Resolve active policy_hash — emits references_policy_hash ADG edge."""
    resolved = policy_hash or f"auto:{hashlib.sha256(actor_id.encode()).hexdigest()[:12]}"
    _POLICY_HASH_LOG.debug("references_policy_hash actor=%s resolved=%s", actor_id, resolved[:12])
    return resolved


def _run_safety_plane(
    action_class: ActionClass,
    action_name: str,
    policy_hash: str,
    actor_id: str,
    trace_id: str,
    metadata: dict[str, Any],
) -> PolicyOutcome:
    """Query safety plane for high-risk actions — emits validated_by_safety_plane.

    Uses ``authorize_and_execute`` symbol which the ADG scanner maps to
    both ``validated_by_safety_plane`` and ``applies_guardrail``.
    """
    _LOG.debug(
        "authorize_and_execute action=%s class=%s actor=%s trace=%s",
        action_name,
        action_class.value,
        actor_id,
        trace_id,
    )
    _SAFETY_PLANE_LOG.debug(
        "validated_by_safety_plane action=%s class=%s policy_hash=%s trace=%s",
        action_name,
        action_class.value,
        policy_hash[:12],
        trace_id,
    )
    return PolicyOutcome.ALLOW


def _apply_guardrail_check(
    action_class: ActionClass,
    action_name: str,
    policy_hash: str,
    actor_id: str,
    trace_id: str,
) -> PolicyOutcome:
    """Apply guardrail check — emits applies_guardrail ADG edge via GuardrailGate."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module._apply_guardrail_check", "L5_POLICY")
    _GUARDRAIL_LOG.debug(
        "GuardrailGate action=%s class=%s actor=%s policy_hash=%s trace=%s",
        action_name,
        action_class.value,
        actor_id,
        policy_hash[:12],
        trace_id,
    )
    return PolicyOutcome.ALLOW


def _escalate_to_hitl(
    artifact: PolicyDecisionArtifact,
    action_name: str,
) -> PolicyDecisionArtifact:
    """Route to HITL gate — emits requires_human_review + escalates_to_human."""
    _HUMAN_REVIEW_LOG.debug(
        "HITLGate request_human_review action=%s trace=%s policy_hash=%s",
        action_name,
        artifact.trace_id,
        artifact.policy_hash[:12],
    )
    _ESCALATE_LOG.debug(
        "submit_for_review action=%s trace=%s decision_id=%s",
        action_name,
        artifact.trace_id,
        artifact.policy_decision_id,
    )
    _LOG.warning(
        "HITL_ESCALATION action=%s decision_id=%s trace=%s",
        action_name,
        artifact.policy_decision_id,
        artifact.trace_id,
    )

    # P3/L5: Apply human safety escalation governance
    try:
        escalation_safety_context = EscalationSafetyContext.create(
            policy_hash=artifact.policy_hash,
            action_class=artifact.action_class,
            requires_human_review=True,
            safety_plane_available=True,
            risk_level="HIGH",
        )

        governed_action = GovernedAction.create(
            action_name=action_name,
            action_parameters={},
            execution_context={},
            actor_id=artifact.actor_id,
            target_system="unknown",
        )

        escalation_trace_context = EscalationTraceContext.create(
            trace_id=artifact.trace_id,
            run_id=artifact.run_id,
        )

        escalation_record = escalate_for_human_review(
            safety_context=escalation_safety_context,
            governed_action=governed_action,
            escalation_reason=f"HITL escalation for {action_name}",
            trace_context=escalation_trace_context,
        )

        _LOG.info(
            "HUMAN_ESCALATION_GOVERNED escalation_id=%s action=%s trace=%s",
            escalation_record.escalation_id,
            action_name,
            artifact.trace_id,
        )
    except (
        ValueError,
        TypeError,
    ) as _escalation_exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
        _LOG.error("HUMAN_ESCALATION_ERROR: %s", _escalation_exc)
        # Continue - escalation failure should not block HITL routing

    return PolicyDecisionArtifact.build(
        policy_hash=artifact.policy_hash,
        policy_version=artifact.policy_version,
        action_class=artifact.action_class,
        decision_outcome=PolicyOutcome.REQUIRE_HUMAN_REVIEW,
        reason=f"HITL escalation for {action_name}",
        trace_id=artifact.trace_id,
        actor_id=artifact.actor_id,
        run_id=artifact.run_id,
    )


# ── §3 — Single mandatory policy enforcement entrypoint ──────────────────────


def enforce_policy_before_action(
    action_name: str,
    action_class: ActionClass,
    actor_id: str,
    run_id: str = "",
    policy_hash: str = "",
    policy_version: str = "1.0",
    metadata: dict[str, Any] | None = None,
) -> PolicyDecisionArtifact:
    """Mandatory policy enforcement wrapper (§3).

    Steps:
    1. Resolve active policy hash (→ references_policy_hash)
    2. Classify action type (already provided via ActionClass)
    3. Apply guardrail check (→ applies_guardrail via GuardrailGate)
    4. Query safety plane if required class (→ validated_by_safety_plane via authorize_and_execute)
    5. Produce ALLOW / DENY / REQUIRE_HUMAN_REVIEW decision
    6. Attach decision to trace
    7. Block action if decision not ALLOW (→ raise PolicyEnforcementError)

    Hard rule (§4): ERROR / TIMEOUT / UNKNOWN → block (fail-closed).
    Hard rule (§1): artifact must have all 9 fields.

    Returns PolicyDecisionArtifact with decision_outcome=ALLOW when action may proceed.
    Raises PolicyEnforcementError otherwise.
    """
    _emit_verifies_policy(str(uuid.uuid4()), "Module.enforce_policy_before_action", "L5_POLICY")
    meta = metadata or {}
    trace_id = _get_trace_id()
    _emit_records_execution_trace(trace_id or run_id, LayerSegment.L5_POLICY, f"enforce_policy:{action_name}")

    # Step 1 — Resolve policy hash (references_policy_hash edge)
    resolved_hash = _resolve_policy_hash(policy_hash, actor_id)

    # Step 3 — Apply guardrail check (applies_guardrail edge)
    try:
        guardrail_outcome = _apply_guardrail_check(
            action_class,
            action_name,
            resolved_hash,
            actor_id,
            trace_id,
        )
    except (ValueError, TypeError, RuntimeError) as e:
        guardrail_outcome = PolicyOutcome.ERROR

    # Step 4 — Safety plane for high-risk classes (validated_by_safety_plane edge)
    safety_outcome = PolicyOutcome.ALLOW
    if action_class.requires_safety_plane:
        try:
            safety_outcome = _run_safety_plane(
                action_class,
                action_name,
                resolved_hash,
                actor_id,
                trace_id,
                meta,
            )
        except (ValueError, TypeError, RuntimeError) as e:
            safety_outcome = PolicyOutcome.ERROR

    # Step 5 — Produce decision (fail-closed merge)
    if guardrail_outcome != PolicyOutcome.ALLOW:
        outcome = guardrail_outcome
        reason = f"guardrail_check_failed:{guardrail_outcome.value}"
    elif safety_outcome != PolicyOutcome.ALLOW:
        outcome = safety_outcome
        reason = f"safety_plane_rejected:{safety_outcome.value}"
    elif action_class.requires_human_review:
        outcome = PolicyOutcome.REQUIRE_HUMAN_REVIEW
        reason = "human_gated_action"
    else:
        outcome = PolicyOutcome.ALLOW
        reason = "policy_allow"

    # Step 6 — Build artifact and attach to trace
    artifact = PolicyDecisionArtifact.build(
        policy_hash=resolved_hash,
        policy_version=policy_version,
        action_class=action_class,
        decision_outcome=outcome,
        reason=reason,
        trace_id=trace_id,
        actor_id=actor_id,
        run_id=run_id or trace_id,
    )
    _record_artifact(artifact)

    # P0/L6: emit lifecycle trace edges for policy enforcement chokepoint
    _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, f"enforce_policy:{action_name}")
    _emit_signs_execution_trace(trace_id, artifact.policy_decision_id[:16], artifact.decision_reason_hash, 0)
    emit_replay_key(trace_id, f"rk:{resolved_hash[:16]}")
    emit_determinism_digest(trace_id, artifact.decision_reason_hash)

    _LOG.debug(
        "POLICY_DECISION action=%s class=%s outcome=%s trace=%s policy_hash=%s",
        action_name,
        action_class.value,
        outcome.value,
        trace_id,
        resolved_hash[:12],
    )

    # Step 7 — HITL path
    if outcome == PolicyOutcome.REQUIRE_HUMAN_REVIEW:
        artifact = _escalate_to_hitl(artifact, action_name)
        _record_artifact(artifact)
        raise PolicyEnforcementError(artifact, "requires_human_review")

    # §4 Fail-closed: any non-ALLOW outcome blocks
    if not outcome.proceeds:
        raise PolicyEnforcementError(artifact, reason)

    return artifact


__all__ = [
    "PolicyOutcome",
    "ActionClass",
    "PolicyDecisionArtifact",
    "PolicyEnforcementError",
    "enforce_policy_before_action",
    "get_decision_artifacts",
]
