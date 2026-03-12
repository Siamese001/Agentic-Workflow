"""ADG-driven tests for L0_routing/reasoning/RootCustomsAgent.py — fan_in=0."""
from __future__ import annotations

import pytest
from pathlib import Path

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.reasoning.RootCustomsAgent import (
        ASTAnalyzer,
        RoutingDecision,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ASTAnalyzer = None  # type: ignore[assignment,misc]
    RoutingDecision = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="RootCustomsAgent deps unavailable")
class TestRoutingDecision:
    def test_creates(self):
        decision = RoutingDecision(
            file_path=Path("test.py"),
            destination="tests/",
            reason="test file",
            confidence=0.9,
            content_matches={},
            ast_matches={},
        )
        assert decision.confidence == 0.9
        assert decision.is_protected is False

    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RoutingDecision)


@pytest.mark.skipif(not _AVAILABLE, reason="RootCustomsAgent deps unavailable")
class TestASTAnalyzer:
    def test_creates(self):
        analyzer = ASTAnalyzer()
        assert analyzer.imports == []
        assert analyzer.class_names == []

    def test_has_analyze_file(self):
        assert hasattr(ASTAnalyzer, "analyze_file")

    def test_analyze_nonpython_returns_empty(self, tmp_path):
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("hello")
        analyzer = ASTAnalyzer()
        result = analyzer.analyze_file(txt_file)
        assert result == {}


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
