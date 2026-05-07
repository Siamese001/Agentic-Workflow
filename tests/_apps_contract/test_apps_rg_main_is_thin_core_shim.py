"""Test 1: apps_rg/__main__.py is a thin core shim with zero domain code.

Proves that __main__.py contains no:
  - _build_l2_callable
  - _run_post_pipeline
  - resolve_l2_callable
  - l2_callable variable
  - StaticDagRegistry
  - generate_resume
  - narrative_pass
  - docx_exporter
  - subprocess.run
  - asyncio.run
"""

from __future__ import annotations

import inspect

import pytest


class TestAppsRgMainIsThinCoreShim:
    """apps_rg/__main__.py must be a pure transport shim."""

    @pytest.fixture(autouse=True)
    def _load_source(self):
        import apps_rg.__main__ as rg_main
        import ast
        import textwrap

        full_source = inspect.getsource(rg_main)
        self.full_source = full_source
        self.module = rg_main

        # Build code-only source (strip docstrings and comments)
        lines = full_source.splitlines()
        tree = ast.parse(full_source)
        docstr_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                for ln in range(node.lineno, node.end_lineno + 1):
                    docstr_lines.add(ln)
        # Strip docstrings, line comments, and inline comments
        def _strip_inline_comment(line: str) -> str:
            if "#" in line:
                return line[:line.index("#")].rstrip()
            return line

        self.source = "\n".join(
            _strip_inline_comment(l) for i, l in enumerate(lines, 1)
            if i not in docstr_lines and not l.strip().startswith("#")
        )

    @pytest.mark.parametrize("forbidden", [
        "_build_l2_callable",
        "_run_post_pipeline",
        "resolve_l2_callable",
        "StaticDagRegistry",
    ])
    def test_no_forbidden_function_or_class(self, forbidden):
        """No forbidden function/class definition or reference in source."""
        assert forbidden not in self.source, (
            f"apps_rg/__main__.py must not contain '{forbidden}'"
        )

    @pytest.mark.parametrize("forbidden_import", [
        "generate_resume",
        "narrative_pass",
        "docx_exporter",
    ])
    def test_no_domain_import(self, forbidden_import):
        """No domain module imported in __main__.py."""
        assert forbidden_import not in self.source, (
            f"apps_rg/__main__.py must not import or reference '{forbidden_import}'"
        )

    def test_no_subprocess_run(self):
        """No subprocess.run call in __main__.py."""
        assert "subprocess.run" not in self.source
        assert "subprocess" not in self.source

    def test_no_asyncio_run(self):
        """No asyncio.run call in __main__.py."""
        assert "asyncio.run" not in self.source
        assert "asyncio" not in self.source

    def test_no_l2_callable_variable(self):
        """No l2_callable variable assignment in executable code."""
        assert "l2_callable" not in self.source

    def test_main_passes_app_name(self):
        """main() passes app_name='apps_rg' to R4 runner."""
        assert 'app_name="apps_rg"' in self.full_source

    def test_no_apps_rg_l2_recipe_import(self):
        """__main__.py must not import apps_rg.l2_recipe in executable code."""
        assert "apps_rg.l2_recipe" not in self.source
        assert "from apps_rg.l2_recipe" not in self.source

    def test_module_has_no_domain_attrs(self):
        """Module object has no domain-execution attributes."""
        assert not hasattr(self.module, "_build_l2_callable")
        assert not hasattr(self.module, "_run_post_pipeline")
        assert not hasattr(self.module, "resolve_l2_callable")

    def test_line_count_under_900(self):
        """__main__.py includes wizard mode — under 900 lines."""
        line_count = len(self.full_source.splitlines())
        assert line_count < 900, (
            f"__main__.py has {line_count} lines — expected <900 for shim + wizard"
        )
