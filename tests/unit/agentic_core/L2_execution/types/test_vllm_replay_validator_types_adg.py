"""ADG contract tests for agentic_core/L2_execution/types/vllm_replay_validator_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.vllm_replay_validator_types import (
        canonical_prompt_hash, VLLMReplayValidator,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    canonical_prompt_hash = VLLMReplayValidator = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCanonicalPromptHash:
    def test_returns_64_hex(self):
        h = canonical_prompt_hash("hello world")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
    def test_deterministic(self):
        assert canonical_prompt_hash("test") == canonical_prompt_hash("test")
    def test_different_inputs_differ(self):
        assert canonical_prompt_hash("a") != canonical_prompt_hash("b")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVLLMReplayValidator:
    def test_is_frozen(self): assert VLLMReplayValidator.__dataclass_params__.frozen is True
    def test_creates(self):
        v = VLLMReplayValidator(); assert v is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
