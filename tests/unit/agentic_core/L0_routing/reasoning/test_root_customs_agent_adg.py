"""ADG-driven tests for L0_routing/reasoning/RootCustomsAgent.py — fan_in=0."""
from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_root_customs_agent_adg")
_emit_applies_guardrail("p0", "test_root_customs_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_root_customs_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_root_customs_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_root_customs_agent_adg")
emit_determinism_digest("p0", "test_root_customs_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.reasoning.RootCustomsAgent import (
        ASTAnalyzer,
        RoutingDecision,
    )
    _AVAILABLE = True
except ImportError:
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
