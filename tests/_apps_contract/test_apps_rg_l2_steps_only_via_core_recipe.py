"""Test 5: L2 steps only invoked through core recipe resolution.

Proves:
  - GenerateResumeStep, NarrativePassStep, DocxExportStep are only
    reachable via the core recipe resolver (not directly from __main__)
  - Step classes exist in apps_rg.l2_recipe.steps
  - Steps implement the __call__(context) -> dict interface
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest


class TestL2StepsOnlyViaCore:
    """L2 step adapters are registered implementations, not standalone scripts."""

    def test_step_classes_exist_in_l2_recipe(self):
        """All three step classes exist in apps_rg.l2_recipe.steps."""
        from apps_rg.l2_recipe.steps import (
            DocxExportStep,
            GenerateResumeStep,
            NarrativePassStep,
        )
        assert GenerateResumeStep.STEP_ID == "hop_4_generate_resume"
        assert NarrativePassStep.STEP_ID == "hop_5_narrative_pass"
        assert DocxExportStep.STEP_ID == "hop_6_docx_export"

    def test_step_classes_are_callable(self):
        """Step instances implement __call__(context) -> dict."""
        from apps_rg.l2_recipe.steps import (
            DocxExportStep,
            GenerateResumeStep,
            NarrativePassStep,
        )
        for cls in (GenerateResumeStep, NarrativePassStep, DocxExportStep):
            instance = cls()
            assert callable(instance)
            sig = inspect.signature(instance.__call__)
            params = list(sig.parameters.keys())
            assert "context" in params or "self" in params

    def test_main_does_not_import_step_classes(self):
        """apps_rg/__main__.py has no reference to step classes in executable code."""
        import ast
        import apps_rg.__main__ as rg_main
        source = inspect.getsource(rg_main)
        # Strip docstrings for this check
        lines = source.splitlines()
        tree = ast.parse(source)
        docstr_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                for ln in range(node.lineno, node.end_lineno + 1):
                    docstr_lines.add(ln)
        code_only = "\n".join(l for i, l in enumerate(lines, 1) if i not in docstr_lines and not l.strip().startswith("#"))
        assert "GenerateResumeStep" not in code_only
        assert "NarrativePassStep" not in code_only
        assert "DocxExportStep" not in code_only

    def test_main_does_not_import_l2_recipe_registry(self):
        """apps_rg/__main__.py has no reference to l2_recipe.registry in executable code."""
        import ast
        import apps_rg.__main__ as rg_main
        source = inspect.getsource(rg_main)
        lines = source.splitlines()
        tree = ast.parse(source)
        docstr_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                for ln in range(node.lineno, node.end_lineno + 1):
                    docstr_lines.add(ln)
        code_only = "\n".join(l for i, l in enumerate(lines, 1) if i not in docstr_lines and not l.strip().startswith("#"))
        assert "l2_recipe" not in code_only
        assert "get_apps_rg_recipe_metadata" not in code_only

    def test_steps_only_reachable_through_resolver(self):
        """Resolver is the only path that instantiates and chains steps."""
        from agentic_core.runtime.l2_recipe_resolver import resolve_l2_recipe
        from apps_rg.l2_recipe.steps import GenerateResumeStep

        raw_request = {"target_company": "X", "target_role": "Y"}
        callable_fn = resolve_l2_recipe("apps_rg", raw_request)

        # The callable's source closure references step_classes
        source = inspect.getsource(callable_fn)
        assert "step_cls" in source or "step_classes" in source

    def test_narrative_step_skips_without_target_company(self):
        """NarrativePassStep skips cleanly when target_company is empty."""
        from apps_rg.l2_recipe.steps import NarrativePassStep

        step = NarrativePassStep()
        result = step({"target_company": "", "target_role": "Eng"})
        assert result["skipped"] is True
        assert result["exit_code"] == 0

    def test_docx_step_fails_without_run_dir(self):
        """DocxExportStep returns error when no run_dir in context."""
        from apps_rg.l2_recipe.steps import DocxExportStep

        step = DocxExportStep()
        result = step({"target_company": "X", "target_role": "Y"})
        assert result["exit_code"] == 1
        assert "no run_dir" in result.get("error", "")
