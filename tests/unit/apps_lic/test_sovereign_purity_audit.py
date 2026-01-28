"""
Test suite for Sovereign Purity Audit.

MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
Focus: Namespace isolation, Foundation renaming, Unknown elimination.
"""
import pytest
from pathlib import Path

# Get repo root (tests/ is one level down from repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent


class test_sovereign_purity_audit:
    """
    MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
    Focus: Namespace isolation, Foundation renaming, Unknown elimination.
    """

    def test_foundation_directory_rename(self, disable_path_shield):
        """Verify the legacy 'core' is now 'foundation'."""
        old = REPO_ROOT / "apps_lic" / "shared" / "core"
        new = REPO_ROOT / "apps_lic" / "shared" / "foundation"
        # Verify 100% Pass: The core DNA must be in 'foundation'
        assert not old.exists(), "core should no longer exist"
        assert new.exists(), "foundation directory must exist"

    def test_engine_folder_specialist_purity(self, disable_path_shield):
        """Verify only Sovereign Specialists remain in the engines/ directory."""
        engine_path = REPO_ROOT / "apps_lic" / "engines"
        # Verify 100% Pass: Stateless tools must have been moved
        assert not (engine_path / "generate_subject_line.py").exists(), "Stateless tools should be in shared/tools/"
        assert not (engine_path / "aggregate_campaign_state.py").exists(), "Stateless tools should be in shared/tools/"
        assert not (engine_path / "tools_lic.py").exists(), "Stateless tools should be in shared/tools/"

    def test_nomenclature_debt_purge(self, disable_path_shield):
        """Verify that passive Enums are no longer labeled as 'Agents'."""
        domain_path = REPO_ROOT / "apps_lic" / "domain"
        engines_path = REPO_ROOT / "apps_lic" / "engines"
        
        # FailureClassifierAgent renamed to failure_types
        assert not (domain_path / "FailureClassifierAgent.py").exists(), "FailureClassifierAgent should be renamed"
        assert (domain_path / "failure_types.py").exists(), "failure_types.py must exist"
        
        # governance_shield_agent renamed to governance_shield_types
        assert not (engines_path / "governance_shield_agent.py").exists(), "governance_shield_agent should be renamed"
        assert (engines_path / "governance_shield_types.py").exists(), "governance_shield_types.py must exist"

    def test_report_completeness(self, disable_path_shield):
        """Verify the generated report addresses the 97 unknowns."""
        report = REPO_ROOT / "SOVEREIGN_FOUNDATION_REPORT.md"
        assert report.exists(), "SOVEREIGN_FOUNDATION_REPORT.md must exist"
        content = report.read_text(encoding="utf-8")
        assert "97" in content, "Report must reference the 97 unknown files"
        assert "UNKNOWN" in content, "Report must contain UNKNOWN classification"

    def test_tools_directory_populated(self, disable_path_shield):
        """Verify stateless tools were moved to shared/tools/."""
        tools_path = REPO_ROOT / "apps_lic" / "shared" / "tools"
        assert tools_path.exists(), "shared/tools/ must exist"
        
        # Check for moved tools
        expected_tools = [
            "generate_subject_line.py",
            "action_call_generator.py",
            "tools_lic.py",
            "aggregate_campaign_state.py",
        ]
        for tool in expected_tools:
            assert (tools_path / tool).exists(), f"{tool} should be in shared/tools/"

    def test_domain_directory_populated(self, disable_path_shield):
        """Verify support structures were moved to domain/."""
        domain_path = REPO_ROOT / "apps_lic" / "domain"
        
        # Check for moved support structures
        expected_files = [
            "lic_archetypes.py",
            "lic_cta_patterns.py",
            "lic_routing_rules.py",
            "models.py",
        ]
        for f in expected_files:
            assert (domain_path / f).exists(), f"{f} should be in domain/"

    def test_legacy_directory_populated(self, disable_path_shield):
        """Verify legacy files were archived."""
        legacy_path = REPO_ROOT / "apps_lic" / "legacy"
        assert legacy_path.exists(), "legacy/ must exist"
        
        # Check for archived files
        expected_legacy = [
            "MainV107.py",
            "core_v107.py",
            "utils_lic_v12.py",
            "OutreachEngineRefactored.py",
        ]
        for f in expected_legacy:
            assert (legacy_path / f).exists(), f"{f} should be in legacy/"

    def test_foundation_core_components(self, disable_path_shield):
        """Verify foundation contains core V2 components."""
        foundation_path = REPO_ROOT / "apps_lic" / "shared" / "foundation"
        
        expected_components = [
            "agent_base.py",
            "immutable_buffer.py",
            "mixins.py",
            "trace_registry.py",
        ]
        for component in expected_components:
            assert (foundation_path / component).exists(), f"{component} should be in foundation/"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
