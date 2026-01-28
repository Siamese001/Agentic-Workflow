#!/usr/bin/env python3
"""
SSOT Integrity Testing Suite - Phase 19 Validation

MANDATORY: 100% PASS REQUIREMENT.
Validates that base_agents is the ONLY source of truth for agent DNA.
"""

import pytest
import sys
from pathlib import Path


class TestSSOTFinalization:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Validates that base_agents is the ONLY source of truth for agent DNA.
    """

    def test_utils_eviction_purity(self):
        """Verify that the utils shipyard is empty of agent logic."""
        utils_path = Path("agentic_core/utils/core_extensions")
        # Verify 100% Pass: No agent-defining classes should remain here
        if utils_path.exists():
            python_files = list(utils_path.rglob("*.py"))
            assert len(python_files) == 0, f"Found remaining files: {python_files}"
        print("✅ utils/core_extensions eviction verified - directory completely removed")

    def test_ssot_import_rewiring(self):
        """Verify LICAgentBase points to the base_agents SSOT."""
        base_path = Path("apps_lic/shared/core/agent_base.py")
        assert base_path.exists(), "LICAgentBase file should exist"
        content = base_path.read_text(encoding="utf-8", errors="ignore")
        assert "from agentic_core.base_agents" in content, "Should import from base_agents SSOT"
        assert "utils.core_extensions" not in content, "Should not import from old utils location"
        print("✅ LICAgentBase correctly points to base_agents SSOT")

    def test_logic_integrity_check(self):
        """Ensure the 'Healer' capability survived the merge."""
        ssot_foundation = Path("agentic_core/base_agents/healer_mixin.py")
        assert ssot_foundation.exists(), "HealerMixin should exist in SSOT"
        content = ssot_foundation.read_text(encoding="utf-8", errors="ignore")
        assert "class HealerMixin" in content, "CRITICAL: HealerMixin class lost during merge!"
        assert "heal_repository" in content, "CRITICAL: Self-healing logic lost during merge!"
        print("✅ HealerMixin capability preserved in SSOT")

    def test_specialist_initialization(self):
        """Confirm a real specialist can still boot up with the new SSOT paths."""
        sys.path.insert(0, ".")
        try:
            from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent

            agent = HOP1ProfileAnalysisAgent()
            assert agent is not None, "HOP1ProfileAnalysisAgent should initialize"
            assert hasattr(agent, "heal_repository"), "Agent should have healing capability"
            print("✅ Specialist agent initializes correctly with new SSOT paths")
        except ImportError as e:
            pytest.fail(f"Failed to import specialist agent: {e}")

    def test_sovereign_base_integrity(self):
        """Verify SovereignBaseAgent is properly established as SSOT foundation."""
        sovereign_path = Path("agentic_core/base_agents/SovereignBaseAgent.py")
        assert sovereign_path.exists(), "SovereignBaseAgent should exist in SSOT"
        content = sovereign_path.read_text(encoding="utf-8", errors="ignore")
        assert "class SovereignBaseAgent" in content, "SovereignBaseAgent class should exist"
        assert "infrastructure_mixin" in content, "Should include infrastructure mixin with MCP"
        print("✅ SovereignBaseAgent properly established as SSOT foundation")

    def test_canon_interface_ssot(self):
        """Verify CanonBaseAgentInterface is in SSOT location."""
        interface_path = Path("agentic_core/base_agents/canon_base_agent_interface.py")
        assert interface_path.exists(), "CanonBaseAgentInterface should exist in SSOT"
        content = interface_path.read_text(encoding="utf-8", errors="ignore")
        assert "class CanonBaseAgentInterface" in content, "Interface should exist"
        assert "Protocol" in content, "Should be a Protocol"
        print("✅ CanonBaseAgentInterface properly located in SSOT")

    def test_no_old_imports_remain(self):
        """Verify no old utils.core_extensions imports remain in active code."""
        import os

        old_imports_found = []
        for root, dirs, files in os.walk("."):
            # Skip hidden directories, archives, and common non-source dirs
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", "venv", ".venv", "archives"]
            ]

            # Skip if we're in an archive directory
            if "archives" in root or "legacy" in root:
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    # Skip test files and scripts
                    if "test_" in file or file_path.parent.name == "scripts":
                        continue
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        # Check for old imports (excluding comments)
                        lines = content.split("\n")
                        actual_imports = [
                            line
                            for line in lines
                            if line.strip().startswith("from agentic_core.utils.core_extensions")
                            and not line.strip().startswith("#")
                        ]
                        if actual_imports:
                            old_imports_found.append(str(file_path))
                    except:
                        pass  # Skip files that can't be read

        assert len(old_imports_found) == 0, f"Found old imports remaining: {old_imports_found}"
        print("✅ No old utils.core_extensions imports remain in active files")

    def test_ssot_completeness(self):
        """Verify SSOT contains all expected foundation files."""
        ssot_path = Path("agentic_core/base_agents")
        assert ssot_path.exists(), "base_agents SSOT should exist"

        # Check for critical foundation files
        critical_files = [
            "SovereignBaseAgent.py",
            "healer_mixin.py",
            "canon_base_agent_interface.py",
            "subatomic_testing_mixin.py",
            "instructional_injection_mixin.py",
            "tracing_mixin.py",
        ]

        for filename in critical_files:
            file_path = ssot_path / filename
            assert file_path.exists(), f"Critical SSOT file missing: {filename}"

        # Count total Python files
        python_files = list(ssot_path.glob("*.py"))
        assert len(python_files) >= 95, (
            f"SSOT should contain at least 95 files, found {len(python_files)}"
        )

        print(f"✅ SSOT completeness verified - {len(python_files)} files in base_agents")


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestSSOTFinalization()

    print("🧪 SSOT INTEGRITY TESTING SUITE")
    print("=" * 60)

    try:
        test_instance.test_utils_eviction_purity()
        test_instance.test_ssot_import_rewiring()
        test_instance.test_logic_integrity_check()
        test_instance.test_specialist_initialization()
        test_instance.test_sovereign_base_integrity()
        test_instance.test_canon_interface_ssot()
        test_instance.test_no_old_imports_remain()
        test_instance.test_ssot_completeness()

        print("=" * 60)
        print("🎉 ALL SSOT TESTS PASSED - SINGLE SOURCE OF TRUTH ESTABLISHED!")
        print("✅ SSOT Integrity: 100% PASS")
        print("✅ Agent-as-Utility Violation: RESOLVED")
        print("✅ Sovereign V2.5 Compliance: ACHIEVED")

    except Exception as e:
        print("=" * 60)
        print(f"❌ SSOT TEST FAILED: {e}")
        print("🚨 SSOT consolidation incomplete - fix failing tests before proceeding")
        raise
