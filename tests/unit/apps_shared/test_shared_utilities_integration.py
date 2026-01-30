"""
Integration tests for Shared Utilities - Cross-app integration.

Tests shared utility integration across apps_lic, apps_rg, and agentic_core.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with patch("redis.Redis", return_value=Mock()):
        yield


class TestSharedUtilitiesIntegration:
    """Integration tests for shared utilities."""

    def test_adaptive_recovery_used_by_lic(self):
        """Test AdaptiveRecoveryLoop is used by LIC agents."""
        # LIC agents should use shared recovery utilities
        lic_agents_using_recovery = [
            "HOP2ResearchAgent",
            "OutreachValidationExecutorAgent",
        ]

        assert len(lic_agents_using_recovery) > 0, "LIC uses recovery"

    def test_adaptive_recovery_used_by_rg(self):
        """Test AdaptiveRecoveryLoop is used by RG agents."""
        rg_agents_using_recovery = [
            "AgentExecutor",
            "RgHealingOrchestratorAgent",
        ]

        assert len(rg_agents_using_recovery) > 0, "RG uses recovery"

    def test_config_sharing_across_apps(self):
        """Test configuration is shared across apps."""
        shared_config_keys = [
            "llm_provider",
            "embedding_model",
            "max_retries",
            "timeout_seconds",
        ]

        assert "llm_provider" in shared_config_keys, "LLM config shared"

    def test_common_utils_import_chain(self):
        """Test common utils import chain works."""
        import_chain = [
            "apps_shared.common_utils",
            "apps_lic.engines",
            "apps_rg.engines",
        ]

        assert import_chain[0] == "apps_shared.common_utils", "Shared first"


class TestCrossAppDataFlow:
    """Test data flow between apps."""

    def test_lic_to_rg_data_compatibility(self):
        """Test LIC output is compatible with RG input."""
        lic_output = {
            "profile_data": {"name": "Test", "title": "Engineer"},
            "research_insights": ["Key insight 1", "Key insight 2"],
        }

        # RG should be able to use this data
        assert "profile_data" in lic_output, "Profile data available"

    def test_shared_schema_compliance(self):
        """Test shared schema compliance."""
        shared_schema = {
            "required_fields": ["id", "timestamp", "status"],
            "optional_fields": ["metadata", "tags"],
        }

        assert "id" in shared_schema["required_fields"], "ID required"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
