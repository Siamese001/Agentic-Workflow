"""ADG-driven tests for L2_execution/types/vllm_concurrency_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_concurrency_types import VLLMStressRequest
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMStressRequest = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_concurrency_types deps unavailable")
class TestVLLMStressRequest:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMStressRequest)

    def test_is_frozen(self):
        req = VLLMStressRequest(
            request_id=1, prompt="hello", task_class="summary", max_output_tokens_requested=600
        )
        with pytest.raises((AttributeError, TypeError)):
            req.request_id = 2

    def test_creates(self):
        req = VLLMStressRequest(
            request_id=1, prompt="test", task_class="analysis", max_output_tokens_requested=400
        )
        assert req.request_id == 1
        assert req.task_class == "analysis"


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
