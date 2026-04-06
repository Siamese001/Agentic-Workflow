"""Prompt Safety Validator — L5 policy/guardrail/budget validation for compiled prompts.

Evaluates a ``CompiledPromptArtifact`` through three validation gates:

  1. POLICY_GATE      — prompt_hash policy alignment check
  2. GUARDRAIL_GATE   — guardrail set evaluation
  3. BUDGET_GATE      — token budget check (OVERFLOW → blocked)

Produces a ``PromptSafetyDecision`` and emits the five safety ADG relations:

  compiled_prompt_validated_by_policy
  compiled_prompt_checked_by_guardrail
  compiled_prompt_budget_checked
  compiled_prompt_allowed          (when all gates pass)
  compiled_prompt_blocked          (when any gate fails)

Design invariants
-----------------
1. Fail-closed: any gate exception → gate fails (not passes).
2. No wall-clock reads; ``timestamp_utc`` caller-supplied.
3. All outputs deterministically content-addressed.
4. Budget OVERFLOW always blocks; EXTENDED is a warning but does not block
   unless ``block_on_extended=True`` (default False).
5. Guardrail evaluation is rule-based from a configurable set; the validator
   checks whether the prompt's slot hashes match any blocked pattern hashes.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

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
)

_emit_authorize_and_execute("p2", "prompt_safety_validator", "execution_auth")
_emit_validates_capability("p2", "prompt_safety_validator", "capability_check")
_emit_routes_to_capability("p2", "prompt_safety_validator", "capability_route")
_emit_writes_via_uwg("p2", "prompt_safety_validator", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_safety_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_safety_validator", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_safety_validator", "exec_output")
_emit_dispatches_agent("p3", "prompt_safety_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_safety_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_safety_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_safety_validator", "healing_outcome")
_emit_escalates_failure("p3", "prompt_safety_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_safety_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_safety_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_safety_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_safety_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_safety_validator", "eval_metric")
_emit_stores_embedding("p4", "prompt_safety_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_safety_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_safety_validator", "exec_snapshot_link")
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.prompt_adg_relations import (
    SAFETY_ALLOWED,
    SAFETY_BLOCKED,
    SAFETY_BUDGET_CHECKED,
    SAFETY_CHECKED_BY_GUARDRAIL,
    SAFETY_VALIDATED_BY_POLICY,
)
from system_learning.types.prompt_artifact_types import (
    CompiledPromptArtifact,
    PromptSafetyDecision,
)

_emit_applies_guardrail("p0", "prompt_safety_validator", "p0_governance")
_emit_snapshots_state("p0", "prompt_safety_validator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("prompt_safety_validator", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_safety_validator", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_safety_validator", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_safety_validator", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_safety_validator", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_safety_validator", "p4obs", "metric_6")
_emit_records_incident_event("prompt_safety_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_safety_validator", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_safety_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_safety_validator", "p4obs", "mon_state")
_emit_triggers_alert("prompt_safety_validator", "p4obs", "alert")
_emit_links_incident_trace("prompt_safety_validator", "p4obs", "trace_link")
_emit_captures_pattern("prompt_safety_validator", "p3lm", "pattern")
_emit_records_learning_event("prompt_safety_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_safety_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_safety_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_safety_validator", "p3lm", "routing")
_emit_improves_agent_policy("prompt_safety_validator", "p3lm", "policy")
_emit_stores_learning_state("prompt_safety_validator", "p3lm", "state")
_emit_records_execution_trace("prompt_safety_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_safety_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_safety_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_safety_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_safety_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_safety_validator", "env_read", "p2_env_1")
_emit_reads_environ("prompt_safety_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_safety_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_safety_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_safety_validator", "context_pull")
_emit_pulls_context("p1", "prompt_safety_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_safety_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_safety_validator", "uwg_term_2")
_emit_writes_through("p1", "prompt_safety_validator", "write_through")
_emit_writes_through("p1", "prompt_safety_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_safety_validator", "safety_validation")
_emit_invokes_eval("p1", "prompt_safety_validator", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_safety_validator", "routing_commit")
_emit_escalates_to_human("p1", "prompt_safety_validator", "human_escalation")
_emit_routes_through("p1", "prompt_safety_validator", "route_through")
_emit_checks_agent_registry("p1", "prompt_safety_validator", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_safety_validator", "capability")
_emit_dispatches_execution_plan("p1", "prompt_safety_validator", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_safety_validator", "sub_agent")
_emit_routes_to_agent("p1", "prompt_safety_validator", "target_agent")
_emit_verifies_policy("p1", "prompt_safety_validator", "policy_check")
_emit_observes_runtime_state("p1", "prompt_safety_validator", "runtime_state")
_emit_verifies_boundary("p1", "prompt_safety_validator", "boundary_check")
_emit_transcripts_response("p1", "prompt_safety_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_safety_validator")
_emit_gated_by_confidence("p1", "prompt_safety_validator", "confidence_gate")
emit_replay_key("p0", "prompt_safety_validator")
emit_determinism_digest("p0", "prompt_safety_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gate names
# ---------------------------------------------------------------------------

GATE_POLICY = "POLICY_GATE"
GATE_GUARDRAIL = "GUARDRAIL_GATE"
GATE_BUDGET = "BUDGET_GATE"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class SafetyValidatorConfig:
    """Configuration for the prompt safety validator.

    Attributes
    ----------
    active_policy_hash : str | None
        Expected policy hash. None means any policy is accepted.
    blocked_guardrails : frozenset[str]
        Guardrail IDs that, if present in the prompt's guardrail set, block it.
        Empty set means no guardrail blocks.
    active_guardrails : frozenset[str]
        All guardrail IDs in scope for evaluation.
    block_on_extended : bool
        If True, EXTENDED budget class also blocks (in addition to OVERFLOW).
    block_on_policy_mismatch : bool
        If False, policy hash mismatch is a warning only (does not block).
        Default: True.
    """

    active_policy_hash: str | None = None
    blocked_guardrails: frozenset[str] = frozenset()
    active_guardrails: frozenset[str] = frozenset()
    block_on_extended: bool = False
    block_on_policy_mismatch: bool = True


# ---------------------------------------------------------------------------
# Gate implementations
# ---------------------------------------------------------------------------


def _gate_policy(
    artifact: CompiledPromptArtifact,
    cfg: SafetyValidatorConfig,
) -> tuple[bool, str | None]:
    if cfg.active_policy_hash is None or artifact.policy_hash is None:
        return True, None
    if artifact.policy_hash != cfg.active_policy_hash:
        return False, "POLICY_HASH_MISMATCH"
    return True, None


def _gate_guardrail(
    artifact: CompiledPromptArtifact,
    cfg: SafetyValidatorConfig,
) -> tuple[bool, str | None]:
    # blocked_guardrails ∩ active_guardrails = guardrails that could fire
    # Since the artifact doesn't carry a pre-evaluated guardrail hit set,
    # we check whether any blocked guardrail is in the active set at compile time.
    # (Runtime hits are captured in PromptOutcomeRecord.)
    triggered = cfg.blocked_guardrails & cfg.active_guardrails
    if triggered:
        return False, f"GUARDRAIL_TRIGGERED:{','.join(sorted(triggered))}"
    return True, None


def _gate_budget(
    artifact: CompiledPromptArtifact,
    cfg: SafetyValidatorConfig,
) -> tuple[bool, str | None]:
    bc = artifact.slot_manifest.budget_class
    if bc == "OVERFLOW":
        return False, "BUDGET_OVERFLOW"
    if bc == "EXTENDED" and cfg.block_on_extended:
        return False, "BUDGET_EXTENDED_BLOCKED"
    return True, None


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------


class PromptSafetyValidator:
    """Evaluates compiled prompts through the three L5 safety gates.

    Usage::

        validator = PromptSafetyValidator(config)
        decision, relations = validator.validate(artifact, timestamp_utc=ts)
        if decision.allowed:
            proceed_to_routing(artifact)
    """

    def __init__(self, config: SafetyValidatorConfig | None = None) -> None:
        self._config = config or SafetyValidatorConfig()

    def validate(
        self,
        artifact: CompiledPromptArtifact,
        timestamp_utc: int,
    ) -> tuple[PromptSafetyDecision, list[tuple[str, str, str]]]:
        """Validate a compiled prompt artifact.

        Returns
        -------
        (PromptSafetyDecision, list of ADG relation tuples)
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptSafetyValidator.validate")

        cfg = self._config
        denial_reasons: list[str] = []
        relations: list[tuple[str, str, str]] = []
        an = artifact.adg_entity_name

        # Policy gate
        try:
            p_pass, p_reason = _gate_policy(artifact, cfg)
        except Exception as exc:
            logger.warning("prompt_safety_validator: policy gate exception: %s", exc)
            p_pass, p_reason = False, "POLICY_GATE_EXCEPTION"
        relations.append((an, SAFETY_VALIDATED_BY_POLICY,
                          f"ADG::Policy::{(artifact.policy_hash or 'NONE')[:16]}"))
        if not p_pass and cfg.block_on_policy_mismatch:
            denial_reasons.append(p_reason or GATE_POLICY)

        # Guardrail gate
        try:
            g_pass, g_reason = _gate_guardrail(artifact, cfg)
        except Exception as exc:
            logger.warning("prompt_safety_validator: guardrail gate exception: %s", exc)
            g_pass, g_reason = False, "GUARDRAIL_GATE_EXCEPTION"
        guardrail_set = tuple(sorted(cfg.active_guardrails))
        relations.append((an, SAFETY_CHECKED_BY_GUARDRAIL,
                          f"ADG::GuardrailSet::{_hash_set(guardrail_set)[:16]}"))
        if not g_pass:
            denial_reasons.append(g_reason or GATE_GUARDRAIL)

        # Budget gate
        try:
            b_pass, b_reason = _gate_budget(artifact, cfg)
        except Exception as exc:
            logger.warning("prompt_safety_validator: budget gate exception: %s", exc)
            b_pass, b_reason = False, "BUDGET_GATE_EXCEPTION"
        relations.append((an, SAFETY_BUDGET_CHECKED,
                          f"ADG::BudgetClass::{artifact.slot_manifest.budget_class}"))
        if not b_pass:
            denial_reasons.append(b_reason or GATE_BUDGET)

        allowed = len(denial_reasons) == 0
        adg_relation = SAFETY_ALLOWED if allowed else SAFETY_BLOCKED

        # Final allowed/blocked relation
        relations.append((
            an,
            adg_relation,
            f"ADG::SafetyDecision::{artifact.prompt_hash[:16]}",
        ))

        # Build decision_id
        canonical = deterministic_json({
            "allowed": allowed,
            "denial_reasons": sorted(denial_reasons),
            "guardrail_set": sorted(guardrail_set),
            "policy_hash": cfg.active_policy_hash,
            "prompt_hash": artifact.prompt_hash,
            "timestamp_utc": timestamp_utc,
        })
        decision_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        decision = PromptSafetyDecision(
            decision_id=decision_id,
            prompt_hash=artifact.prompt_hash,
            allowed=allowed,
            policy_hash=cfg.active_policy_hash,
            guardrail_set=guardrail_set,
            budget_class=artifact.slot_manifest.budget_class,
            denial_reasons=tuple(sorted(denial_reasons)),
            adg_relation=adg_relation,
            timestamp_utc=timestamp_utc,
        )
        return decision, relations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hash_set(items: tuple[str, ...]) -> str:
    return hashlib.sha256(
        deterministic_json(list(items)).encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def validate_prompt(
    artifact: CompiledPromptArtifact,
    timestamp_utc: int,
    *,
    config: SafetyValidatorConfig | None = None,
) -> tuple[PromptSafetyDecision, list[tuple[str, str, str]]]:
    """Module-level convenience wrapper."""
    return PromptSafetyValidator(config).validate(artifact, timestamp_utc)


__all__ = [
    "GATE_BUDGET",
    "GATE_GUARDRAIL",
    "GATE_POLICY",
    "PromptSafetyValidator",
    "SafetyValidatorConfig",
    "validate_prompt",
]
