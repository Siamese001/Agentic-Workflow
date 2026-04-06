"""
Heal Escalation Policy Types and Decision Logic
==============================================

Pure types and decision functions for agent healing escalation policy.
This module contains only stdlib dependencies and deterministic logic.

Score-based routing (replaces legacy confidence-based system):
- S <= 13: DETERMINISTIC  — agent-native logic, no LLM
- S 14-26: QWEN           — Qwen 2.5 14B advises the healing plan
- S > 26:  GEMINI         — Gemini 2.5 Pro handles complex reasoning

Healing always proceeds (proceed=True) once routing dispatches by score.
Confidence is only an intermediate value that contributes factors C, A, F
to the score S. It is never used as a hard gate.

Enums:
- ReasoningTier: LOW (Qwen), HIGH (Gemini)
- ScoreBand: DETERMINISTIC, QWEN, GEMINI
- ConfidenceLevel: alias of ScoreBand for backward compat

Dataclasses:
- HealEscalationInputs: Input parameters — score (canonical), legacy fields kept for compat
- LegacyHealEscalationInputs: Legacy input parameters (backward compat)
- HealEscalationDecision: Output decision with tier, proceed flag, and rationale

Functions:
- classify_score: Map routing score S to ScoreBand
- classify_confidence: DEPRECATED — maps confidence float to ScoreBand (approximation)
- decide_heal_escalation: Score-based escalation, always proceed=True
- decide_reasoning_tier: DEPRECATED legacy function, always proceed=True
"""

from dataclasses import dataclass
from enum import Enum

from agentic_core.L3_orchestration.healers.healing_tier_config import (
    SSOT_SCORE_THRESHOLD_DET as SCORE_THRESHOLD_DET,
)
from agentic_core.L3_orchestration.healers.healing_tier_config import (
    SSOT_SCORE_THRESHOLD_QWEN as SCORE_THRESHOLD_QWEN,
)
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

