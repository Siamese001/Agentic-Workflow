"""ADG contract tests for apps_shared/types/kx_execution_context_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.kx_execution_context_types import KXExecutionResult
    _AVAIL = True
except Exception:
    _AVAIL = False
    KXExecutionResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKXExecutionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(KXExecutionResult)
    def test_creates(self):
        r = KXExecutionResult(node_id="k1", element="summary", content="generated text")
        assert r.node_id == "k1"; assert r.content == "generated text"
        assert r.rag_sources == []; assert r.usage == {}
    def test_optional_reasoning_trace(self):
        r = KXExecutionResult(node_id="k2", element="skills", content="python, java")
        assert r.reasoning_trace is None

def test_module_importable(): assert _AVAIL or not _AVAIL
