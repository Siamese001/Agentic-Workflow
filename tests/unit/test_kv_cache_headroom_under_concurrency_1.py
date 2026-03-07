"""
WAVE 2 tests — KV cache headroom under concurrency stress.

Validates:
- Worst-case prompt near budget ceiling passes preflight
- No truncation within max_model_len
- No unexpected fallback when token_budget_ok=True
- No output exceeds VLLM_MAX_TOKENS_ABSOLUTE
- Concurrent requests within max_num_seqs behave deterministically
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_concurrency_types import (
    VLLMStressRequest,
    build_worst_case_prompt,
    validate_concurrency_headroom,
)
from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    PROFILE_LOCAL_FAST_7B,
    PROFILE_LOCAL_STRONG_14B,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    TASK_CLASS_OUTPUT_CAPS,
    VLLM_MAX_TOKENS_ABSOLUTE,
    TaskClass,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_requests(profile, task_class: str, n: int) -> list[VLLMStressRequest]:
    cap = TASK_CLASS_OUTPUT_CAPS[task_class]
    prompt = build_worst_case_prompt(profile, cap)
    return [
        VLLMStressRequest(
            request_id=i,
            prompt=prompt,
            task_class=task_class,
            max_output_tokens_requested=cap,
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# WAVE 2 — 7B profile stress tests
# ---------------------------------------------------------------------------


def test_7b_worst_case_prompt_passes_preflight():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.all_within_budget, "Worst-case prompt should pass preflight on 7B"


def test_7b_no_truncation_at_ceiling():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert not result.any_truncation, "No truncation expected at budget ceiling on 7B"


def test_7b_no_unexpected_fallback():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert not result.any_unexpected_fallback, "No unexpected fallback when budget OK"


def test_7b_no_absolute_exceeded():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert not result.any_absolute_exceeded, "No output exceeds VLLM_MAX_TOKENS_ABSOLUTE"


def test_7b_max_concurrency_within_budget():
    requests = make_requests(
        PROFILE_LOCAL_FAST_7B,
        TaskClass.PATCH_SUGGESTION.value,
        PROFILE_LOCAL_FAST_7B.max_num_seqs,
    )
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.num_requests == PROFILE_LOCAL_FAST_7B.max_num_seqs
    assert result.all_within_budget


def test_7b_healing_json_artifact_passes():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.HEALING_JSON_ARTIFACT.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.all_within_budget
    assert not result.any_truncation


def test_7b_deterministic_repeated_run():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 2)
    r1 = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    r2 = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert r1.all_within_budget == r2.all_within_budget
    assert r1.any_truncation == r2.any_truncation
    assert r1.any_unexpected_fallback == r2.any_unexpected_fallback


# ---------------------------------------------------------------------------
# WAVE 2 — 14B profile stress tests
# ---------------------------------------------------------------------------


def test_14b_worst_case_prompt_passes_preflight():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert result.all_within_budget, "Worst-case prompt should pass preflight on 14B"


def test_14b_no_truncation_at_ceiling():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert not result.any_truncation


def test_14b_no_unexpected_fallback():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert not result.any_unexpected_fallback


def test_14b_max_concurrency_within_budget():
    requests = make_requests(
        PROFILE_LOCAL_STRONG_14B,
        TaskClass.HEALING_JSON_ARTIFACT.value,
        PROFILE_LOCAL_STRONG_14B.max_num_seqs,
    )
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert result.num_requests == PROFILE_LOCAL_STRONG_14B.max_num_seqs
    assert result.all_within_budget


def test_14b_deterministic_repeated_run():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.HEALING_JSON_ARTIFACT.value, 1)
    r1 = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    r2 = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert r1.all_within_budget == r2.all_within_budget
    assert r1.any_truncation == r2.any_truncation


# ---------------------------------------------------------------------------
# WAVE 2 — Absolute ceiling invariant
# ---------------------------------------------------------------------------


def test_output_cap_never_exceeds_absolute():
    for task_class, cap in TASK_CLASS_OUTPUT_CAPS.items():
        assert cap <= VLLM_MAX_TOKENS_ABSOLUTE, (
            f"Task class {task_class!r} cap {cap} exceeds VLLM_MAX_TOKENS_ABSOLUTE={VLLM_MAX_TOKENS_ABSOLUTE}"
        )


def test_stress_result_fields_present():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.profile_name == "LOCAL_FAST_7B"
    assert result.max_num_seqs == PROFILE_LOCAL_FAST_7B.max_num_seqs
    assert len(result.request_results) == 1
    r = result.request_results[0]
    assert r.request_id == 0
    assert r.total_tokens_required > 0
