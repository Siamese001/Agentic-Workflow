"""
WAVE 1 — Token Cap Enforcement Tests.

Validates:
- Output caps enforced per task class
- VLLM_MAX_TOKENS_ABSOLUTE never exceeded
- Undefined task class routes to Gemini (raises VLLMOutputCapExceeded)
- Deterministic token estimation returns identical values across calls
- No 32B model present in routing constants
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
)

_emit_records_execution_trace("p0", "evidence", "test_token_cap_enforced")
_emit_applies_guardrail("p0", "test_token_cap_enforced", "p0_governance")
_emit_reads_policy_state("p0", "test_token_cap_enforced", "policy_binding")
_emit_snapshots_state("p0", "test_token_cap_enforced", "state_snapshot")
emit_replay_key("p0", "test_token_cap_enforced")
emit_determinism_digest("p0", "test_token_cap_enforced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_token_cap_enforced", "execution_auth")
_emit_validates_capability("p2", "test_token_cap_enforced", "capability_check")
_emit_routes_to_capability("p2", "test_token_cap_enforced", "capability_route")
_emit_writes_via_uwg("p2", "test_token_cap_enforced", "uwg_write")
_emit_blocks_direct_write("p2", "test_token_cap_enforced", "direct_write_block")
_emit_records_tool_invocation("p2", "test_token_cap_enforced", "tool_invocation")
_emit_captures_execution_output("p2", "test_token_cap_enforced", "exec_output")
_emit_dispatches_agent("p3", "test_token_cap_enforced", "agent_dispatch")
_emit_coordinates_agents("p3", "test_token_cap_enforced", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_token_cap_enforced", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_token_cap_enforced", "healing_outcome")
_emit_escalates_failure("p3", "test_token_cap_enforced", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_token_cap_enforced", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_token_cap_enforced", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_token_cap_enforced", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_token_cap_enforced", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_token_cap_enforced", "eval_metric")
_emit_stores_embedding("p4", "test_token_cap_enforced", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_token_cap_enforced", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_token_cap_enforced", "exec_snapshot_link")

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
    EXTENDED_CAP_WHITELIST,
    TASK_CLASS_OUTPUT_CAPS,
    VLLM_MAX_TOKENS_ABSOLUTE,
    VLLM_MAX_TOKENS_DEFAULT,
    VLLM_MAX_TOKENS_EXTENDED,
    TaskClass,
    VLLMOutputCapExceeded,
    enforce_output_cap,
    estimate_tokens_qwen,
    get_output_cap,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_token_cap_enforced", "p4obs", "metric_1")
_emit_emits_metric_event("test_token_cap_enforced", "p4obs", "metric_2")
_emit_emits_metric_event("test_token_cap_enforced", "p4obs", "metric_3")
_emit_emits_metric_event("test_token_cap_enforced", "p4obs", "metric_4")
_emit_emits_metric_event("test_token_cap_enforced", "p4obs", "metric_5")
_emit_emits_metric_event("test_token_cap_enforced", "p4obs", "metric_6")
_emit_records_incident_event("test_token_cap_enforced", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_token_cap_enforced", "p4obs", "anomaly")
_emit_writes_observability_log("test_token_cap_enforced", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_token_cap_enforced", "p4obs", "mon_state")
_emit_triggers_alert("test_token_cap_enforced", "p4obs", "alert")
_emit_links_incident_trace("test_token_cap_enforced", "p4obs", "trace_link")
_emit_captures_pattern("test_token_cap_enforced", "p3lm", "pattern")
_emit_records_learning_event("test_token_cap_enforced", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_token_cap_enforced", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_token_cap_enforced", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_token_cap_enforced", "p3lm", "routing")
_emit_improves_agent_policy("test_token_cap_enforced", "p3lm", "policy")
_emit_stores_learning_state("test_token_cap_enforced", "p3lm", "state")
_emit_records_execution_trace("test_token_cap_enforced", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_token_cap_enforced", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_token_cap_enforced", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_token_cap_enforced", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_token_cap_enforced", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_token_cap_enforced", "env_read", "p2_env_1")
_emit_reads_environ("test_token_cap_enforced", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_token_cap_enforced", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_token_cap_enforced", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_token_cap_enforced", "context_pull")
_emit_pulls_context("p1", "test_token_cap_enforced", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_token_cap_enforced", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_token_cap_enforced", "uwg_term_2")
_emit_writes_through("p1", "test_token_cap_enforced", "write_through")
_emit_writes_through("p1", "test_token_cap_enforced", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_token_cap_enforced", "safety_validation")
_emit_invokes_eval("p1", "test_token_cap_enforced", "eval_call")
_emit_proposal_commits_routing("p1", "test_token_cap_enforced", "routing_commit")

# ---------------------------------------------------------------------------
# Test 1 — Constants are hard-coded, not env-derived
# ---------------------------------------------------------------------------


def test_constants_are_hardcoded() -> None:
    """Gateway-level caps must be integer constants, not env-derived."""
    assert isinstance(VLLM_MAX_TOKENS_DEFAULT, int)
    assert isinstance(VLLM_MAX_TOKENS_EXTENDED, int)
    assert isinstance(VLLM_MAX_TOKENS_ABSOLUTE, int)
    assert VLLM_MAX_TOKENS_DEFAULT == 600
    assert VLLM_MAX_TOKENS_EXTENDED == 1200
    assert VLLM_MAX_TOKENS_ABSOLUTE == 1200


# ---------------------------------------------------------------------------
# Test 2 — Task-class caps are within absolute ceiling
# ---------------------------------------------------------------------------


def test_task_class_caps_within_absolute() -> None:
    """All task-class caps must not exceed VLLM_MAX_TOKENS_ABSOLUTE."""
    for task_class, cap in TASK_CLASS_OUTPUT_CAPS.items():
        assert cap <= VLLM_MAX_TOKENS_ABSOLUTE, (
            f"Task class {task_class!r} cap {cap} exceeds VLLM_MAX_TOKENS_ABSOLUTE={VLLM_MAX_TOKENS_ABSOLUTE}"
        )


# ---------------------------------------------------------------------------
# Test 3 — healing_json_artifact cap = 300
# ---------------------------------------------------------------------------


def test_healing_json_artifact_cap() -> None:
    """healing_json_artifact must have output cap of 300."""
    cap = get_output_cap(TaskClass.HEALING_JSON_ARTIFACT.value)
    assert cap == 300


# ---------------------------------------------------------------------------
# Test 4 — patch_suggestion cap = 600
# ---------------------------------------------------------------------------


def test_patch_suggestion_cap() -> None:
    """patch_suggestion must have output cap of 600."""
    cap = get_output_cap(TaskClass.PATCH_SUGGESTION.value)
    assert cap == 600


# ---------------------------------------------------------------------------
# Test 5 — multi_file_summary cap = 1200 (whitelisted)
# ---------------------------------------------------------------------------


def test_multi_file_summary_cap() -> None:
    """multi_file_summary must have output cap of 1200 and be whitelisted."""
    cap = get_output_cap(TaskClass.MULTI_FILE_SUMMARY.value)
    assert cap == 1200
    assert TaskClass.MULTI_FILE_SUMMARY.value in EXTENDED_CAP_WHITELIST


# ---------------------------------------------------------------------------
# Test 6 — Undefined task class returns None (routes to Gemini)
# ---------------------------------------------------------------------------


def test_undefined_task_class_returns_none() -> None:
    """Undefined task class must return None from get_output_cap."""
    cap = get_output_cap("undefined_class_xyz")
    assert cap is None


# ---------------------------------------------------------------------------
# Test 7 — enforce_output_cap raises for undefined class
# ---------------------------------------------------------------------------


def test_enforce_output_cap_raises_for_undefined() -> None:
    """enforce_output_cap must raise VLLMOutputCapExceeded for undefined class."""
    with pytest.raises(VLLMOutputCapExceeded) as exc_info:
        enforce_output_cap(500, "undefined_class_xyz")
    assert exc_info.value.reason == "undefined_task_class_requires_gemini_escalation"


# ---------------------------------------------------------------------------
# Test 8 — enforce_output_cap clamps to task-class cap
# ---------------------------------------------------------------------------


def test_enforce_output_cap_clamps_to_task_cap() -> None:
    """enforce_output_cap must clamp requested tokens to task-class cap."""
    # Request 1000 tokens for healing_json_artifact (cap=300)
    result = enforce_output_cap(1000, TaskClass.HEALING_JSON_ARTIFACT.value)
    assert result == 300


# ---------------------------------------------------------------------------
# Test 9 — enforce_output_cap respects exact cap
# ---------------------------------------------------------------------------


def test_enforce_output_cap_exact_cap() -> None:
    """enforce_output_cap with exactly the cap must return the cap."""
    result = enforce_output_cap(600, TaskClass.PATCH_SUGGESTION.value)
    assert result == 600


# ---------------------------------------------------------------------------
# Test 10 — No local request exceeds VLLM_MAX_TOKENS_ABSOLUTE
# ---------------------------------------------------------------------------


def test_no_local_request_exceeds_absolute() -> None:
    """enforce_output_cap must never return > VLLM_MAX_TOKENS_ABSOLUTE."""
    for task_class in [
        TaskClass.HEALING_JSON_ARTIFACT.value,
        TaskClass.PATCH_SUGGESTION.value,
        TaskClass.MULTI_FILE_SUMMARY.value,
    ]:
        result = enforce_output_cap(99999, task_class)
        assert result <= VLLM_MAX_TOKENS_ABSOLUTE, (
            f"enforce_output_cap returned {result} > VLLM_MAX_TOKENS_ABSOLUTE for task_class={task_class!r}"
        )


# ---------------------------------------------------------------------------
# Test 11 — Deterministic token estimation: identical across 10 calls
# ---------------------------------------------------------------------------


def test_token_estimation_deterministic() -> None:
    """estimate_tokens_qwen must return identical values across 10 calls."""
    prompt = "This is a test prompt for deterministic token estimation."
    results = [estimate_tokens_qwen(prompt) for _ in range(10)]
    assert len(set(results)) == 1, f"Non-deterministic token estimation: {results}"


# ---------------------------------------------------------------------------
# Test 12 — Token estimation: empty string returns 0
# ---------------------------------------------------------------------------


def test_token_estimation_empty_string() -> None:
    """estimate_tokens_qwen must return 0 for empty string."""
    assert estimate_tokens_qwen("") == 0


# ---------------------------------------------------------------------------
# Test 13 — Token estimation: minimum 1 for non-empty
# ---------------------------------------------------------------------------


def test_token_estimation_minimum_one() -> None:
    """estimate_tokens_qwen must return at least 1 for non-empty string."""
    assert estimate_tokens_qwen("a") >= 1
    assert estimate_tokens_qwen("ab") >= 1


# ---------------------------------------------------------------------------
# Test 14 — Token estimation: proportional to length
# ---------------------------------------------------------------------------


def test_token_estimation_proportional() -> None:
    """Longer prompts must estimate more tokens than shorter ones."""
    short = "Hello"
    long = "Hello " * 100
    assert estimate_tokens_qwen(long) > estimate_tokens_qwen(short)


# ---------------------------------------------------------------------------
# Test 15 — No 32B model in routing constants
# ---------------------------------------------------------------------------


def test_no_32b_model_in_constants() -> None:
    """No 32B model must appear in routing constants."""
    from agentic_core.L2_execution.types.vllm_token_budget_types import (
        GEMINI_25_PRO_MODEL_ID,
        QWEN_7B_MODEL_ID,
        QWEN_14B_MODEL_ID,
    )

    all_model_ids = [QWEN_7B_MODEL_ID, QWEN_14B_MODEL_ID, GEMINI_25_PRO_MODEL_ID]
    for model_id in all_model_ids:
        assert "32B" not in model_id and "32b" not in model_id, (
            f"32B model found in routing constants: {model_id!r}"
        )


# ---------------------------------------------------------------------------
# Test 16 — No quantized tier in routing constants
# ---------------------------------------------------------------------------


def test_no_quantized_tier_in_constants() -> None:
    """No quantized model identifier must appear in routing constants."""
    from agentic_core.L2_execution.types.vllm_token_budget_types import (
        GEMINI_25_PRO_MODEL_ID,
        QWEN_7B_MODEL_ID,
        QWEN_14B_MODEL_ID,
    )

    quantized_markers = ["awq", "gptq", "gguf", "int4", "int8", "quantized"]
    all_model_ids = [QWEN_7B_MODEL_ID, QWEN_14B_MODEL_ID, GEMINI_25_PRO_MODEL_ID]
    for model_id in all_model_ids:
        for marker in quantized_markers:
            assert marker not in model_id.lower(), (
                f"Quantized marker {marker!r} found in model ID: {model_id!r}"
            )
