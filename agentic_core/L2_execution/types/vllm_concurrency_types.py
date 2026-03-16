"""
WAVE 2 — Concurrency + KV Cache Stress Validation types.

Defines deterministic stress harness, concurrency request simulation,
and telemetry assertions for KV-cache headroom validation.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    VLLMServingProfile,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    SAFETY_MARGIN_TOKENS,
    VLLM_MAX_TOKENS_ABSOLUTE,
    VLLMPreflightResult,
    estimate_tokens_qwen,
    run_preflight_budget_check,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "vllm_concurrency_types")
emit_determinism_digest("p0", "vllm_concurrency_types")

_emit_dispatches_healing_run("p1", "vllm_concurrency_types", "L2")
_emit_routes_through("p1", "vllm_concurrency_types", "L2")
_emit_escalates_to_human("p1", "vllm_concurrency_types", "L2")
_emit_reads_policy_state("p1", "vllm_concurrency_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "vllm_concurrency_types")
_emit_applies_guardrail("p0", "vllm_concurrency_types", "p0_governance")
_emit_snapshots_state("p0", "vllm_concurrency_types", "state_snapshot")
_emit_authorize_and_execute("p2", "vllm_concurrency_types", "execution_auth")
_emit_validates_capability("p2", "vllm_concurrency_types", "capability_check")
_emit_routes_to_capability("p2", "vllm_concurrency_types", "capability_route")
_emit_writes_via_uwg("p2", "vllm_concurrency_types", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_concurrency_types", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_concurrency_types", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_concurrency_types", "exec_output")
_emit_dispatches_agent("p3", "vllm_concurrency_types", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_concurrency_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_concurrency_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_concurrency_types", "healing_outcome")
_emit_escalates_failure("p3", "vllm_concurrency_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_concurrency_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_concurrency_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_concurrency_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_concurrency_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_concurrency_types", "eval_metric")
_emit_stores_embedding("p4", "vllm_concurrency_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_concurrency_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_concurrency_types", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# WAVE 2.1 — Stress request dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VLLMStressRequest:
    """A single deterministic stress request near the budget ceiling.

    Immutable. Used to simulate worst-case prompt + max_output_tokens.
    """

    request_id: int
    prompt: str
    task_class: str
    max_output_tokens_requested: int


@dataclass(frozen=True)
class VLLMStressResult:
    """Result of a single stress request evaluation.

    Immutable. Records preflight outcome and truncation status.
    """

    request_id: int
    preflight: VLLMPreflightResult
    truncated: bool
    unexpected_fallback: bool
    total_tokens_required: int


# ---------------------------------------------------------------------------
# WAVE 2.2 — Deterministic stress harness
# ---------------------------------------------------------------------------


def build_worst_case_prompt(profile: VLLMServingProfile, task_class_cap: int) -> str:
    """Build a worst-case prompt that fills the budget ceiling.

    Constructs a prompt whose token estimate equals:
        max_model_len - SAFETY_MARGIN_TOKENS - task_class_cap - 1

    This is the largest prompt that should still pass preflight.

    Args:
        profile: Serving profile defining max_model_len.
        task_class_cap: Output cap for the task class.

    Returns:
        Deterministic prompt string at budget ceiling.
    """
    available_prompt_tokens = profile.max_model_len - SAFETY_MARGIN_TOKENS - task_class_cap - 1
    if available_prompt_tokens <= 0:
        return "x"
    # 3 chars per token (pinned Qwen2.5 ratio)
    return "a" * (available_prompt_tokens * 3)


def run_stress_batch(
    profile: VLLMServingProfile,
    requests: list[VLLMStressRequest],
) -> list[VLLMStressResult]:
    """Execute a batch of stress requests against a serving profile.

    Evaluates each request via preflight check. Records:
    - Whether truncation would occur (total_tokens > max_model_len)
    - Whether unexpected fallback occurred (budget_ok=True but route_to_gemini=True)

    Args:
        profile: Serving profile to validate against.
        requests: List of stress requests to evaluate.

    Returns:
        List of VLLMStressResult, one per request.
    """
    results = []
    for req in requests:
        preflight = run_preflight_budget_check(
            prompt=req.prompt,
            task_class=req.task_class,
            max_model_len=profile.max_model_len,
        )
        prompt_tokens = estimate_tokens_qwen(req.prompt)
        total_required = prompt_tokens + req.max_output_tokens_requested
        truncated = total_required > profile.max_model_len
        unexpected_fallback = preflight.token_budget_ok and preflight.route_to_gemini
        results.append(
            VLLMStressResult(
                request_id=req.request_id,
                preflight=preflight,
                truncated=truncated,
                unexpected_fallback=unexpected_fallback,
                total_tokens_required=total_required,
            )
        )
    return results


# ---------------------------------------------------------------------------
# WAVE 2.3 — Telemetry assertion helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VLLMConcurrencyValidationResult:
    """Aggregated result of a concurrency stress validation run.

    Immutable. Used for evidence reporting.
    """

    profile_name: str
    num_requests: int
    max_num_seqs: int
    any_truncation: bool
    any_unexpected_fallback: bool
    any_absolute_exceeded: bool
    all_within_budget: bool
    request_results: tuple[VLLMStressResult, ...]


def validate_concurrency_headroom(
    profile: VLLMServingProfile,
    requests: list[VLLMStressRequest],
) -> VLLMConcurrencyValidationResult:
    """Validate KV-cache headroom under concurrent request load.

    Asserts:
    1. No request exceeds VLLM_MAX_TOKENS_ABSOLUTE output tokens.
    2. No unexpected fallback when token_budget_ok=True.
    3. No truncation within max_model_len.

    Args:
        profile: Serving profile to validate.
        requests: Concurrent requests to simulate (len <= max_num_seqs).

    Returns:
        VLLMConcurrencyValidationResult with full telemetry.
    """
    results = run_stress_batch(profile, requests)

    any_truncation = any(r.truncated for r in results)
    any_unexpected_fallback = any(r.unexpected_fallback for r in results)
    any_absolute_exceeded = any(
        r.preflight.max_output_tokens_requested > VLLM_MAX_TOKENS_ABSOLUTE for r in results
    )
    all_within_budget = all(r.preflight.token_budget_ok for r in results)

    return VLLMConcurrencyValidationResult(
        profile_name=profile.profile_name,
        num_requests=len(requests),
        max_num_seqs=profile.max_num_seqs,
        any_truncation=any_truncation,
        any_unexpected_fallback=any_unexpected_fallback,
        any_absolute_exceeded=any_absolute_exceeded,
        all_within_budget=all_within_budget,
        request_results=tuple(results),
    )


__all__ = [
    "VLLMConcurrencyValidationResult",
    "VLLMStressRequest",
    "VLLMStressResult",
    "build_worst_case_prompt",
    "run_stress_batch",
    "validate_concurrency_headroom",
]
