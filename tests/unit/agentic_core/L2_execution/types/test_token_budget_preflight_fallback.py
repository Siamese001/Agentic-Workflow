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
