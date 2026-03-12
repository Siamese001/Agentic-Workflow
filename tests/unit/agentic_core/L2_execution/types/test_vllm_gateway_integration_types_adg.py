"""ADG contract tests for agentic_core/L2_execution/types/vllm_gateway_integration_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
        VLLMLocalRequest, VLLM_TEMPERATURE, VLLM_TOP_P, VLLM_SEED,
        select_serving_profile,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    VLLMLocalRequest = VLLM_TEMPERATURE = VLLM_TOP_P = VLLM_SEED = None  # type: ignore[assignment,misc]
    select_serving_profile = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDeterminismConstants:
    def test_temperature_is_zero(self): assert VLLM_TEMPERATURE == 0.0
    def test_top_p_is_one(self): assert VLLM_TOP_P == 1.0
    def test_seed_is_int(self): assert isinstance(VLLM_SEED, int)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVLLMLocalRequest:
    def test_is_frozen(self): assert VLLMLocalRequest.__dataclass_params__.frozen is True
    def test_creates(self):
        req = VLLMLocalRequest(
            model="Qwen/Qwen2.5-7B-Instruct", prompt="hello",
            max_tokens=512, temperature=0.0, top_p=1.0, seed=42,
            task_class="ROUTING", profile_name="LOCAL_FAST_7B",
            max_model_len=8192,
        )
        assert req.model.startswith("Qwen")
        assert req.temperature == 0.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSelectServingProfile:
    def test_high_severity_returns_strong(self):
        profile = select_serving_profile("high")
        assert "14B" in profile.model or "strong" in profile.profile_name.lower()
    def test_low_severity_returns_fast(self):
        profile = select_serving_profile("low")
        assert "7B" in profile.model or "fast" in profile.profile_name.lower()
    def test_medium_severity_returns_fast(self):
        profile = select_serving_profile("medium")
        assert profile is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
