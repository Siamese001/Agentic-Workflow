"""
WAVE 1 tests — Serving profile selection + vLLM request shaping.

Validates:
- Correct profile selected for low/medium/high severity
- Token budget gate uses profile max_model_len (not any other source)
- Local request payload always includes explicit max_tokens
- Determinism policy enforced: temperature=0, top_p=1.0, seed=42
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

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLM_SEED,
    VLLM_TEMPERATURE,
    VLLM_TOP_P,
    select_serving_profile,
    shape_local_request,
)
from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    LOCAL_FAST_7B_MAX_MODEL_LEN,
    LOCAL_STRONG_14B_MAX_MODEL_LEN,
    PROFILE_LOCAL_FAST_7B,
    PROFILE_LOCAL_STRONG_14B,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    TASK_CLASS_OUTPUT_CAPS,
    TaskClass,
)

# ---------------------------------------------------------------------------
# Profile selection tests
# ---------------------------------------------------------------------------


def test_low_severity_selects_fast_7b():
    profile = select_serving_profile("low")
    assert profile.profile_name == "LOCAL_FAST_7B"


def test_medium_severity_selects_fast_7b():
    profile = select_serving_profile("medium")
    assert profile.profile_name == "LOCAL_FAST_7B"


def test_high_severity_selects_strong_14b():
    profile = select_serving_profile("high")
    assert profile.profile_name == "LOCAL_STRONG_14B"


def test_low_severity_profile_model_id():
    profile = select_serving_profile("low")
    assert "7B" in profile.model or "7b" in profile.model


def test_high_severity_profile_model_id():
    profile = select_serving_profile("high")
    assert "14B" in profile.model or "14b" in profile.model


def test_profile_max_model_len_low():
    profile = select_serving_profile("low")
    assert profile.max_model_len == LOCAL_FAST_7B_MAX_MODEL_LEN


def test_profile_max_model_len_high():
    profile = select_serving_profile("high")
    assert profile.max_model_len == LOCAL_STRONG_14B_MAX_MODEL_LEN


# ---------------------------------------------------------------------------
# Request shaping tests
# ---------------------------------------------------------------------------


def test_shaped_request_has_explicit_max_tokens():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.max_tokens is not None
    assert req.max_tokens > 0


def test_shaped_request_max_tokens_matches_task_cap():
    task_class = TaskClass.PATCH_SUGGESTION.value
    req = shape_local_request("hello", task_class, PROFILE_LOCAL_FAST_7B)
    assert req.max_tokens == TASK_CLASS_OUTPUT_CAPS[task_class]


def test_shaped_request_temperature_is_zero():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.temperature == VLLM_TEMPERATURE
    assert req.temperature == 0.0


def test_shaped_request_top_p_is_one():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.top_p == VLLM_TOP_P
    assert req.top_p == 1.0


def test_shaped_request_seed_is_fixed():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.seed == VLLM_SEED
    assert req.seed == 42


def test_shaped_request_uses_profile_max_model_len():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.max_model_len == PROFILE_LOCAL_FAST_7B.max_model_len


def test_shaped_request_14b_uses_14b_max_model_len():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_STRONG_14B)
    assert req.max_model_len == PROFILE_LOCAL_STRONG_14B.max_model_len


def test_shaped_request_profile_name_recorded():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.profile_name == "LOCAL_FAST_7B"


def test_shaped_request_undefined_task_class_raises():
    with pytest.raises(ValueError, match="no output cap"):
        shape_local_request("hello", "undefined_class", PROFILE_LOCAL_FAST_7B)


def test_shaped_request_healing_json_artifact():
    req = shape_local_request("hello", TaskClass.HEALING_JSON_ARTIFACT.value, PROFILE_LOCAL_FAST_7B)
    assert req.max_tokens == TASK_CLASS_OUTPUT_CAPS[TaskClass.HEALING_JSON_ARTIFACT.value]


def test_shaped_request_is_deterministic():
    req1 = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    req2 = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req1 == req2


def test_shaped_request_model_matches_profile():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.model == PROFILE_LOCAL_FAST_7B.model
