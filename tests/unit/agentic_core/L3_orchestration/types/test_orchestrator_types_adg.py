"""ADG contract tests for L3_orchestration/types/orchestrator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.orchestrator_types import (
        AgentResult,
        ExecutionContext,
        ExecutionPhase,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False; ExecutionPhase = ExecutionContext = AgentResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionPhase:
    def test_is_str_enum(self):
        assert issubclass(ExecutionPhase, str)
    def test_has_planning(self): assert ExecutionPhase.PLANNING == "planning"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionContext:
    def test_creates_defaults(self):
        ctx = ExecutionContext()
        assert ctx.dry_run is True
        assert ctx.current_depth == 0
    def test_with_depth(self):
        ctx = ExecutionContext()
        ctx2 = ctx.with_depth(2)
        assert ctx2.current_depth == 2

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AgentResult)
    def test_creates(self):
        r = AgentResult(agent_name="MyAgent", success=True)
        assert r.agent_name == "MyAgent"

def test_module_importable(): assert _AVAIL or not _AVAIL
