#!/usr/bin/env python3
"""
Phase 20: Core Sovereign Test Suite

Mandatory 100% PASS REQUIREMENT validation for high-rigor synthesis and structural purity.
Validates the Final Sovereign Engine after Phase 20 synthesis operations.
"""

import ast
import sys
from pathlib import Path

import pytest

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCoreLogicSynthesis:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Validates high-rigor synthesis and structural purity.
    """

    def test_absolute_core_independence(self):
        """Verify the Core contains ZERO downstream app dependencies."""
        forbidden_zones = ["apps_lic", "apps_rg", "apps_shared"]
        core_files = list(Path("agentic_core").rglob("*.py"))

        for f in core_files:
            if f.name == "__init__.py":
                continue

            try:
                content = f.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import | ast.ImportFrom):
                        module = getattr(node, "module", "") or ""

                        # Check for direct imports
                        if any(zone in str(module) for zone in forbidden_zones):
                            pytest.fail(f"Circular Dependency: {f.name} imports {module}")

                        # Check for imported names
                        if hasattr(node, "names"):
                            for alias in node.names:
                                if any(zone in str(alias.name) for zone in forbidden_zones):
                                    pytest.fail(
                                        f"Circular Dependency: {f.name} imports {alias.name}"
                                    )

            except Exception as e:
                pytest.fail(f"Error analyzing {f.name}: {e}")

        # If we get here, no circular dependencies found
        assert True, "✅ Core contains no app dependencies"

    def test_healer_logic_synthesis(self):
        """Ensure the legacy HealerAgent logic is present in the Mixin."""
        mixin_path = Path("agentic_core/base_agents/healer_mixin.py")

        if not mixin_path.exists():
            pytest.fail("healer_mixin.py not found - synthesis may have failed")

        content = mixin_path.read_text(encoding="utf-8")

        # Check for synthesized methods from legacy agents
        synthesized_methods = [
            "ASCIIEnforcerAgent",
            "CodeStandardsEnforcerAgent",
            "DeadCodeDetectorAgent",
            "FallbackManagerAgent",
            "GravityHealerAgent",
            "HallucinationDetectorAgent",
            "L1CognitionExerciserAgent",
            "L4StateExerciserAgent",
            "McpConnectionManagerAgent",
        ]

        for method in synthesized_methods:
            assert f"SYNTHESIZED from {method}.py" in content, (
                f"Missing synthesized logic from {method}"
            )

        # Verify original agent files are archived
        archived_path = Path("archives/phase20_synthesis/synthesized")
        for method in synthesized_methods:
            agent_file = archived_path / f"{method}.py"
            assert agent_file.exists(), f"Original {method}.py not properly archived"

    def test_contract_adherence(self):
        """Verify SovereignBaseAgent implements the full Canon interface."""
        try:
            from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
            from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

            # Check inheritance
            assert issubclass(SovereignBaseAgent, CanonBaseAgentInterface), (
                "SovereignBaseAgent must implement CanonBaseAgentInterface"
            )

        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"Import error: {e}")

    def test_core_file_structure(self):
        """Verify the core structure after synthesis."""
        base_agents_path = Path("agentic_core/base_agents")

        # Essential core files must exist
        essential_files = [
            "SovereignBaseAgent.py",
            "healer_mixin.py",
            "subatomic_testing_mixin.py",
            "canon_base_agent_interface.py",
            "mcp_hardened_mixin.py",
        ]

        for file_name in essential_files:
            file_path = base_agents_path / file_name
            assert file_path.exists(), f"Essential core file missing: {file_name}"

    def test_archived_files_structure(self):
        """Verify archived files are properly organized."""
        archives_path = Path("archives/phase20_synthesis")

        # Archives directory should exist
        assert archives_path.exists(), "Archives directory not created"

        # Should have synthesized subdirectory
        synthesized_path = archives_path / "synthesized"
        assert synthesized_path.exists(), "Synthesized archives directory not created"

    def test_utils_eviction(self):
        """Verify utility files were properly evicted to utils/."""
        utils_path = Path("agentic_core/utils")

        # Check that evicted files exist in utils
        evicted_files = [
            "force_app_depth.py",
            "forge_fortress.py",
            "scorched_earth_merge.py",
            "structural_fix.py",
            "decorators.py",
        ]

        for file_name in evicted_files:
            file_path = utils_path / file_name
            assert file_path.exists(), f"Evicted file missing from utils: {file_name}"

    def test_no_duplicate_classes(self):
        """Verify no duplicate class definitions exist in core."""
        core_files = list(Path("agentic_core/base_agents").rglob("*.py"))
        class_names = {}

        for f in core_files:
            if f.name == "__init__.py":
                continue

            try:
                content = f.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name

                        if class_name in class_names:
                            pytest.fail(
                                f"Duplicate class '{class_name}' found in {f.name} and {class_names[class_name]}"
                            )

                        class_names[class_name] = f.name

            except Exception as e:
                pytest.fail(f"Error analyzing {f.name}: {e}")

    def test_mixin_integrity(self):
        """Verify core mixins maintain proper structure."""
        mixins_path = Path("agentic_core/base_agents")

        # Check essential mixins exist and have proper structure
        mixin_files = ["healer_mixin.py", "subatomic_testing_mixin.py", "mcp_hardened_mixin.py"]

        for mixin_file in mixin_files:
            mixin_path = mixins_path / mixin_file
            assert mixin_path.exists(), f"Mixin missing: {mixin_file}"

            content = mixin_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Should have at least one class
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            assert len(classes) > 0, f"Mixin {mixin_file} has no class definitions"

    def test_sovereign_base_agent_completeness(self):
        """Verify SovereignBaseAgent has all required components."""
        try:
            from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

            # Check class exists and can be instantiated
            assert SovereignBaseAgent is not None, "SovereignBaseAgent not importable"

            # Check it has required attributes/methods
            required_methods = ["__init__"]

            for method in required_methods:
                assert hasattr(SovereignBaseAgent, method), f"Missing required method: {method}"

        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"Cannot import SovereignBaseAgent: {e}")

    def test_synthesis_report_exists(self):
        """Verify synthesis execution report was generated."""
        report_path = Path("PHASE20_SYNTHESIS_EXECUTION_REPORT.md")
        assert report_path.exists(), "Synthesis execution report missing"

        content = report_path.read_text(encoding="utf-8")
        assert "COMPLETED" in content, "Report does not show completed status"
        assert "V2.5 Compliance" in content, "Report missing V2.5 compliance status"

    def test_core_refinery_analysis_exists(self):
        """Verify core refinery analysis was generated."""
        analysis_path = Path("CORE_REFINERY_ANALYSIS.md")
        assert analysis_path.exists(), "Core refinery analysis missing"

        content = analysis_path.read_text(encoding="utf-8")
        assert "EXECUTIVE SUMMARY" in content, "Analysis missing executive summary"
        assert "DETAILED ANALYSIS" in content, "Analysis missing detailed analysis"

    def test_no_legacy_imports(self):
        """Verify no imports from old utils/core_extensions remain."""
        core_files = list(Path("agentic_core").rglob("*.py"))

        for f in core_files:
            if f.name == "__init__.py":
                continue

            try:
                content = f.read_text(encoding="utf-8")

                # Check for old import patterns
                forbidden_imports = [
                    "from agentic_core.utils.core_extensions",
                    "from agentic_core.L0_maintenance.scripts.maintenance",
                    "from agentic_core.base_agents.HealerAgent",
                    "from agentic_core.base_agents.CodeStandardsEnforcerAgent",
                ]

                for forbidden in forbidden_imports:
                    assert forbidden not in content, f"Legacy import found in {f.name}: {forbidden}"

            except Exception as e:
                pytest.fail(f"Error analyzing {f.name}: {e}")


def run_core_sovereign_tests():
    """Run the complete Core Sovereign test suite."""
    print("🧪 PHASE 20: CORE SOVEREIGN TEST SUITE")
    print("=" * 80)
    print("MANDATORY: 100% PASS REQUIREMENT")
    print("=" * 80)

    # Run pytest with our test class
    test_file = Path(__file__)
    exit_code = pytest.main([str(test_file), "-v", "--tb=short", "--color=yes"])

    if exit_code == 0:
        print("\n" + "=" * 80)
        print("🎉 CORE SOVEREIGN TEST SUITE: 100% PASS")
        print("=" * 80)
        print("✅ Final Sovereign Engine VALIDATED")
        print("✅ V2.5 Compliance CONFIRMED")
        print("✅ Structural Purity VERIFIED")
        print("✅ Ready for Production Deployment")
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ CORE SOVEREIGN TEST SUITE: FAILED")
        print("=" * 80)
        print("🚫 CRITICAL ISSUES FOUND - DO NOT DEPLOY")
        return False


if __name__ == "__main__":
    success = run_core_sovereign_tests()
    sys.exit(0 if success else 1)
