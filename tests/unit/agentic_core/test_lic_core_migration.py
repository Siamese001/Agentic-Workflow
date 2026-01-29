"""
Test suite for LIC Core Migration.

MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
Verifies that 'LICAgentBase' is now the sovereign standard.
"""

import pytest
from pathlib import Path

# Get repo root (tests/ is one level down from repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent


class TestLICCoreMigration:
    """
    MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
    Verifies that 'LICAgentBase' is now the sovereign standard.
    """

    def test_base_class_rename(self, disable_path_shield):
        """Verify that LICAgentBase is the defined class in the core folder."""
        core_path = REPO_ROOT / "apps_lic" / "shared" / "core" / "agent_base.py"
        content = core_path.read_text(encoding="utf-8")
        # Verify 100% Pass: V2 branding must be purged
        assert "class LICAgentBase" in content, "LICAgentBase class must be defined"
        assert "V2AgentBase" not in content, "V2AgentBase must be renamed to LICAgentBase"

    def test_hop_agent_inheritance(self, disable_path_shield):
        """Verify that HOP-1 through HOP-9 now inherit from LICAgentBase."""
        # Testing HOP-1 as the primary gatekeeper
        hop1_path = REPO_ROOT / "apps_lic" / "engines" / "HOP1ProfileAnalysisAgent.py"
        content = hop1_path.read_text(encoding="utf-8")
        assert "LICAgentBase" in content, "HOP1 must use LICAgentBase"
        assert "from apps_lic.shared.core" in content, "HOP1 must import from apps_lic.shared.core"

    def test_import_integrity_recursive(self, disable_path_shield):
        """Ensure no 'v2_patterns' import strings remain in the apps_lic tree."""
        apps_lic_path = REPO_ROOT / "apps_lic"
        violations = []
        for f in apps_lic_path.rglob("*.py"):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                # Verify 100% Pass: No broken imports to the old path
                if "v2_patterns" in content:
                    violations.append(f.name)
            except Exception:
                pass
        assert len(violations) == 0, f"Files still referencing v2_patterns: {violations}"

    def test_orchestrator_sync(self, disable_path_shield):
        """Verify the Master Orchestrator is synced with the new LICAgentBase."""
        orch_path = REPO_ROOT / "apps_lic" / "engines" / "HOPOrchestratorAgent.py"
        content = orch_path.read_text(encoding="utf-8")
        assert "LICAgentBase" in content, "HOPOrchestratorAgent must use LICAgentBase"

    def test_foundation_directory_removed(self, disable_path_shield):
        """Verify the old 'foundation' directory no longer exists."""
        old_foundation = REPO_ROOT / "apps_lic" / "shared" / "foundation"
        new_core = REPO_ROOT / "apps_lic" / "shared" / "core"
        assert not old_foundation.exists(), "foundation directory should be renamed to core"
        assert new_core.exists(), "core directory must exist"

    def test_all_hop_agents_use_lic_base(self, disable_path_shield):
        """Verify all HOP agents (1-9) use LICAgentBase."""
        engines_path = REPO_ROOT / "apps_lic" / "engines"
        hop_agents = [
            "HOP1ProfileAnalysisAgent.py",
            "HOP2ResearchAgent.py",
            "HOP3SenderGroundingAgent.py",
            "HOP4RoutingAgent.py",
            "HOP5GenerationAgent.py",
            "HOP6ValidationAgent.py",
            "HOP7GateDecisionAgent.py",
            "HOP8QAReportAgent.py",
            "HOP9IntegrationAgent.py",
        ]
        for agent_file in hop_agents:
            agent_path = engines_path / agent_file
            if agent_path.exists():
                content = agent_path.read_text(encoding="utf-8")
                assert "LICAgentBase" in content, f"{agent_file} must use LICAgentBase"

    def test_no_v2_references_in_docstrings(self, disable_path_shield):
        """Verify V2 branding is purged from docstrings."""
        core_path = REPO_ROOT / "apps_lic" / "shared" / "core" / "agent_base.py"
        content = core_path.read_text(encoding="utf-8")
        assert "V2 Agent" not in content, "V2 Agent references should be LIC Agent"
        assert "LIC Sovereign Architecture" in content or "LIC Agent" in content, (
            "Should reference LIC"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
