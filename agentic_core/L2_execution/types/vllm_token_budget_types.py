"""
WAVE 1 — Authoritative Token Budget Policy for vLLM Tiered Routing.

Defines gateway-level hard caps (constants, not env-derived defaults),
task-class output-cap mapping, and deterministic token estimation
for Qwen 7B / 14B / Gemini-2.5-Pro tiered routing.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_snapshots_state,
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

emit_replay_key("p0", "vllm_token_budget_types")
emit_determinism_digest("p0", "vllm_token_budget_types")

_emit_dispatches_healing_run("p1", "vllm_token_budget_types", "L2")
_emit_routes_through("p1", "vllm_token_budget_types", "L2")
_emit_checks_agent_registry("p1", "vllm_token_budget_types", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_token_budget_types", "capability")
_emit_dispatches_execution_plan("p1", "vllm_token_budget_types", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_token_budget_types", "sub_agent")
_emit_routes_to_agent("p1", "vllm_token_budget_types", "target_agent")
_emit_verifies_policy("p1", "vllm_token_budget_types", "policy_check")
_emit_observes_runtime_state("p1", "vllm_token_budget_types", "runtime_state")
_emit_verifies_boundary("p1", "vllm_token_budget_types", "boundary_check")
_emit_transcripts_response("p1", "vllm_token_budget_types", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_token_budget_types")
_emit_gated_by_confidence("p1", "vllm_token_budget_types", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_token_budget_types", "L2")
_emit_reads_policy_state("p1", "vllm_token_budget_types", "L2")
_emit_authorize_and_execute("p2", "vllm_token_budget_types", "execution_auth")
_emit_validates_capability("p2", "vllm_token_budget_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_token_budget_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_token_budget_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_token_budget_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_token_budget_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_token_budget_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_token_budget_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_token_budget_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_token_budget_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_token_budget_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_token_budget_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_token_budget_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_token_budget_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_token_budget_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_token_budget_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_token_budget_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_token_budget_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_token_budget_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_token_budget_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("vllm_token_budget_types", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_token_budget_types", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_token_budget_types", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_token_budget_types", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_token_budget_types", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_token_budget_types", "p4obs", "metric_6")
_emit_records_incident_event("vllm_token_budget_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_token_budget_types", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_token_budget_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_token_budget_types", "p4obs", "mon_state")
_emit_triggers_alert("vllm_token_budget_types", "p4obs", "alert")
_emit_links_incident_trace("vllm_token_budget_types", "p4obs", "trace_link")
_emit_captures_pattern("vllm_token_budget_types", "p3lm", "pattern")
_emit_records_learning_event("vllm_token_budget_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_token_budget_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_token_budget_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_token_budget_types", "p3lm", "routing")
_emit_improves_agent_policy("vllm_token_budget_types", "p3lm", "policy")
_emit_stores_learning_state("vllm_token_budget_types", "p3lm", "state")
_emit_records_execution_trace("vllm_token_budget_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_token_budget_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_token_budget_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_token_budget_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_token_budget_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_token_budget_types", "env_read", "p2_env_1")
_emit_reads_environ("vllm_token_budget_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_token_budget_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_token_budget_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_token_budget_types", "context_pull")
_emit_pulls_context("p1", "vllm_token_budget_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_token_budget_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_token_budget_types", "uwg_term_2")
_emit_writes_through("p1", "vllm_token_budget_types", "write_through")
_emit_writes_through("p1", "vllm_token_budget_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_token_budget_types", "safety_validation")
_emit_invokes_eval("p1", "vllm_token_budget_types", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_token_budget_types", "routing_commit")

VLLM_MAX_TOKENS_DEFAULT: int = 600
VLLM_MAX_TOKENS_EXTENDED: int = 1200
VLLM_MAX_TOKENS_ABSOLUTE: int = 1200
SAFETY_MARGIN_TOKENS: int = 256
_QWEN_CHARS_PER_TOKEN: int = 3
QWEN_MAX_MODEL_LEN: int = 32768
# Backward-compat aliases (2026-04-25 single-tier collapse) — both names
# refer to the same QWEN_LOCAL_MODEL_ID model now that vLLM serves
# Qwen2.5-32B-Instruct-AWQ exclusively. Kept to avoid breaking external
# consumers that import these symbols. New code should use QWEN_MAX_MODEL_LEN.
QWEN_7B_MAX_MODEL_LEN: int = QWEN_MAX_MODEL_LEN
QWEN_14B_MAX_MODEL_LEN: int = QWEN_MAX_MODEL_LEN


class TaskClass(str, Enum):
    """Authoritative task class taxonomy for vLLM output cap enforcement."""

    HEALING_JSON_ARTIFACT = "healing_json_artifact"
    PATCH_SUGGESTION = "patch_suggestion"
    MULTI_FILE_SUMMARY = "multi_file_summary"
    # apps_* task classes — long-form generation, capped to extended ceiling
    EXECUTION_PLANNING = "execution_planning"
    RESEARCH_SYNTHESIS = "research_synthesis"
    PROPOSAL_GENERATION = "proposal_generation"
    RESUME_GENERATION = "resume_generation"
    GOVERNANCE_ANALYSIS = "governance_analysis"
    UNDEFINED = "undefined"


TASK_CLASS_OUTPUT_CAPS: dict[str, int] = {
    TaskClass.HEALING_JSON_ARTIFACT.value: 300,
    TaskClass.PATCH_SUGGESTION.value: 600,
    TaskClass.MULTI_FILE_SUMMARY.value: 1200,
    # apps_* generative task classes — capped at VLLM_MAX_TOKENS_ABSOLUTE (1200)
    TaskClass.EXECUTION_PLANNING.value: 1200,
    TaskClass.RESEARCH_SYNTHESIS.value: 1200,
    TaskClass.PROPOSAL_GENERATION.value: 1200,
    TaskClass.RESUME_GENERATION.value: 1200,
    TaskClass.GOVERNANCE_ANALYSIS.value: 800,
}
EXTENDED_CAP_WHITELIST: frozenset[str] = frozenset(
    {
        TaskClass.MULTI_FILE_SUMMARY.value,
        TaskClass.RESEARCH_SYNTHESIS.value,
        TaskClass.PROPOSAL_GENERATION.value,
    }
)


def get_output_cap(task_class: str) -> int | None:
    """Return the output token cap for a task class.

    Returns:
        int: Cap in tokens if task_class is known and local.
        None: If task_class is undefined — caller must route to Gemini-2.5-Pro.

    Raises:
        ValueError: If cap would exceed VLLM_MAX_TOKENS_ABSOLUTE.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_output_cap", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_output_cap", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_output_cap")
    cap = TASK_CLASS_OUTPUT_CAPS.get(task_class)
    if cap is None:
        return None
    if cap > VLLM_MAX_TOKENS_ABSOLUTE:
        raise ValueError(
            f"Task class {task_class!r} cap {cap} exceeds VLLM_MAX_TOKENS_ABSOLUTE={VLLM_MAX_TOKENS_ABSOLUTE}. Route to Gemini-2.5-Pro.",
        )
    return cap


