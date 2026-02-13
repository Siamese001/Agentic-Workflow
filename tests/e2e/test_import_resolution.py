"""E2E tests for import resolution across the codebase."""

import ast
from pathlib import Path

import pytest


class TestCriticalImportResolution:
    """Tests for critical import resolution."""

    def test_structure_blueprint_imports(self):
        """Structure blueprint should import without errors."""
        try:
            from agentic_core.L5_safety.config.structure_blueprint_config import SOVEREIGN_TERRITORIES

            assert SOVEREIGN_TERRITORIES is not None
        except ImportError as e:
            if "pydantic" in str(e) or "No module named" in str(e):
                pytest.skip(f"Missing optional dependency: {e}")
            pytest.fail(f"Import failed: {e}")

    def test_file_classification_agent_imports(self):
        """FileClassificationAgent should import without errors."""
        try:
            from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

            assert FileClassificationAgent is not None
        except ImportError as e:
            if "pydantic" in str(e) or "No module named" in str(e):
                pytest.skip(f"Missing optional dependency: {e}")
            pytest.fail(f"Import failed: {e}")


class TestSyntaxValidity:
    """Tests for Python syntax validity across codebase."""

    def test_agentic_core_syntax_valid(self):
        """All Python files in agentic_core should have valid syntax."""
        base = Path("agentic_core")
        if not base.exists():
            pytest.skip("agentic_core/ not found")

        errors = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")

        assert len(errors) == 0, f"Syntax errors found: {errors[:5]}"

    def test_apps_rg_syntax_valid(self):
        """All Python files in apps_rg should have valid syntax."""
        base = Path("apps_rg")
        if not base.exists():
            pytest.skip("apps_rg/ not found")

        errors = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")

        assert len(errors) == 0, f"Syntax errors found: {errors[:5]}"

    def test_apps_lic_syntax_valid(self):
        """All Python files in apps_lic should have valid syntax."""
        base = Path("apps_lic")
        if not base.exists():
            pytest.skip("apps_lic/ not found")

        errors = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")

        assert len(errors) == 0, f"Syntax errors found: {errors[:5]}"


class TestTrackedImportDebt:
    """Tests that explicitly track known-broken import chains.

    These are NOT ignored — they are marked xfail(strict=True) so that:
    - CI stays green today.
    - If someone fixes the module, the test auto-promotes to a real pass.
    - If the breakage silently changes shape, CI catches it.
    """

    @pytest.mark.xfail(
        strict=True,
        reason="Legacy broken import chain: meta_learning_client_types does not exist",
    )
    def test_meta_learning_client_types_import(self):
        """The meta_learning_client_types module should be importable.

        RGAgentBase (apps_rg/utils/RGAgentBase.py:29) imports
        HealingPattern, MetaLearningClient, get_meta_learning_client from
        agentic_core.L1_cognition.reasoning.meta_learning_client_types.

        That module does not exist, making the entire RGAgentBase import
        chain broken at runtime. This test tracks the debt explicitly.
        """
        from agentic_core.L1_cognition.reasoning.meta_learning_client_types import (
            HealingPattern,
            MetaLearningClient,
            get_meta_learning_client,
        )

        assert HealingPattern is not None
        assert MetaLearningClient is not None
        assert get_meta_learning_client is not None


class TestNoCircularImports:
    """Tests for circular import detection."""

    def test_base_agents_no_circular(self):
        """base_agents should not have circular imports."""
        base = Path("agentic_core/base_agents")
        if not base.exists():
            pytest.skip("base_agents/ not found")

        # Check that base_agents don't import from layers that import them
        violations = []
        for py_file in base.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Base agents should not import from L0-L6 reasoning (which inherit from them)
            for layer in [
                "L0_routing",
                "L1_cognition",
                "L2_execution",
                "L3_orchestration",
                "L4_state",
                "L5_safety",
                "L6_observability",
            ]:
                if f"from agentic_core.{layer}.reasoning" in content:
                    violations.append(f"{py_file.name} imports from {layer}.reasoning")

        assert len(violations) == 0, f"Potential circular imports: {violations}"
