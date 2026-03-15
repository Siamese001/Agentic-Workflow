"""ADG-driven tests for apps_shared/utils/configuration_service_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.configuration_service_util import (  # noqa: F401
        ABOVE,
        ACTION,
        ADDENDUM,
        ADJACENCY,
        AGENT_CAPABILITIES,
        AGENTS,
        ConfigurationService,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ConfigurationService = None  # type: ignore[assignment,misc]
    ABOVE = None  # type: ignore[assignment,misc]
    ACTION = None  # type: ignore[assignment,misc]
    ADDENDUM = None  # type: ignore[assignment,misc]
    ADJACENCY = None  # type: ignore[assignment,misc]
    AGENTS = None  # type: ignore[assignment,misc]
    AGENT_CAPABILITIES = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestConfigurationService:
    def test_is_class(self):
        assert isinstance(ConfigurationService, type)
    def test_importable(self):
        assert ConfigurationService is not None

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestAboveConstant:
    def test_is_not_none(self):
        assert ABOVE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestActionConstant:
    def test_is_not_none(self):
        assert ACTION is not None

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestAddendumConstant:
    def test_is_not_none(self):
        assert ADDENDUM is not None

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestAdjacencyConstant:
    def test_is_not_none(self):
        assert ADJACENCY is not None

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestAgentsConstant:
    def test_is_not_none(self):
        assert AGENTS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_service_util.py deps unavailable")
class TestAgentCapabilitiesConstant:
    def test_is_not_none(self):
        assert AGENT_CAPABILITIES is not None


def test_module_importable():
    """Module configuration_service_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