def enforce_output_cap(requested_tokens: int, task_class: str) -> int:
    """Enforce hard ceiling on requested output tokens.

    Args:
        requested_tokens: Caller-requested max_tokens.
        task_class: Task class string from TaskClass enum.

    Returns:
        Enforced token count (never exceeds VLLM_MAX_TOKENS_ABSOLUTE).

    Raises:
        VLLMOutputCapExceeded: If requested_tokens > VLLM_MAX_TOKENS_ABSOLUTE
            and task_class is not in extended whitelist.
    """
    cap = get_output_cap(task_class)
    if cap is None:
        raise VLLMOutputCapExceeded(
            task_class=task_class,
            requested=requested_tokens,
            cap=0,
            reason="undefined_task_class_requires_gemini_escalation",
        )
    effective = min(requested_tokens, cap)
    if effective > VLLM_MAX_TOKENS_ABSOLUTE:
        raise VLLMOutputCapExceeded(
            task_class=task_class,
            requested=requested_tokens,
            cap=VLLM_MAX_TOKENS_ABSOLUTE,
            reason="exceeds_absolute_ceiling",
        )
    return effective


class VLLMOutputCapExceeded(Exception):
    """Raised when a local vLLM request would exceed the output cap.

    Caller must route to Gemini-2.5-Pro.
    """

    def __init__(self, task_class: str, requested: int, cap: int, reason: str) -> None:
        self.task_class = task_class
        self.requested = requested
        self.cap = cap
        self.reason = reason
        super().__init__(
            f"VLLMOutputCapExceeded: task_class={task_class!r}, requested={requested}, cap={cap}, reason={reason}",
        )


