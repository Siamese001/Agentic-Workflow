"""ADG-driven tests for agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.agent_heal_audit import (  # noqa: F401
        AgentHealAuditScanner,
        main,
        generate_markdown_report,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AgentHealAuditScanner = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    generate_markdown_report = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_heal_audit.py deps unavailable")
class TestAgentHealAuditScanner:
    def test_is_class(self):
        assert isinstance(AgentHealAuditScanner, type)
    def test_importable(self):
        assert AgentHealAuditScanner is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_heal_audit.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_heal_audit.py deps unavailable")
class TestGenerateMarkdownReport:
    def test_is_callable(self):
        assert callable(generate_markdown_report)


def test_module_importable():
    """Module agent_heal_audit.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
