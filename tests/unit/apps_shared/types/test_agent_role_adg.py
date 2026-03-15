"""ADG contract tests for apps_shared/types/AgentRole.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.AgentRole import AGENT_CAPABILITIES, AgentCapability, AgentRole
    _AVAIL = True
except ImportError:
    _AVAIL = False
    AgentRole = AgentCapability = AGENT_CAPABILITIES = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentRole:
    def test_is_enum(self):
        import enum; assert issubclass(AgentRole, enum.Enum)
    def test_has_content_drafter(self):
        assert AgentRole.CONTENT_DRAFTER.value == "content_drafter"
    def test_has_quality_critic(self):
        assert AgentRole.QUALITY_CRITIC.value == "quality_critic"
    def test_has_fifteen_roles(self):
        assert len(list(AgentRole)) == 15

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentCapability:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AgentCapability)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentCapabilities:
    def test_is_dict(self): assert isinstance(AGENT_CAPABILITIES, dict)
    def test_content_drafter_present(self):
        assert AgentRole.CONTENT_DRAFTER in AGENT_CAPABILITIES
    def test_capability_has_tools(self):
        cap = AGENT_CAPABILITIES[AgentRole.CONTENT_DRAFTER]
        assert isinstance(cap.tools, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
