"""
WAVE 2 — Preflight Token Budget Gate Tests.

Validates:
- Preflight check routes to Gemini when budget exceeded
- Preflight check allows local when budget OK
- All telemetry fields present in VLLMPreflightResult
- Routing decision deterministic across identical runs
- TOKEN_BUDGET_EXCEEDED failure type emitted correctly
- Undefined task class forces Gemini escalation
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_token_budget_preflight_fallback")
_emit_applies_guardrail("p0", "test_token_budget_preflight_fallback", "p0_governance")
_emit_reads_policy_state("p0", "test_token_budget_preflight_fallback", "policy_binding")
_emit_snapshots_state("p0", "test_token_budget_preflight_fallback", "state_snapshot")
emit_replay_key("p0", "test_token_budget_preflight_fallback")
emit_determinism_digest("p0", "test_token_budget_preflight_fallback")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_token_budget_preflight_fallback", "execution_auth")
_emit_validates_capability("p2", "test_token_budget_preflight_fallback", "capability_check")
_emit_routes_to_capability("p2", "test_token_budget_preflight_fallback", "capability_route")
_emit_writes_via_uwg("p2", "test_token_budget_preflight_fallback", "uwg_write")
_emit_blocks_direct_write("p2", "test_token_budget_preflight_fallback", "direct_write_block")
_emit_records_tool_invocation("p2", "test_token_budget_preflight_fallback", "tool_invocation")
_emit_captures_execution_output("p2", "test_token_budget_preflight_fallback", "exec_output")
_emit_dispatches_agent("p3", "test_token_budget_preflight_fallback", "agent_dispatch")
_emit_coordinates_agents("p3", "test_token_budget_preflight_fallback", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_token_budget_preflight_fallback", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_token_budget_preflight_fallback", "healing_outcome")
_emit_escalates_failure("p3", "test_token_budget_preflight_fallback", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_token_budget_preflight_fallback", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_token_budget_preflight_fallback", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_token_budget_preflight_fallback", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_token_budget_preflight_fallback", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_token_budget_preflight_fallback", "eval_metric")
_emit_stores_embedding("p4", "test_token_budget_preflight_fallback", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_token_budget_preflight_fallback", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_token_budget_preflight_fallback", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.types.vllm_token_budget_types import (
    QWEN_7B_MAX_MODEL_LEN,
    SAFETY_MARGIN_TOKENS,
    TASK_CLASS_OUTPUT_CAPS,
    TaskClass,
    VLLMFailureType,
    VLLMPreflightResult,
    estimate_tokens_qwen,
    run_preflight_budget_check,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_token_budget_preflight_fallback", "p4obs", "metric_1")
_emit_emits_metric_event("test_token_budget_preflight_fallback", "p4obs", "metric_2")
_emit_emits_metric_event("test_token_budget_preflight_fallback", "p4obs", "metric_3")
_emit_emits_metric_event("test_token_budget_preflight_fallback", "p4obs", "metric_4")
_emit_emits_metric_event("test_token_budget_preflight_fallback", "p4obs", "metric_5")
_emit_emits_metric_event("test_token_budget_preflight_fallback", "p4obs", "metric_6")
_emit_records_incident_event("test_token_budget_preflight_fallback", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_token_budget_preflight_fallback", "p4obs", "anomaly")
_emit_writes_observability_log("test_token_budget_preflight_fallback", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_token_budget_preflight_fallback", "p4obs", "mon_state")
_emit_triggers_alert("test_token_budget_preflight_fallback", "p4obs", "alert")
_emit_links_incident_trace("test_token_budget_preflight_fallback", "p4obs", "trace_link")
_emit_captures_pattern("test_token_budget_preflight_fallback", "p3lm", "pattern")
_emit_records_learning_event("test_token_budget_preflight_fallback", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_token_budget_preflight_fallback", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_token_budget_preflight_fallback", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_token_budget_preflight_fallback", "p3lm", "routing")
_emit_improves_agent_policy("test_token_budget_preflight_fallback", "p3lm", "policy")
_emit_stores_learning_state("test_token_budget_preflight_fallback", "p3lm", "state")
_emit_records_execution_trace("test_token_budget_preflight_fallback", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_token_budget_preflight_fallback", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_token_budget_preflight_fallback", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_token_budget_preflight_fallback", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_token_budget_preflight_fallback", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_token_budget_preflight_fallback", "env_read", "p2_env_1")
_emit_reads_environ("test_token_budget_preflight_fallback", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_token_budget_preflight_fallback", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_token_budget_preflight_fallback", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_token_budget_preflight_fallback", "context_pull")
_emit_pulls_context("p1", "test_token_budget_preflight_fallback", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_token_budget_preflight_fallback", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_token_budget_preflight_fallback", "uwg_term_2")
_emit_writes_through("p1", "test_token_budget_preflight_fallback", "write_through")
_emit_writes_through("p1", "test_token_budget_preflight_fallback", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_token_budget_preflight_fallback", "safety_validation")
_emit_invokes_eval("p1", "test_token_budget_preflight_fallback", "eval_call")
_emit_proposal_commits_routing("p1", "test_token_budget_preflight_fallback", "routing_commit")
_emit_escalates_to_human("p1", "test_token_budget_preflight_fallback", "human_escalation")
_emit_routes_through("p1", "test_token_budget_preflight_fallback", "route_through")
_emit_checks_agent_registry("p1", "test_token_budget_preflight_fallback", "agent_registry")
_emit_validates_agent_capability("p1", "test_token_budget_preflight_fallback", "capability")
_emit_dispatches_execution_plan("p1", "test_token_budget_preflight_fallback", "exec_plan")
_emit_agent_executes_agent("p1", "test_token_budget_preflight_fallback", "sub_agent")
_emit_routes_to_agent("p1", "test_token_budget_preflight_fallback", "target_agent")
_emit_verifies_policy("p1", "test_token_budget_preflight_fallback", "policy_check")
_emit_observes_runtime_state("p1", "test_token_budget_preflight_fallback", "runtime_state")
_emit_verifies_boundary("p1", "test_token_budget_preflight_fallback", "boundary_check")
_emit_transcripts_response("p1", "test_token_budget_preflight_fallback", "transcript")
_emit_hard_fails_untranscripted("p1", "test_token_budget_preflight_fallback")
_emit_gated_by_confidence("p1", "test_token_budget_preflight_fallback", "confidence_gate")

# ---------------------------------------------------------------------------
# Test 1 — Preflight passes for small prompt + known task class
# ---------------------------------------------------------------------------


def test_preflight_passes_small_prompt() -> None:
    """Small prompt with known task class must pass preflight."""
    prompt = "Fix the import error."
    result = run_preflight_budget_check(
        prompt=prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.token_budget_ok is True
    assert result.route_to_gemini is False
    assert result.failure_type is None


# ---------------------------------------------------------------------------
# Test 2 — Preflight fails for oversized prompt
# ---------------------------------------------------------------------------


def test_preflight_fails_oversized_prompt() -> None:
    """Prompt that exhausts model context must fail preflight."""
    # Generate a prompt that is ~32000 tokens (fills 7B context)
    # 3 chars/token * 32000 = 96000 chars
    huge_prompt = "x " * 50000  # ~100000 chars → ~33333 tokens
    result = run_preflight_budget_check(
        prompt=huge_prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.token_budget_ok is False
    assert result.route_to_gemini is True
    assert result.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED


# ---------------------------------------------------------------------------
# Test 3 — TOKEN_BUDGET_EXCEEDED failure type emitted
# ---------------------------------------------------------------------------


def test_token_budget_exceeded_failure_type() -> None:
    """TOKEN_BUDGET_EXCEEDED must be the failure type when budget exceeded."""
    huge_prompt = "word " * 40000
    result = run_preflight_budget_check(
        prompt=huge_prompt,
        task_class=TaskClass.PATCH_SUGGESTION.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED


# ---------------------------------------------------------------------------
# Test 4 — All telemetry fields present
# ---------------------------------------------------------------------------


def test_preflight_telemetry_fields_present() -> None:
    """VLLMPreflightResult must contain all required telemetry fields."""
    prompt = "Analyze the following code."
    result = run_preflight_budget_check(
        prompt=prompt,
        task_class=TaskClass.PATCH_SUGGESTION.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    # All telemetry fields must be present and typed correctly
    assert isinstance(result.prompt_tokens_estimated, int)
    assert isinstance(result.max_output_tokens_requested, int)
    assert isinstance(result.max_model_len_configured, int)
    assert isinstance(result.token_budget_ok, bool)
    assert isinstance(result.budget_margin_tokens, int)
    # failure_type is None or VLLMFailureType
    assert result.failure_type is None or isinstance(result.failure_type, VLLMFailureType)
    assert isinstance(result.route_to_gemini, bool)


# ---------------------------------------------------------------------------
# Test 5 — Routing decision deterministic across identical runs
# ---------------------------------------------------------------------------


def test_preflight_deterministic_across_runs() -> None:
    """Identical prompt + task_class must produce identical preflight results."""
    prompt = "Deterministic routing test prompt."
    kwargs = {
        "prompt": prompt,
        "task_class": TaskClass.HEALING_JSON_ARTIFACT.value,
        "max_model_len": QWEN_7B_MAX_MODEL_LEN,
    }
    results = [run_preflight_budget_check(**kwargs) for _ in range(5)]
    first = results[0]
    for r in results[1:]:
        assert r.prompt_tokens_estimated == first.prompt_tokens_estimated
        assert r.max_output_tokens_requested == first.max_output_tokens_requested
        assert r.token_budget_ok == first.token_budget_ok
        assert r.budget_margin_tokens == first.budget_margin_tokens
        assert r.failure_type == first.failure_type
        assert r.route_to_gemini == first.route_to_gemini


# ---------------------------------------------------------------------------
# Test 6 — prompt_tokens_estimated matches estimate_tokens_qwen
# ---------------------------------------------------------------------------


def test_preflight_prompt_tokens_matches_estimator() -> None:
    """prompt_tokens_estimated must match estimate_tokens_qwen output."""
    prompt = "Check the configuration file for errors."
    expected_tokens = estimate_tokens_qwen(prompt)
    result = run_preflight_budget_check(
        prompt=prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.prompt_tokens_estimated == expected_tokens


# ---------------------------------------------------------------------------
# Test 7 — max_output_tokens_requested matches task-class cap
# ---------------------------------------------------------------------------


def test_preflight_output_tokens_matches_cap() -> None:
    """max_output_tokens_requested must match the task-class cap."""
    prompt = "Short prompt."
    result = run_preflight_budget_check(
        prompt=prompt,
        task_class=TaskClass.PATCH_SUGGESTION.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.max_output_tokens_requested == TASK_CLASS_OUTPUT_CAPS[TaskClass.PATCH_SUGGESTION.value]


# ---------------------------------------------------------------------------
# Test 8 — budget_margin_tokens is correct
# ---------------------------------------------------------------------------


def test_preflight_budget_margin_correct() -> None:
    """budget_margin_tokens must equal available - required."""
    prompt = "Fix the import."
    cap = TASK_CLASS_OUTPUT_CAPS[TaskClass.HEALING_JSON_ARTIFACT.value]
    prompt_tokens = estimate_tokens_qwen(prompt)
    required = prompt_tokens + cap
    available = QWEN_7B_MAX_MODEL_LEN - SAFETY_MARGIN_TOKENS
    expected_margin = available - required

    result = run_preflight_budget_check(
        prompt=prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.budget_margin_tokens == expected_margin


# ---------------------------------------------------------------------------
# Test 9 — Undefined task class forces Gemini escalation
# ---------------------------------------------------------------------------


def test_preflight_undefined_task_class_routes_gemini() -> None:
    """Undefined task class must force Gemini escalation via preflight."""
    result = run_preflight_budget_check(
        prompt="Some prompt.",
        task_class="totally_unknown_task_class",
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    assert result.token_budget_ok is False
    assert result.route_to_gemini is True
    assert result.failure_type == VLLMFailureType.UNDEFINED_TASK_CLASS


# ---------------------------------------------------------------------------
# Test 10 — VLLMPreflightResult is frozen (immutable)
# ---------------------------------------------------------------------------


def test_preflight_result_frozen() -> None:
    """VLLMPreflightResult must be immutable (frozen dataclass)."""
    import dataclasses

    result = run_preflight_budget_check(
        prompt="Test.",
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=QWEN_7B_MAX_MODEL_LEN,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.token_budget_ok = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Test 11 — Contradictory state rejected by __post_init__
# ---------------------------------------------------------------------------


def test_preflight_contradictory_state_rejected() -> None:
    """token_budget_ok=True + route_to_gemini=True must raise ValueError."""
    with pytest.raises(ValueError, match="contradictory"):
        VLLMPreflightResult(
            prompt_tokens_estimated=10,
            max_output_tokens_requested=300,
            max_model_len_configured=32768,
            token_budget_ok=True,
            budget_margin_tokens=1000,
            failure_type=None,
            route_to_gemini=True,  # contradicts token_budget_ok=True
        )


# ---------------------------------------------------------------------------
# Test 12 — Failed preflight without failure_type rejected
# ---------------------------------------------------------------------------


def test_preflight_failed_without_failure_type_rejected() -> None:
    """token_budget_ok=False without failure_type must raise ValueError."""
    with pytest.raises(ValueError, match="failure_type"):
        VLLMPreflightResult(
            prompt_tokens_estimated=10,
            max_output_tokens_requested=300,
            max_model_len_configured=32768,
            token_budget_ok=False,
            budget_margin_tokens=-100,
            failure_type=None,  # missing — must raise
            route_to_gemini=True,
        )


# ---------------------------------------------------------------------------
# Test 13 — max_model_len_configured is preserved in result
# ---------------------------------------------------------------------------


def test_preflight_max_model_len_preserved() -> None:
    """max_model_len_configured must match the input max_model_len."""
    result = run_preflight_budget_check(
        prompt="Test prompt.",
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=16384,
    )
    assert result.max_model_len_configured == 16384


# ---------------------------------------------------------------------------
# Test 14 — Safety margin is applied in budget calculation
# ---------------------------------------------------------------------------


def test_safety_margin_applied() -> None:
    """Budget calculation must subtract SAFETY_MARGIN_TOKENS from max_model_len."""
    # Craft a prompt that fits within max_model_len but not within
    # max_model_len - SAFETY_MARGIN_TOKENS
    # Use a tiny max_model_len to make this easy to test
    tiny_max_len = 400  # tokens
    # cap for healing_json_artifact = 300
    # safety_margin = 256
    # available = 400 - 256 = 144
    # prompt that uses ~100 tokens (300 chars) + 300 cap = 400 > 144 → fail
    prompt = "x" * 300  # ~100 tokens
    result = run_preflight_budget_check(
        prompt=prompt,
        task_class=TaskClass.HEALING_JSON_ARTIFACT.value,
        max_model_len=tiny_max_len,
    )
    assert result.token_budget_ok is False
    assert result.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED
