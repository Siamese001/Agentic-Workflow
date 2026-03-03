"""
WAVE 1 tests — Authoritative serving profile constants and config validation.

Validates:
- Profile constants are hardcoded (not env-derived)
- Startup fails on invalid configuration
- Co-change invariant enforcement
- 14B max_model_len ceiling guard
- No 32B tier, no quantized tier
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    GPU_MEMORY_UTILIZATION,
    GPU_VRAM_GB,
    LOCAL_FAST_7B_MAX_MODEL_LEN,
    LOCAL_FAST_7B_MAX_NUM_SEQS,
    LOCAL_FAST_7B_MODEL,
    LOCAL_STRONG_14B_MAX_MODEL_LEN,
    LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING,
    LOCAL_STRONG_14B_MAX_NUM_SEQS,
    LOCAL_STRONG_14B_MODEL,
    PROFILE_LOCAL_FAST_7B,
    PROFILE_LOCAL_STRONG_14B,
    SERVING_PROFILE_REGISTRY,
    VLLMCoChangeViolation,
    VLLMServingProfile,
    VLLMServingProfileInvalid,
    assert_no_simultaneous_increase,
    get_profile,
)

# ---------------------------------------------------------------------------
# Profile constant tests
# ---------------------------------------------------------------------------


def test_local_fast_7b_model_id():
    assert LOCAL_FAST_7B_MODEL == "Qwen/Qwen2.5-7B-Instruct"


def test_local_strong_14b_model_id():
    assert LOCAL_STRONG_14B_MODEL == "Qwen/Qwen2.5-14B-Instruct"


def test_local_fast_7b_max_model_len():
    assert LOCAL_FAST_7B_MAX_MODEL_LEN == 8192


def test_local_strong_14b_max_model_len():
    assert LOCAL_STRONG_14B_MAX_MODEL_LEN == 4096


def test_local_fast_7b_max_num_seqs():
    assert LOCAL_FAST_7B_MAX_NUM_SEQS == 4


def test_local_strong_14b_max_num_seqs():
    assert LOCAL_STRONG_14B_MAX_NUM_SEQS == 2


def test_gpu_memory_utilization():
    assert GPU_MEMORY_UTILIZATION == 0.85


def test_gpu_vram_gb():
    assert GPU_VRAM_GB == 32


def test_14b_ceiling():
    assert LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING == 8192


def test_14b_max_model_len_within_ceiling():
    assert LOCAL_STRONG_14B_MAX_MODEL_LEN <= LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING


# ---------------------------------------------------------------------------
# Profile instance tests
# ---------------------------------------------------------------------------


def test_profile_local_fast_7b_is_valid():
    assert PROFILE_LOCAL_FAST_7B.profile_name == "LOCAL_FAST_7B"
    assert PROFILE_LOCAL_FAST_7B.model == LOCAL_FAST_7B_MODEL
    assert PROFILE_LOCAL_FAST_7B.max_model_len == LOCAL_FAST_7B_MAX_MODEL_LEN
    assert PROFILE_LOCAL_FAST_7B.max_num_seqs == LOCAL_FAST_7B_MAX_NUM_SEQS


def test_profile_local_strong_14b_is_valid():
    assert PROFILE_LOCAL_STRONG_14B.profile_name == "LOCAL_STRONG_14B"
    assert PROFILE_LOCAL_STRONG_14B.model == LOCAL_STRONG_14B_MODEL
    assert PROFILE_LOCAL_STRONG_14B.max_model_len == LOCAL_STRONG_14B_MAX_MODEL_LEN
    assert PROFILE_LOCAL_STRONG_14B.max_num_seqs == LOCAL_STRONG_14B_MAX_NUM_SEQS


def test_registry_contains_both_tiers():
    assert "local_fast" in SERVING_PROFILE_REGISTRY
    assert "local_strong" in SERVING_PROFILE_REGISTRY


def test_get_profile_local_fast():
    p = get_profile("local_fast")
    assert p.profile_name == "LOCAL_FAST_7B"


def test_get_profile_local_strong():
    p = get_profile("local_strong")
    assert p.profile_name == "LOCAL_STRONG_14B"


def test_get_profile_unknown_raises():
    with pytest.raises(KeyError):
        get_profile("local_32b")


# ---------------------------------------------------------------------------
# Startup validation guard tests
# ---------------------------------------------------------------------------


def test_invalid_max_model_len_zero_raises():
    with pytest.raises(VLLMServingProfileInvalid):
        VLLMServingProfile(
            profile_name="LOCAL_FAST_7B",
            model=LOCAL_FAST_7B_MODEL,
            max_model_len=0,
            max_num_seqs=4,
            gpu_memory_utilization=0.85,
        )


def test_invalid_max_num_seqs_zero_raises():
    with pytest.raises(VLLMServingProfileInvalid):
        VLLMServingProfile(
            profile_name="LOCAL_FAST_7B",
            model=LOCAL_FAST_7B_MODEL,
            max_model_len=8192,
            max_num_seqs=0,
            gpu_memory_utilization=0.85,
        )


def test_invalid_gpu_utilization_zero_raises():
    with pytest.raises(VLLMServingProfileInvalid):
        VLLMServingProfile(
            profile_name="LOCAL_FAST_7B",
            model=LOCAL_FAST_7B_MODEL,
            max_model_len=8192,
            max_num_seqs=4,
            gpu_memory_utilization=0.0,
        )


def test_14b_exceeds_ceiling_raises():
    with pytest.raises(VLLMServingProfileInvalid) as exc_info:
        VLLMServingProfile(
            profile_name="LOCAL_STRONG_14B",
            model=LOCAL_STRONG_14B_MODEL,
            max_model_len=LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING + 1,
            max_num_seqs=2,
            gpu_memory_utilization=0.85,
        )
    assert "hard fail at startup" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Co-change invariant tests
# ---------------------------------------------------------------------------


def test_co_change_both_increase_raises():
    with pytest.raises(VLLMCoChangeViolation):
        assert_no_simultaneous_increase(
            old_max_model_len=4096,
            new_max_model_len=8192,
            old_max_num_seqs=1,
            new_max_num_seqs=2,
            profile_name="LOCAL_STRONG_14B",
        )


def test_co_change_only_model_len_increase_ok():
    assert_no_simultaneous_increase(
        old_max_model_len=4096,
        new_max_model_len=8192,
        old_max_num_seqs=2,
        new_max_num_seqs=2,
        profile_name="LOCAL_STRONG_14B",
    )


def test_co_change_only_num_seqs_increase_ok():
    assert_no_simultaneous_increase(
        old_max_model_len=4096,
        new_max_model_len=4096,
        old_max_num_seqs=1,
        new_max_num_seqs=2,
        profile_name="LOCAL_STRONG_14B",
    )


def test_co_change_both_decrease_ok():
    assert_no_simultaneous_increase(
        old_max_model_len=8192,
        new_max_model_len=4096,
        old_max_num_seqs=2,
        new_max_num_seqs=1,
        profile_name="LOCAL_STRONG_14B",
    )


# ---------------------------------------------------------------------------
# No 32B / quantized tier invariants
# ---------------------------------------------------------------------------


def test_no_32b_in_registry():
    for key in SERVING_PROFILE_REGISTRY:
        assert "32b" not in key.lower()
        assert "32B" not in SERVING_PROFILE_REGISTRY[key].model


def test_no_quantized_in_registry():
    for key in SERVING_PROFILE_REGISTRY:
        model = SERVING_PROFILE_REGISTRY[key].model.lower()
        assert "awq" not in model
        assert "gptq" not in model
        assert "gguf" not in model
        assert "int4" not in model
        assert "int8" not in model