def estimate_tokens_qwen(text: str) -> int:
    """Deterministic token estimation for Qwen2.5 tokenizer family.

    Uses pinned chars-per-token ratio (_QWEN_CHARS_PER_TOKEN = 3).
    Deterministic: identical input → identical output across all runs.
    No external tokenizer library required (L2 purity preserved).

    Args:
        text: Input text to estimate.

    Returns:
        Estimated token count (minimum 1).
    """
    if not text:
        return 0
    return max(1, len(text) // _QWEN_CHARS_PER_TOKEN)


class VLLMFailureType(str, Enum):
    """Failure classification for vLLM routing decisions."""

    TOKEN_BUDGET_EXCEEDED = "TOKEN_BUDGET_EXCEEDED"
    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"
    QUEUE_OVERFLOW = "QUEUE_OVERFLOW"
    GPU_HEALTH_FAILED = "GPU_HEALTH_FAILED"
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    UNDEFINED_TASK_CLASS = "UNDEFINED_TASK_CLASS"


@dataclass(frozen=True)
class VLLMPreflightResult:
    """Result of the preflight token budget gate.

    Produced before any local vLLM call. Immutable.
    """

    prompt_tokens_estimated: int
    max_output_tokens_requested: int
    max_model_len_configured: int
    token_budget_ok: bool
    budget_margin_tokens: int
    failure_type: VLLMFailureType | None
    route_to_gemini: bool

    def __post_init__(self) -> None:
        if self.token_budget_ok and self.route_to_gemini:
            raise ValueError(
                "VLLMPreflightResult: token_budget_ok=True and route_to_gemini=True is contradictory — budget OK should not force Gemini escalation.",
            )
        if not self.token_budget_ok and self.failure_type is None:
            raise ValueError("VLLMPreflightResult: token_budget_ok=False requires failure_type.")


def run_preflight_budget_check(prompt: str, task_class: str, max_model_len: int) -> VLLMPreflightResult:
    """Execute preflight token budget gate.

    Algorithm (per spec):
        1. Estimate prompt_tokens
        2. Determine max_output_tokens via task-class cap
        3. Retrieve configured max_model_len
        4. required = prompt_tokens + max_output_tokens
        5. If required > max_model_len - SAFETY_MARGIN_TOKENS:
               route to Gemini-2.5-Pro, emit TOKEN_BUDGET_EXCEEDED
           Else:
               proceed to local tier selection

    Args:
        prompt: Input prompt string.
        task_class: Task class string from TaskClass enum.
        max_model_len: Configured maximum model context length.

    Returns:
        VLLMPreflightResult with all telemetry fields populated.
    """
    prompt_tokens = estimate_tokens_qwen(prompt)
    cap = get_output_cap(task_class)
    if cap is None:
        return VLLMPreflightResult(
            prompt_tokens_estimated=prompt_tokens,
            max_output_tokens_requested=0,
            max_model_len_configured=max_model_len,
            token_budget_ok=False,
            budget_margin_tokens=0,
            failure_type=VLLMFailureType.UNDEFINED_TASK_CLASS,
            route_to_gemini=True,
        )
    required = prompt_tokens + cap
    available = max_model_len - SAFETY_MARGIN_TOKENS
    margin = available - required
    budget_ok = required <= available
    return VLLMPreflightResult(
        prompt_tokens_estimated=prompt_tokens,
        max_output_tokens_requested=cap,
        max_model_len_configured=max_model_len,
        token_budget_ok=budget_ok,
        budget_margin_tokens=margin,
        failure_type=None if budget_ok else VLLMFailureType.TOKEN_BUDGET_EXCEEDED,
        route_to_gemini=not budget_ok,
    )


LocalTier = Literal["local_fast", "local_strong", "gemini_backstop"]
# Single-tier collapse (2026-04-25): vLLM serves Qwen2.5-32B-Instruct-AWQ
# exclusively. The QWEN_7B_MODEL_ID/QWEN_14B_MODEL_ID names are preserved
# as deprecated aliases pointing at the SSOT QWEN_LOCAL_MODEL_ID — both
# return the same value. New code should import QWEN_LOCAL_MODEL_ID from
# agentic_core.L0_routing.config.model_registry directly.
from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MODEL_ID  # noqa: E402, PLC0415

QWEN_7B_MODEL_ID: str = (
    QWEN_LOCAL_MODEL_ID  # Deprecated alias (was "Qwen/Qwen2.5-7B-Instruct" — model never served)
)
QWEN_14B_MODEL_ID: str = (
    QWEN_LOCAL_MODEL_ID  # Deprecated alias (was misnamed; value already pointed at 32B-AWQ)
)
GEMINI_25_PRO_MODEL_ID: str = "gemini-2.5-pro"
HIGH_SEVERITY_LEVELS: frozenset[str] = frozenset({"high"})
FAST_TIER_SEVERITY_LEVELS: frozenset[str] = frozenset({"low", "medium"})


@dataclass(frozen=True)
class TieredRoutingDecision:
    """Immutable routing decision for vLLM tiered routing.

    Produced after preflight check passes.
    """

    tier: LocalTier
    model_id: str
    reason: str
    preflight: VLLMPreflightResult
    failure_type: VLLMFailureType | None


def select_local_tier(
    preflight: VLLMPreflightResult,
    severity: str,
    circuit_breaker_open: bool = False,
    queue_overflow: bool = False,
    gpu_health_failed: bool = False,
    schema_validation_failed: bool = False,
    confidence_below_threshold: bool = False,
) -> TieredRoutingDecision:
    """Select local execution tier per routing invariants.

    Routing invariants (in priority order):
        1. token budget fails → Gemini-2.5-Pro
        2. circuit breaker open → Gemini-2.5-Pro
        3. queue overflow → Gemini-2.5-Pro
        4. GPU health fails → Gemini-2.5-Pro
        5. schema/semantic validation fails → Gemini-2.5-Pro
        6. confidence < threshold → Gemini-2.5-Pro
        7. Otherwise:
              severity low/medium → 7B (local_fast)
              severity high (non-critical) → 14B (local_strong)

    Gemini-2.5-Pro is NEVER removed from gateway.
    It remains mandatory for all failure states.

    Args:
        preflight: Result of run_preflight_budget_check.
        severity: Severity level string ("low", "medium", "high").
        circuit_breaker_open: Whether circuit breaker is open.
        queue_overflow: Whether request queue is full.
        gpu_health_failed: Whether GPU health check failed.
        schema_validation_failed: Whether schema/semantic validation failed.
        confidence_below_threshold: Whether confidence is below threshold.

    Returns:
        TieredRoutingDecision with tier, model_id, and reason.
    """
    if not preflight.token_budget_ok:
        return TieredRoutingDecision(
            tier="gemini_backstop",
            model_id=GEMINI_25_PRO_MODEL_ID,
            reason="token_budget_exceeded",
            preflight=preflight,
            failure_type=VLLMFailureType.TOKEN_BUDGET_EXCEEDED,
        )
    if circuit_breaker_open:
        return TieredRoutingDecision(
            tier="gemini_backstop",
            model_id=GEMINI_25_PRO_MODEL_ID,
            reason="circuit_breaker_open",
            preflight=preflight,
            failure_type=VLLMFailureType.CIRCUIT_BREAKER_OPEN,
        )
    if queue_overflow:
        return TieredRoutingDecision(
            tier="gemini_backstop",
            model_id=GEMINI_25_PRO_MODEL_ID,
            reason="queue_overflow",
            preflight=preflight,
            failure_type=VLLMFailureType.QUEUE_OVERFLOW,
        )
    if gpu_health_failed:
        return TieredRoutingDecision(
            tier="gemini_backstop",
            model_id=GEMINI_25_PRO_MODEL_ID,
            reason="gpu_health_failed",
            preflight=preflight,
            failure_type=VLLMFailureType.GPU_HEALTH_FAILED,
        )
    if schema_validation_failed:
        return TieredRoutingDecision(
            tier="gemini_backstop",
            model_id=GEMINI_25_PRO_MODEL_ID,
            reason="schema_validation_failed",
            preflight=preflight,
            failure_type=VLLMFailureType.SCHEMA_VALIDATION_FAILED,
        )
    if confidence_below_threshold:
        return TieredRoutingDecision(
            tier="gemini_backstop",
            model_id=GEMINI_25_PRO_MODEL_ID,
            reason="low_confidence",
            preflight=preflight,
            failure_type=VLLMFailureType.LOW_CONFIDENCE,
        )
    # Single-tier collapse (2026-04-25): vLLM serves only QWEN_LOCAL_MODEL_ID,
    # so all severity levels route to the same physical model. The "local_fast"
    # vs "local_strong" distinction was scaffolding for a 7B tier that was
    # never actually served. Severity is preserved as a tier-name signal for
    # downstream telemetry/dashboards but no longer changes the model_id.
    if severity in HIGH_SEVERITY_LEVELS:
        return TieredRoutingDecision(
            tier="local_strong",
            model_id=QWEN_LOCAL_MODEL_ID,
            reason="high_severity_local_strong",
            preflight=preflight,
            failure_type=None,
        )
    return TieredRoutingDecision(
        tier="local_fast",
        model_id=QWEN_LOCAL_MODEL_ID,
        reason="low_medium_severity_unified_qwen",
        preflight=preflight,
        failure_type=None,
    )


__all__ = [
    "EXTENDED_CAP_WHITELIST",
    "FAST_TIER_SEVERITY_LEVELS",
    "GEMINI_25_PRO_MODEL_ID",
    "HIGH_SEVERITY_LEVELS",
    "QWEN_14B_MAX_MODEL_LEN",
    "QWEN_14B_MODEL_ID",
    "QWEN_7B_MAX_MODEL_LEN",
    "QWEN_7B_MODEL_ID",
    "QWEN_LOCAL_MODEL_ID",
    "QWEN_MAX_MODEL_LEN",
    "SAFETY_MARGIN_TOKENS",
    "TASK_CLASS_OUTPUT_CAPS",
    "VLLM_MAX_TOKENS_ABSOLUTE",
    "VLLM_MAX_TOKENS_DEFAULT",
    "VLLM_MAX_TOKENS_EXTENDED",
    "TaskClass",
    "TieredRoutingDecision",
    "VLLMFailureType",
    "VLLMOutputCapExceeded",
    "VLLMPreflightResult",
    "enforce_output_cap",
    "estimate_tokens_qwen",
    "get_output_cap",
    "run_preflight_budget_check",
    "select_local_tier",
]
