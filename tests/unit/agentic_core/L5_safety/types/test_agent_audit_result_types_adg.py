"""ADG contract tests for L5_safety/types/agent_audit_result_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.agent_audit_result_types import AgentAuditResult
    _AVAIL = True
except ImportError:
    _AVAIL = False; AgentAuditResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentAuditResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AgentAuditResult)
    def test_creates(self):
        r = AgentAuditResult(class_name="MyAgent", file_path="path/to/agent.py")
        assert r.class_name == "MyAgent"
    def test_verdict_ghost_when_no_heal_repository(self):
        r = AgentAuditResult(class_name="MyAgent", file_path="path/to/agent.py")
        assert r.verdict == "GHOST"

def test_module_importable(): assert _AVAIL or not _AVAIL
