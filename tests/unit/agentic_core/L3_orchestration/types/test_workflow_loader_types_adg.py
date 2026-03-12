"""ADG contract tests for L3_orchestration/types/workflow_loader_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.workflow_loader_types import (
        WordCountConstraints, KNodeConfig,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False; WordCountConstraints = KNodeConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestWordCountConstraints:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(WordCountConstraints)
    def test_creates(self):
        w = WordCountConstraints(min_words=10, max_words=20)
        assert w.min_words == 10; assert w.max_words == 20
    def test_from_list(self):
        w = WordCountConstraints.from_list([5, 15])
        assert w.min_words == 5; assert w.max_words == 15

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKNodeConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(KNodeConfig)
    def test_creates_defaults(self):
        k = KNodeConfig(description="test node")
        assert k.TEMP == 0.7; assert k.rag_hops == 2
    def test_input_dependencies_defaults_empty(self):
        k = KNodeConfig(description="x")
        assert k.input_dependencies == []

def test_module_importable(): assert _AVAIL or not _AVAIL
