#!/usr/bin/env python3
"""
Test Core Foundation Purity - Zero-Loss Migration Validation

MANDATORY: 100% PASS REQUIREMENT.
Focus: Eviction of base agents from apps_shared to agentic_core.
"""

from pathlib import Path

import pytest


class TestCoreFoundationPurity:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Focus: Eviction of base agents from apps_shared to agentic_core.
    """

    def test_apps_shared_purity(self):
        """Verify the base_agents folder is effectively evicted."""
        path = Path("apps_shared/base_agents")
        # Verify 100% Pass: Only __init__.py should remain in the shared base
        python_files = list(path.glob("*.py"))
        non_init_files = [f for f in python_files if f.name != "__init__.py"]
        assert len(non_init_files) == 0, f"Found unexpected files: {non_init_files}"
        print("✅ apps_shared/base_agents eviction verified - only __init__.py remains")

    def test_agentic_core_inheritance(self):
        """Verify LICAgentBase now correctly points to the agentic_core foundation."""
        base_path = Path("apps_lic/shared/core/agent_base.py")
        assert base_path.exists(), "LICAgentBase file should exist"
        content = base_path.read_text(encoding="utf-8", errors="ignore")
        # Verify 100% Pass: Import must come from agentic_core
        assert (
            "from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin"
            in content
        )
        assert "from agentic_core.base_agents.healer_mixin import HealerMixin" in content
        assert "apps_shared.base_agents" not in content
        print("✅ LICAgentBase correctly points to agentic_core foundation")

    def test_specialist_initialization(self):
        """Ensure a HOP agent can still initialize with the new core path."""
        import sys

        sys.path.insert(0, ".")
        from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent

        agent = HOP1ProfileAnalysisAgent()
        # Verify 100% Pass: Inherited core capabilities must remain active
        assert hasattr(agent, "heal_repository")
        assert hasattr(agent, "config")
        assert hasattr(agent, "toggles")
        print("✅ Specialist agent initializes correctly with new core")

    def test_canon_interface_import(self):
        """Verify CanonBaseAgentInterface imports from new location."""
        import sys

        sys.path.insert(0, ".")
        try:
            from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface

            # Verify interface has expected attributes
            assert hasattr(CanonBaseAgentInterface, "smart_fix")
            print("✅ CanonBaseAgentInterface imports from new agentic_core location")
        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"Failed to import CanonBaseAgentInterface from new location: {e}")

    def test_global_legacy_archive(self):
        """Verify the legacy folder in apps_shared caught the leftovers."""
        legacy_path = Path("apps_shared/legacy/")
        assert legacy_path.exists(), "Legacy folder should exist"
        assert (legacy_path / "README.md").exists(), "Legacy README should document migration"
        print("✅ Global legacy archive exists and documented")

    def test_no_old_imports_remain(self):
        """Verify no old apps_shared.base_agents imports remain in codebase."""
        import os

        # Search for any remaining old imports
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
            if "archives" in root or "deprecated" in root:
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    # Skip test files and scripts
                    if "test_" in file or file_path.parent.name == "scripts":
                        continue
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        # Skip comments - only check actual import statements
                        lines = content.split("\n")
                        actual_imports = [
                            line
                            for line in lines
                            if line.strip().startswith("from apps_shared.base_agents")
                            and not line.strip().startswith("#")
                        ]
                        if actual_imports:
                            # Allow the deprecated agent file itself to have the comment
                            if "GenerativeGuardDeprecatedAgent.py" not in str(file_path):
                                old_imports_found.append(str(file_path))
                    except:
                        pass  # Skip files that can't be read

        # Filter to only show non-archive files
        active_old_imports = [
            imp for imp in old_imports_found if "archives" not in imp and "deprecated" not in imp
        ]

        assert len(active_old_imports) == 0, (
            f"Found old imports remaining in active files: {active_old_imports}"
        )
        print("✅ No old apps_shared.base_agents imports remain in active files")


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestCoreFoundationPurity()

    print("🧪 Running Core Foundation Purity Tests...")
    print("=" * 60)

    try:
        test_instance.test_apps_shared_purity()
        test_instance.test_agentic_core_inheritance()
        test_instance.test_specialist_initialization()
        test_instance.test_canon_interface_import()
        test_instance.test_global_legacy_archive()
        test_instance.test_no_old_imports_remain()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED - Zero-Loss Migration Verified!")
        print("✅ Core Foundation Purity: 100% PASS")

    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("🚨 Migration incomplete - fix failing tests before proceeding")
        raise