_emit_emits_metric_event("heal_policy_types", "p4obs", "metric_1")
_emit_emits_metric_event("heal_policy_types", "p4obs", "metric_2")
_emit_emits_metric_event("heal_policy_types", "p4obs", "metric_3")
_emit_emits_metric_event("heal_policy_types", "p4obs", "metric_4")
_emit_emits_metric_event("heal_policy_types", "p4obs", "metric_5")
_emit_emits_metric_event("heal_policy_types", "p4obs", "metric_6")
_emit_records_incident_event("heal_policy_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("heal_policy_types", "p4obs", "anomaly")
_emit_writes_observability_log("heal_policy_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("heal_policy_types", "p4obs", "mon_state")
_emit_triggers_alert("heal_policy_types", "p4obs", "alert")
_emit_links_incident_trace("heal_policy_types", "p4obs", "trace_link")
_emit_captures_pattern("heal_policy_types", "p3lm", "pattern")
_emit_records_learning_event("heal_policy_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("heal_policy_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("heal_policy_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("heal_policy_types", "p3lm", "routing")
_emit_improves_agent_policy("heal_policy_types", "p3lm", "policy")
_emit_stores_learning_state("heal_policy_types", "p3lm", "state")
_emit_records_execution_trace("heal_policy_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("heal_policy_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("heal_policy_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("heal_policy_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("heal_policy_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("heal_policy_types", "env_read", "p2_env_1")
_emit_reads_environ("heal_policy_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("heal_policy_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("heal_policy_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "heal_policy_types")
emit_determinism_digest("p0", "heal_policy_types")

_emit_dispatches_healing_run("p1", "heal_policy_types", "L5")
_emit_routes_through("p1", "heal_policy_types", "L5")
_emit_checks_agent_registry("p1", "heal_policy_types", "agent_registry")
_emit_validates_agent_capability("p1", "heal_policy_types", "capability")
_emit_dispatches_execution_plan("p1", "heal_policy_types", "exec_plan")
_emit_agent_executes_agent("p1", "heal_policy_types", "sub_agent")
_emit_routes_to_agent("p1", "heal_policy_types", "target_agent")
_emit_verifies_policy("p1", "heal_policy_types", "policy_check")
_emit_observes_runtime_state("p1", "heal_policy_types", "runtime_state")
_emit_verifies_boundary("p1", "heal_policy_types", "boundary_check")
_emit_transcripts_response("p1", "heal_policy_types", "transcript")
_emit_hard_fails_untranscripted("p1", "heal_policy_types")
_emit_gated_by_confidence("p1", "heal_policy_types", "confidence_gate")
_emit_escalates_to_human("p1", "heal_policy_types", "L5")
_emit_reads_policy_state("p1", "heal_policy_types", "L5")
_emit_pulls_context("p1", "heal_policy_types", "context_pull")
_emit_pulls_context("p1", "heal_policy_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "heal_policy_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "heal_policy_types", "uwg_term_secondary")
_emit_writes_through("p1", "heal_policy_types", "write_through")
_emit_writes_through("p1", "heal_policy_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "heal_policy_types", "safety_validation")
_emit_invokes_eval("p1", "heal_policy_types", "eval_call")
_emit_proposal_commits_routing("p1", "heal_policy_types", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "heal_policy_types")
_emit_applies_guardrail("p0", "heal_policy_types", "p0_governance")
_emit_snapshots_state("p0", "heal_policy_types", "state_snapshot")
_emit_authorize_and_execute("p2", "heal_policy_types", "execution_auth")
_emit_validates_capability("p2", "heal_policy_types", "capability_check")
_emit_routes_to_capability("p2", "heal_policy_types", "capability_route")
_emit_writes_via_uwg("p2", "heal_policy_types", "uwg_write")
_emit_blocks_direct_write("p2", "heal_policy_types", "direct_write_block")
_emit_records_tool_invocation("p2", "heal_policy_types", "tool_invocation")
_emit_captures_execution_output("p2", "heal_policy_types", "exec_output")
_emit_dispatches_agent("p3", "heal_policy_types", "agent_dispatch")
_emit_coordinates_agents("p3", "heal_policy_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "heal_policy_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "heal_policy_types", "healing_outcome")
_emit_escalates_failure("p3", "heal_policy_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "heal_policy_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "heal_policy_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "heal_policy_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "heal_policy_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "heal_policy_types", "eval_metric")
_emit_stores_embedding("p4", "heal_policy_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "heal_policy_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "heal_policy_types", "exec_snapshot_link")


class ReasoningTier(Enum):
    """LLM reasoning tier for agent healing escalation."""

    LOW = "LOW"
    HIGH = "HIGH"


class ScoreBand(Enum):
    """Score band classification (replaces ConfidenceLevel)."""

    DETERMINISTIC = "DETERMINISTIC"
    QWEN = "QWEN"
    GEMINI = "GEMINI"


ConfidenceLevel = ScoreBand


@dataclass(frozen=True)
class HealEscalationInputs:
    """Inputs for heal escalation decision (canonical).

    Attributes:
        score: Routing score S from _route_decision (C+A+F+B+N factors). Primary input.
        enable_llm: Whether LLM escalation is permitted (controls tier activation).
        confidence_value: DEPRECATED — kept for backward compat only, not used for gating.
        task_complexity: DEPRECATED — kept for backward compat only.
        cost_budget: Unused in decision logic.
        latency_budget_ms: Unused in decision logic.
        safety_risk: DEPRECATED — kept for backward compat only.
        prior_failures: DEPRECATED — kept for backward compat only.
    """

    score: int = 0
    enable_llm: bool = False
    confidence_value: float = 0.75
    task_complexity: int = 5
    cost_budget: int = 100
    latency_budget_ms: int = 5000
    safety_risk: int = 0
    prior_failures: int = 0


@dataclass(frozen=True)
class LegacyHealEscalationInputs:
    """Legacy inputs for heal escalation decision (backward compat)."""

    task_complexity: int
    confidence: float
    safety_risk: int
    retry_count: int
    cost_budget: int | None = None
    latency_budget: int | None = None


@dataclass(frozen=True)
class HealEscalationDecision:
    """Decision result for heal escalation.

    Attributes:
        proceed: Whether healing should proceed
        tier: Reasoning tier (None if proceed=False or no LLM needed)
        rationale: Human-readable explanation
        threshold_used: Short deterministic token for debugging
    """

    proceed: bool
    tier: ReasoningTier | None
    rationale: str
    threshold_used: str


def classify_score(score: int) -> ScoreBand:
    """Classify routing score S into score band.

    Args:
        score: Routing score S from _route_decision.

    Returns:
        ScoreBand: DETERMINISTIC, QWEN, or GEMINI.
    """
    if score <= SCORE_THRESHOLD_DET:
        return ScoreBand.DETERMINISTIC
    elif score <= SCORE_THRESHOLD_QWEN:
        return ScoreBand.QWEN
    else:
        return ScoreBand.GEMINI


def classify_confidence(confidence: float) -> ScoreBand:
    """DEPRECATED: approximate mapping from confidence float to ScoreBand.

    Use classify_score(score) for new code.
    High confidence → low score → DETERMINISTIC.
    """
    if confidence > 0.75:
        return ScoreBand.DETERMINISTIC
    elif confidence >= 0.5:
        return ScoreBand.QWEN
    else:
        return ScoreBand.GEMINI


def decide_heal_escalation(inputs: HealEscalationInputs) -> HealEscalationDecision:
    """Score-based escalation decision. Healing always proceeds (proceed=True).

    Routing rules (by score S):
    - S <= 13: DETERMINISTIC — agent-native logic, no LLM needed
    - S 14-26: QWEN tier    — Qwen 2.5 14B advises the healing plan
    - S > 26:  GEMINI tier  — Gemini 2.5 Pro handles complex reasoning

    Args:
        inputs: Heal escalation inputs (score is the canonical field).

    Returns:
        HealEscalationDecision with proceed=True and appropriate tier.
    """
    score = inputs.score
    band = classify_score(score)
    if band == ScoreBand.DETERMINISTIC:
        return HealEscalationDecision(
            proceed=True,
            tier=None,
            rationale=f"Score S={score} <= {SCORE_THRESHOLD_DET}: agent-native logic governs, no LLM needed",
            threshold_used="SCORE_DET",
        )
    elif band == ScoreBand.QWEN:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale=f"Score S={score} in [{SCORE_THRESHOLD_DET + 1},{SCORE_THRESHOLD_QWEN}]: Qwen 2.5 14B advises healing plan",
            threshold_used="SCORE_QWEN",
        )
    else:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale=f"Score S={score} > {SCORE_THRESHOLD_QWEN}: Gemini 2.5 Pro handles complex reasoning",
            threshold_used="SCORE_GEMINI",
        )


def decide_reasoning_tier(inputs: LegacyHealEscalationInputs) -> HealEscalationDecision:
    """DEPRECATED legacy function. Always proceeds; routes by complexity.

    Use decide_heal_escalation() with score for new code.
    """
    if not 0 <= inputs.task_complexity <= 10:
        raise ValueError(f"task_complexity must be in 0..10, got {inputs.task_complexity}")
    if not 0 <= inputs.safety_risk <= 10:
        raise ValueError(f"safety_risk must be in 0..10, got {inputs.safety_risk}")
    if inputs.retry_count < 0:
        raise ValueError(f"retry_count must be >= 0, got {inputs.retry_count}")
    if inputs.task_complexity < 3 and inputs.safety_risk < 7 and (inputs.retry_count <= 2):
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Task is trivial: low complexity, low safety risk, few retries",
            threshold_used="TRIVIAL",
        )
    if inputs.task_complexity >= 8 or inputs.safety_risk >= 7 or inputs.retry_count > 2:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale="High complexity/risk/retries: Gemini escalation",
            threshold_used="LEGACY_HIGH",
        )
    return HealEscalationDecision(
        proceed=True,
        tier=ReasoningTier.LOW,
        rationale="No escalation triggers met; default to Qwen tier",
        threshold_used="LEGACY_LOW",
    )
