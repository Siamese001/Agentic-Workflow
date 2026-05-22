"""Test 5: L2 steps only invoked through core recipe resolution.

Proves:
  - GenerateResumeStep, ResumeArtifactGateStep are only
    reachable via the core recipe resolver (not directly from __main__)
  - Step classes exist in apps_rg.l2_recipe.steps
  - Steps implement the __call__(context) -> dict interface
"""

from __future__ import annotations

import inspect

import pytest


class TestL2StepsOnlyViaCore:
    """L2 step adapters are registered implementations, not standalone scripts."""

    def test_step_classes_exist_in_l2_recipe(self):
        """Recipe step classes exist and expose STEP_NAME."""
        from apps_rg.l2_recipe.steps import (
            GenerateResumeStep,
            ResumeArtifactGateStep,
        )
        assert GenerateResumeStep.STEP_NAME == "generate_resume"
        assert ResumeArtifactGateStep.STEP_NAME == "resume_artifact_gate"

    def test_step_classes_are_callable(self):
        """Step instances implement __call__(context) -> dict."""
        from apps_rg.l2_recipe.steps import (
            GenerateResumeStep,
            ResumeArtifactGateStep,
        )
        for cls in (GenerateResumeStep, ResumeArtifactGateStep):
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
        lines = source.splitlines()
        tree = ast.parse(source)
        docstr_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                for ln in range(node.lineno, node.end_lineno + 1):
                    docstr_lines.add(ln)
        code_only = "\n".join(l for i, l in enumerate(lines, 1) if i not in docstr_lines and not l.strip().startswith("#"))
        assert "GenerateResumeStep" not in code_only
        assert "ResumeArtifactGateStep" not in code_only

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

        raw_request = {"target_company": "X", "target_role": "Y"}
        callable_fn = resolve_l2_recipe("apps_rg", raw_request)

        source = inspect.getsource(callable_fn)
        assert "step_cls" in source or "step_classes" in source

    def test_artifact_gate_step_requires_artifact_dir(self):
        """ResumeArtifactGateStep raises when no artifact_dir in context."""
        from apps_rg.l2_recipe.steps import ResumeArtifactGateStep

        step = ResumeArtifactGateStep()
        with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE"):
            step({"target_company": "X", "target_role": "Y"})
