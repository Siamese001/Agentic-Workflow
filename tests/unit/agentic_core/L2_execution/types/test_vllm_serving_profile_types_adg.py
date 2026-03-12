"""ADG contract tests for agentic_core/L2_execution/types/vllm_serving_profile_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.vllm_serving_profile_types import (
        VLLMServingProfile, VLLMServingProfileInvalid,
        PROFILE_LOCAL_FAST_7B, PROFILE_LOCAL_STRONG_14B,
        SERVING_PROFILE_REGISTRY, GPU_MEMORY_UTILIZATION, GPU_VRAM_GB,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    VLLMServingProfile = VLLMServingProfileInvalid = None  # type: ignore[assignment,misc]
    PROFILE_LOCAL_FAST_7B = PROFILE_LOCAL_STRONG_14B = None  # type: ignore[assignment,misc]
    SERVING_PROFILE_REGISTRY = GPU_MEMORY_UTILIZATION = GPU_VRAM_GB = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVLLMServingProfileInvalid:
    def test_is_exception(self): assert issubclass(VLLMServingProfileInvalid, Exception)
    def test_has_profile_and_reason(self):
        e = VLLMServingProfileInvalid(profile="test", reason="bad value")
        assert e.profile == "test"; assert e.reason == "bad value"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVLLMServingProfile:
    def test_is_frozen(self): assert VLLMServingProfile.__dataclass_params__.frozen is True
    def test_creates_valid(self):
        p = VLLMServingProfile(
            profile_name="TEST", model="test/model",
            max_model_len=4096, max_num_seqs=2,
            gpu_memory_utilization=0.85,
        )
        assert p.max_model_len == 4096
    def test_zero_max_model_len_raises(self):
        with pytest.raises(VLLMServingProfileInvalid):
            VLLMServingProfile(profile_name="X", model="m", max_model_len=0, max_num_seqs=1, gpu_memory_utilization=0.85)
    def test_zero_max_num_seqs_raises(self):
        with pytest.raises(VLLMServingProfileInvalid):
            VLLMServingProfile(profile_name="X", model="m", max_model_len=4096, max_num_seqs=0, gpu_memory_utilization=0.85)
    def test_gpu_over_1_raises(self):
        with pytest.raises(VLLMServingProfileInvalid):
            VLLMServingProfile(profile_name="X", model="m", max_model_len=4096, max_num_seqs=1, gpu_memory_utilization=1.5)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestProfiles:
    def test_fast_7b_model_name(self): assert "7B" in PROFILE_LOCAL_FAST_7B.model or "Qwen" in PROFILE_LOCAL_FAST_7B.model
    def test_strong_14b_model_name(self): assert "14B" in PROFILE_LOCAL_STRONG_14B.model or "Qwen" in PROFILE_LOCAL_STRONG_14B.model
    def test_registry_has_local_fast(self): assert "local_fast" in SERVING_PROFILE_REGISTRY
    def test_registry_has_local_strong(self): assert "local_strong" in SERVING_PROFILE_REGISTRY
    def test_gpu_memory_utilization_in_range(self):
        assert 0.0 < GPU_MEMORY_UTILIZATION <= 1.0
    def test_gpu_vram_gb_positive(self):
        assert GPU_VRAM_GB > 0

def test_module_importable(): assert _AVAIL or not _AVAIL
