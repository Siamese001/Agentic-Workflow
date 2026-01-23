"""
MANDATORY: 100% PASS REQUIRED. Validates Phase 1-3 Execution.

Tests for LIC Sovereign Purity as defined in SOVEREIGN_FOUNDATION_REPORT.md
"""

import pytest
from pathlib import Path

# Get the project root (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.mark.usefixtures("disable_path_shield")
class test_sovereign_purity:
    """MANDATORY: 100% PASS REQUIRED. Validates Phase 1-3 Execution."""

    def test_unknown_count_is_zero(self, disable_path_shield):
        """Verify the 'UNKNOWN' count is zero by checking logic-less files in engines."""
        engine_path = PROJECT_ROOT / "apps_lic" / "engines"
        # Every file remaining in engines must be a stateful LICAgentBase specialist
        for f in engine_path.glob("*.py"):
            if f.name == "__init__.py":
                continue
            content = f.read_text(encoding="utf-8", errors="ignore")
            assert "class" in content, f"Incomplete migration: {f.name}"

    def test_config_eviction(self, disable_path_shield):
        """Confirm passive config has been evicted from the engines folder."""
        old_config = PROJECT_ROOT / "apps_lic" / "engines" / "outreach_orchestration_config.py"
        new_config = (
            PROJECT_ROOT / "apps_lic" / "domain" / "config" / "outreach_orchestration_config.py"
        )
        assert not old_config.exists(), f"Config still in engines: {old_config}"
        assert new_config.exists(), f"Config not in domain/config: {new_config}"

    def test_split_brain_archival(self, disable_path_shield):
        """Confirm redundant agents are quarantined in legacy."""
        redundant = ["CampaignPlannerAgent.py", "ProfileAnalysisAgent.py", "OutreachAgent.py"]
        for agent in redundant:
            assert not (PROJECT_ROOT / "apps_lic" / "engines" / agent).exists(), (
                f"{agent} still in engines"
            )
            assert (PROJECT_ROOT / "apps_lic" / "legacy" / agent).exists(), f"{agent} not in legacy"

    def test_stateless_tool_path(self, disable_path_shield):
        """Verify subject line generator is in the tools namespace."""
        tool_path = PROJECT_ROOT / "apps_lic" / "shared" / "tools" / "generate_subject_line.py"
        assert tool_path.exists(), f"Tool not found: {tool_path}"

    def test_governance_types_eviction(self, disable_path_shield):
        """Verify governance shield types are in domain, not engines."""
        old_types = PROJECT_ROOT / "apps_lic" / "engines" / "governance_shield_types.py"
        new_types = PROJECT_ROOT / "apps_lic" / "domain" / "governance_shield_types.py"
        assert not old_types.exists(), f"Types still in engines: {old_types}"
        assert new_types.exists(), f"Types not in domain: {new_types}"

    def test_governance_agent_in_engines(self, disable_path_shield):
        """Verify GovernanceShieldAgent is properly in engines."""
        agent_path = PROJECT_ROOT / "apps_lic" / "engines" / "GovernanceShieldAgent.py"
        assert agent_path.exists(), f"Agent not found: {agent_path}"
        content = agent_path.read_text()
        assert "class GovernanceShieldAgent" in content, "GovernanceShieldAgent class not found"
        assert "from apps_lic.domain.governance_shield_types import" in content, (
            "Missing domain import"
        )

    def test_stateless_tools_count(self, disable_path_shield):
        """Verify at least 50 stateless tools are in shared/tools."""
        tools_path = PROJECT_ROOT / "apps_lic" / "shared" / "tools"
        py_files = list(tools_path.glob("*.py"))
        # Exclude __init__.py
        tool_count = len([f for f in py_files if f.name != "__init__.py"])
        assert tool_count >= 50, f"Expected 50+ tools, found {tool_count}"

    def test_hop_agents_in_legacy(self, disable_path_shield):
        """Verify hop_agents_LIC.py is in legacy."""
        legacy_hop = PROJECT_ROOT / "apps_lic" / "legacy" / "hop_agents_LIC.py"
        assert legacy_hop.exists(), f"hop_agents_LIC.py not in legacy: {legacy_hop}"

    def test_outreach_validation_executor_in_legacy(self, disable_path_shield):
        """Verify OutreachValidationExecutor.py is in legacy."""
        legacy_executor = PROJECT_ROOT / "apps_lic" / "legacy" / "OutreachValidationExecutor.py"
        assert legacy_executor.exists(), (
            f"OutreachValidationExecutor.py not in legacy: {legacy_executor}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
