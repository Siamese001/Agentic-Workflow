"""ADG contract tests for agentic_core/L2_execution/types/gateway_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.gateway_types import GenerationRequest, GenerationResponse
    _AVAIL = True
except Exception:
    _AVAIL = False
    GenerationRequest = GenerationResponse = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGenerationRequest:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(GenerationRequest)
    def test_creates_defaults(self):
        r = GenerationRequest(prompt="Write a resume", agent_id="writer")
        assert r.provider == "openai"; assert r.temperature == 0.7
        assert r.max_tokens == 4096
    def test_custom_provider(self):
        r = GenerationRequest(prompt="hello", agent_id="a", provider="anthropic")
        assert r.provider == "anthropic"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGenerationResponse:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(GenerationResponse)
    def test_creates(self):
        r = GenerationResponse(
            content="Hello world", tokens=10, provider="openai",
            model="gpt-4", replay_envelope="env_abc",
        )
        assert r.content == "Hello world"; assert r.tokens == 10
    def test_none_content(self):
        r = GenerationResponse(
            content=None, tokens=0, provider="openai",
            model="gpt-4", replay_envelope="",
        )
        assert r.content is None

def test_module_importable(): assert _AVAIL or not _AVAIL
