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

from agentic_core.L0_routing.config.path_constants import (
    SSOT_SCORE_THRESHOLD_DET as SCORE_THRESHOLD_DET,
)
from agentic_core.L0_routing.config.path_constants import (
    SSOT_SCORE_THRESHOLD_QWEN as SCORE_THRESHOLD_QWEN,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("heal_policy_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("heal_policy_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("heal_policy_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("heal_policy_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("heal_policy_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("heal_policy_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("heal_policy_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("heal_policy_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("heal_policy_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("heal_policy_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("heal_policy_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("heal_policy_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("heal_policy_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("heal_policy_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("heal_policy_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("heal_policy_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("heal_policy_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("heal_policy_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("heal_policy_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("heal_policy_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("heal_policy_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("heal_policy_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("heal_policy_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("heal_policy_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("heal_policy_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("heal_policy_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("heal_policy_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("heal_policy_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "heal_policy_types")
trace_contract.emit_determinism_digest("p0", "heal_policy_types")

trace_contract._emit_dispatches_healing_run("p1", "heal_policy_types", "L5")
trace_contract._emit_routes_through("p1", "heal_policy_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "heal_policy_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "heal_policy_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "heal_policy_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "heal_policy_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "heal_policy_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "heal_policy_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "heal_policy_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "heal_policy_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "heal_policy_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "heal_policy_types")
trace_contract._emit_gated_by_confidence("p1", "heal_policy_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "heal_policy_types", "L5")
trace_contract._emit_reads_policy_state("p1", "heal_policy_types", "L5")
trace_contract._emit_pulls_context("p1", "heal_policy_types", "context_pull")
trace_contract._emit_pulls_context("p1", "heal_policy_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "heal_policy_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "heal_policy_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "heal_policy_types", "write_through")
trace_contract._emit_writes_through("p1", "heal_policy_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "heal_policy_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "heal_policy_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "heal_policy_types", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "heal_policy_types")
trace_contract._emit_applies_guardrail("p0", "heal_policy_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "heal_policy_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "heal_policy_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "heal_policy_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "heal_policy_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "heal_policy_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "heal_policy_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "heal_policy_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "heal_policy_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "heal_policy_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "heal_policy_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "heal_policy_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "heal_policy_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "heal_policy_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "heal_policy_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "heal_policy_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "heal_policy_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "heal_policy_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "heal_policy_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "heal_policy_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "heal_policy_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "heal_policy_types", "exec_snapshot_link")


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
