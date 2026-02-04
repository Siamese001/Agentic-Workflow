"""
Phase 1 MRO Refactoring Tests (AST-Based Static Analysis)
==========================================================
Validates the removal of redundant mixin inheritance and proper base class usage.

Uses AST-based static analysis to avoid import errors from missing dependencies.

Tests verify:
1. Agents no longer have redundant SubatomicTestingMixin inheritance
2. DispatchResumeToolsAgent properly inherits from SovereignBaseAgent
3. Class declarations match expected patterns
"""

import ast
import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Mark all tests as guardian tests
pytestmark = pytest.mark.guardian


def get_class_bases_from_ast(file_path: Path, class_name: str) -> list[str]:
    """Extract class bases from AST without importing the module."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)
                return bases
    except Exception:
        pass
    return []


def get_imports_from_ast(file_path: Path) -> list[str]:
    """Extract all import names from AST."""
    imports = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                for alias in node.names:
                    imports.append(alias.name)
    except Exception:
        pass
    return imports


class TestPhase1RedundantMixinRemovalAST:
    """Test that redundant SubatomicTestingMixin inheritance was removed using AST."""

    def test_hop2_research_agent_no_redundant_mixin(self):
        """HOP2ResearchAgent should not directly inherit SubatomicTestingMixin."""
        file_path = PROJECT_ROOT / "apps_lic" / "engines" / "Hop2researchagentStrategy.py"
        assert file_path.exists(), f"File not found: {file_path}"

        bases = get_class_bases_from_ast(file_path, "HOP2ResearchAgent")
        assert "SubatomicTestingMixin" not in bases, (
            f"HOP2ResearchAgent should not directly inherit SubatomicTestingMixin. "
            f"Current bases: {bases}"
        )
        assert "LICAgentBase" in bases, (
            f"HOP2ResearchAgent should inherit from LICAgentBase. Current bases: {bases}"
        )

    def test_pii_sanitizer_agent_no_redundant_mixin(self):
        """PII_SanitizerSpecialistAgent should not directly inherit SubatomicTestingMixin."""
        file_path = PROJECT_ROOT / "apps_lic" / "engines" / "PIISanitizerSpecialistAgent.py"
        assert file_path.exists(), f"File not found: {file_path}"

        bases = get_class_bases_from_ast(file_path, "PII_SanitizerSpecialistAgent")
        assert "SubatomicTestingMixin" not in bases, (
            f"PII_SanitizerSpecialistAgent should not directly inherit SubatomicTestingMixin. "
            f"Current bases: {bases}"
        )
        assert "LICAgentBase" in bases, (
            f"PII_SanitizerSpecialistAgent should inherit from LICAgentBase. Current bases: {bases}"
        )

    def test_location_validator_agent_no_redundant_mixin(self):
        """LocationValidatorAgent should not directly inherit SubatomicTestingMixin."""
        file_path = (
            PROJECT_ROOT
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "location_validator_agent.py"
        )
        assert file_path.exists(), f"File not found: {file_path}"

        bases = get_class_bases_from_ast(file_path, "LocationValidatorAgent")
        assert "SubatomicTestingMixin" not in bases, (
            f"LocationValidatorAgent should not directly inherit SubatomicTestingMixin. "
            f"Current bases: {bases}"
        )
        assert "SovereignBaseAgent" in bases, (
            f"LocationValidatorAgent should inherit from SovereignBaseAgent. Current bases: {bases}"
        )

    def test_hierarchy_agent_no_redundant_mixin(self):
        """HierarchyAgent should not directly inherit SubatomicTestingMixin."""
        file_path = (
            PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "HierarchyagentStrategy.py"
        )
        assert file_path.exists(), f"File not found: {file_path}"

        bases = get_class_bases_from_ast(file_path, "HierarchyAgent")
        assert "SubatomicTestingMixin" not in bases, (
            f"HierarchyAgent should not directly inherit SubatomicTestingMixin. "
            f"Current bases: {bases}"
        )
        assert "SovereignBaseAgent" in bases, (
            f"HierarchyAgent should inherit from SovereignBaseAgent. Current bases: {bases}"
        )

    def test_no_subatomic_import_in_hierarchy_agent(self):
        """HierarchyAgent file should not import SubatomicTestingMixin."""
        file_path = (
            PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "HierarchyagentStrategy.py"
        )
        assert file_path.exists(), f"File not found: {file_path}"

        imports = get_imports_from_ast(file_path)
        assert "SubatomicTestingMixin" not in imports, (
            f"HierarchyAgent should not import SubatomicTestingMixin. Imports: {imports}"
        )

    def test_no_subatomic_import_in_location_validator(self):
        """LocationValidatorAgent file should not import SubatomicTestingMixin."""
        file_path = (
            PROJECT_ROOT
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "location_validator_agent.py"
        )
        assert file_path.exists(), f"File not found: {file_path}"

        imports = get_imports_from_ast(file_path)
        assert "SubatomicTestingMixin" not in imports, (
            f"LocationValidatorAgent should not import SubatomicTestingMixin. Imports: {imports}"
        )


class TestPhase1DispatchResumeToolsAgentAST:
    """Test DispatchResumeToolsAgent now inherits from SovereignBaseAgent using AST."""

    def test_inherits_from_sovereign_base(self):
        """DispatchResumeToolsAgent should inherit from SovereignBaseAgent."""
        file_path = PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py"
        assert file_path.exists(), f"File not found: {file_path}"

        bases = get_class_bases_from_ast(file_path, "DispatchResumeToolsAgent")
        assert "SovereignBaseAgent" in bases, (
            f"DispatchResumeToolsAgent should inherit from SovereignBaseAgent. "
            f"Current bases: {bases}"
        )

    def test_not_inherits_from_raw_mixins(self):
        """DispatchResumeToolsAgent should not directly inherit from
        HealerMixin or MCPHardenedMixin."""
        file_path = PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py"
        assert file_path.exists(), f"File not found: {file_path}"

        bases = get_class_bases_from_ast(file_path, "DispatchResumeToolsAgent")
        assert "HealerMixin" not in bases, (
            f"DispatchResumeToolsAgent should not directly inherit HealerMixin. "
            f"Current bases: {bases}"
        )
        assert "MCPHardenedMixin" not in bases, (
            f"DispatchResumeToolsAgent should not directly inherit MCPHardenedMixin. "
            f"Current bases: {bases}"
        )

    def test_imports_sovereign_base_agent(self):
        """DispatchResumeToolsAgent file should import SovereignBaseAgent."""
        file_path = PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py"
        assert file_path.exists(), f"File not found: {file_path}"

        imports = get_imports_from_ast(file_path)
        assert "SovereignBaseAgent" in imports, (
            f"DispatchResumeToolsAgent should import SovereignBaseAgent. Imports: {imports}"
        )

    def test_has_dataclass_decorator(self):
        """DispatchResumeToolsAgent should be a dataclass."""
        file_path = PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py"
        assert file_path.exists(), f"File not found: {file_path}"

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DispatchResumeToolsAgent":
                decorator_names = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorator_names.append(dec.id)
                assert "dataclass" in decorator_names, (
                    f"DispatchResumeToolsAgent should have @dataclass decorator. "
                    f"Decorators: {decorator_names}"
                )
                return

        pytest.fail("DispatchResumeToolsAgent class not found")

    def test_has_post_init_method(self):
        """DispatchResumeToolsAgent should have __post_init__ method."""
        file_path = PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py"
        assert file_path.exists(), f"File not found: {file_path}"

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DispatchResumeToolsAgent":
                method_names = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                assert "__post_init__" in method_names, (
                    f"DispatchResumeToolsAgent should have __post_init__ method. "
                    f"Methods: {method_names}"
                )
                return

        pytest.fail("DispatchResumeToolsAgent class not found")


class TestPhase1CodeQuality:
    """Test code quality aspects of the refactoring."""

    def test_all_refactored_files_are_valid_python(self):
        """All refactored files should be valid Python syntax."""
        files_to_check = [
            PROJECT_ROOT / "apps_lic" / "engines" / "Hop2researchagentStrategy.py",
            PROJECT_ROOT / "apps_lic" / "engines" / "PIISanitizerSpecialistAgent.py",
            PROJECT_ROOT
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "location_validator_agent.py",
            PROJECT_ROOT
            / "agentic_core"
            / "L5_safety"
            / "validators"
            / "HierarchyagentStrategy.py",
            PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py",
        ]

        for file_path in files_to_check:
            assert file_path.exists(), f"File not found: {file_path}"
            content = file_path.read_text(encoding="utf-8")
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {file_path}: {e}")

    def test_refactored_agents_have_single_base_or_sovereign(self):
        """Refactored agents should have clean inheritance (single base or SovereignBaseAgent)."""
        agents_to_check = [
            (
                PROJECT_ROOT / "apps_lic" / "engines" / "Hop2researchagentStrategy.py",
                "HOP2ResearchAgent",
            ),
            (
                PROJECT_ROOT / "apps_lic" / "engines" / "PIISanitizerSpecialistAgent.py",
                "PII_SanitizerSpecialistAgent",
            ),
            (
                PROJECT_ROOT
                / "agentic_core"
                / "L5_safety"
                / "validators"
                / "location_validator_agent.py",
                "LocationValidatorAgent",
            ),
            (
                PROJECT_ROOT
                / "agentic_core"
                / "L5_safety"
                / "validators"
                / "HierarchyagentStrategy.py",
                "HierarchyAgent",
            ),
            (
                PROJECT_ROOT / "apps_rg" / "shared" / "tools" / "dispatch_resume_tools_agent.py",
                "DispatchResumeToolsAgent",
            ),
        ]

        for file_path, class_name in agents_to_check:
            bases = get_class_bases_from_ast(file_path, class_name)
            # Should have exactly 1 base class (clean inheritance)
            assert len(bases) == 1, (
                f"{class_name} should have exactly 1 base class after refactoring. "
                f"Current bases: {bases}"
            )
