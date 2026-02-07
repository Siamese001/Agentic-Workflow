"""
Unit tests for AppBaseAgent.

Tests Phase 2A.3 - Base class standardization.
"""

from pathlib import Path
from unittest.mock import patch

import pytest


# Mock CoreIntegrityVerifier before importing AppBaseAgent
@pytest.fixture(autouse=True)
def mock_core_integrity():
    """Mock CoreIntegrityVerifier for all tests."""
    mock_path = (
        "agentic_core.L0_maintenance.enforcement"
        ".core_integrity_util.CoreIntegrityVerifier.verify_core_integrity"
    )
    with patch(mock_path):
        yield


class TestAppBaseAgent:
    """Test AppBaseAgent functionality."""

    def test_initialization_defaults(self, mock_core_integrity):
        """Test AppBaseAgent initializes with default values."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent = AppBaseAgent()
        assert agent.domain_root == Path("apps")
        assert agent._app_version == "2.5.0-unified"
        assert agent._namespace == "apps"
        assert agent._similarity_threshold == 0.85
        assert agent._resource_prefix == "app"

    def test_initialization_custom_domain(self, mock_core_integrity):
        """Test AppBaseAgent with custom domain root."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        custom_path = Path("custom_apps")
        agent = AppBaseAgent(domain_root=custom_path)
        assert agent.domain_root == custom_path

    def test_get_resource_key(self, mock_core_integrity):
        """Test get_resource_key generates namespaced keys."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent = AppBaseAgent()

        key = agent.get_resource_key("test_resource")

        assert key == "app:apps:test_resource"

    def test_get_resource_key_custom_prefix(self, mock_core_integrity):
        """Test get_resource_key with custom prefix."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent = AppBaseAgent()
        agent._resource_prefix = "custom"
        agent._namespace = "custom_ns"

        key = agent.get_resource_key("resource")

        assert key == "custom:custom_ns:resource"

    def test_get_app_metadata(self, mock_core_integrity):
        """Test get_app_metadata returns correct metadata."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent = AppBaseAgent()

        metadata = agent.get_app_metadata()

        assert metadata["agent_class"] == "AppBaseAgent"
        assert metadata["domain"] == str(agent.domain_root)
        assert metadata["namespace"] == "apps"
        assert metadata["version"] == "2.5.0-unified"
        assert metadata["similarity_threshold"] == 0.85


class TestAppBaseAgentInheritance:
    """Test AppBaseAgent inheritance from SovereignBaseAgent."""

    def test_inherits_from_sovereign_base(self, mock_core_integrity):
        """Test AppBaseAgent inherits from SovereignBaseAgent."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = AppBaseAgent()

        assert isinstance(agent, SovereignBaseAgent)

    def test_has_class_attributes(self, mock_core_integrity):
        """Test AppBaseAgent has expected class attributes."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent = AppBaseAgent()

        # Check for expected attributes
        assert hasattr(agent, "domain_root")
        assert hasattr(agent, "_app_version")
        assert hasattr(agent, "_namespace")
        assert hasattr(agent, "_resource_prefix")


class TestAppBaseAgentResourceIsolation:
    """Test resource isolation features."""

    def test_different_agents_different_keys(self, mock_core_integrity):
        """Test different agents generate different resource keys."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent1 = AppBaseAgent()
        agent1._resource_prefix = "app1"
        agent1._namespace = "ns1"

        agent2 = AppBaseAgent()
        agent2._resource_prefix = "app2"
        agent2._namespace = "ns2"

        key1 = agent1.get_resource_key("resource")
        key2 = agent2.get_resource_key("resource")

        assert key1 != key2
        assert key1 == "app1:ns1:resource"
        assert key2 == "app2:ns2:resource"

    def test_same_resource_different_namespaces(self, mock_core_integrity):
        """Test same resource name in different namespaces."""
        from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

        agent1 = AppBaseAgent()
        agent1._namespace = "ns1"

        agent2 = AppBaseAgent()
        agent2._namespace = "ns2"

        key1 = agent1.get_resource_key("cache")
        key2 = agent2.get_resource_key("cache")

        assert key1 == "app:ns1:cache"
        assert key2 == "app:ns2:cache"
        assert key1 != key2
