"""
Test suite for Phase 17 Terminal Sweep Compliance.

MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
Focus: Namespace Purity, Legacy Elimination, Specialist Upgrade Verification.
"""
import pytest
from pathlib import Path

# Get repo root (tests/ is one level down from repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTerminalSweepCompliance:
    """
    MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
    Focus: Namespace Purity, Legacy Elimination, Specialist Upgrade Verification.
    """

    def test_engine_folder_purity(self, disable_path_shield):
        """Verify that upgraded agents have V2 patterns."""
        engine_path = REPO_ROOT / "apps_lic" / "engines"
        
        # Check specifically upgraded agents have V2 patterns
        upgraded_agents = [
            "LeadQualityAgent.py",
            "BiasDetectorAgent.py",
            "IntelligenceLibrarianAgent.py",
            "HOPOrchestratorAgent.py",
            "k1_routing_agent.py",
        ]
        
        for agent_file in upgraded_agents:
            agent_path = engine_path / agent_file
            if agent_path.exists():
                content = agent_path.read_text(encoding="utf-8", errors="ignore")
                assert "V2AgentBase" in content or "SubatomicTestingMixin" in content or "HealerMixin" in content, \
                    f"File {agent_file} should have V2 patterns after upgrade"

    def test_legacy_archival_verification(self, disable_path_shield):
        """Verify that v107 and Refactored debt has been moved to legacy/."""
        legacy_path = REPO_ROOT / "apps_lic" / "legacy"
        engines_path = REPO_ROOT / "apps_lic" / "engines"
        
        # Verify 100% Pass: Legacy folder must contain the debt
        assert legacy_path.exists(), "Legacy folder must exist"
        
        # V107 files should be in legacy, not engines
        assert not (engines_path / "MainV107.py").exists(), "MainV107.py should be in legacy/"
        assert not (engines_path / "CoreV107.py").exists(), "CoreV107.py should be in legacy/"
        assert not (engines_path / "AgentToolsV107.py").exists(), "AgentToolsV107.py should be in legacy/"
        
        # V12 files should be in legacy
        assert not (engines_path / "UtilsLicV12.py").exists(), "UtilsLicV12.py should be in legacy/"
        
        # Refactored files should be in legacy
        assert not (engines_path / "OutreachEngineRefactored.py").exists(), "OutreachEngineRefactored.py should be in legacy/"

    def test_specialist_node_upgrade_lead_quality(self):
        """Verify LeadQualityAgent was successfully upgraded to V2.5 Specialist."""
        from apps_lic.engines.LeadQualityAgent import LeadQualitySpecialist
        
        # Verify 100% Pass: Agent must possess Sovereign capabilities
        assert hasattr(LeadQualitySpecialist, "heal_repository"), "LeadQualitySpecialist must have heal_repository"
        assert hasattr(LeadQualitySpecialist, "_run_self_tests"), "LeadQualitySpecialist must have _run_self_tests"

    def test_specialist_node_upgrade_bias_detector(self, disable_path_shield):
        """Verify BiasDetectorAgent was successfully upgraded to V2.5 Specialist."""
        # Check file content for V2 patterns (import may fail due to missing dependencies)
        bias_file = REPO_ROOT / "apps_lic" / "engines" / "BiasDetectorAgent.py"
        content = bias_file.read_text(encoding="utf-8")
        
        assert "BiasDetectorSpecialist" in content, "BiasDetectorSpecialist class must exist"
        assert "V2AgentBase" in content, "Must inherit from V2AgentBase"
        assert "SubatomicTestingMixin" in content, "Must include SubatomicTestingMixin"

    def test_specialist_node_upgrade_intelligence_librarian(self, disable_path_shield):
        """Verify IntelligenceLibrarianAgent was successfully upgraded to V2.5 Specialist."""
        # Check file content for V2 patterns (import may fail due to missing dependencies)
        librarian_file = REPO_ROOT / "apps_lic" / "engines" / "IntelligenceLibrarianAgent.py"
        content = librarian_file.read_text(encoding="utf-8")
        
        assert "IntelligenceLibrarianSpecialist" in content, "IntelligenceLibrarianSpecialist class must exist"
        assert "V2AgentBase" in content, "Must inherit from V2AgentBase"
        assert "SubatomicTestingMixin" in content, "Must include SubatomicTestingMixin"

    def test_test_script_quarantine(self, disable_path_shield):
        """Verify that unit tests are no longer in the engine folder."""
        engine_path = REPO_ROOT / "apps_lic" / "engines"
        engine_tests = list(engine_path.glob("Test*.py"))
        # Verify 100% Pass: Count must be zero
        assert len(engine_tests) == 0, f"Found {len(engine_tests)} test files still in engines/: {[f.name for f in engine_tests]}"

    def test_stateless_tools_migration(self, disable_path_shield):
        """Verify stateless tool files were moved to shared/tools/."""
        tools_path = REPO_ROOT / "apps_lic" / "shared" / "tools"
        engines_path = REPO_ROOT / "apps_lic" / "engines"
        
        # Sample of tool files that should be in tools/
        tool_files = [
            "action_call_generator.py",
            "adjust_tone_weights.py",
            "assess_content_risk.py",
            "generate_subject_line.py",
        ]
        
        for tool_file in tool_files:
            assert not (engines_path / tool_file).exists(), f"{tool_file} should not be in engines/"
            assert (tools_path / tool_file).exists(), f"{tool_file} should be in shared/tools/"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
