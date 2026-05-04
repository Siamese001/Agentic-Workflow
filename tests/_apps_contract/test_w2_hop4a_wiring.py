"""W2.P2.1 — HOP-4A-HEADLINE wiring contract tests.

Plan: apps-rg-canonical-emit-and-hop4a-wiring-b8e2f4
Phase: W2.P2.1

Verifies that:
  1. HOP-4A-HEADLINE module is importable.
  2. main_canonical() invokes _run_post_pipeline (which runs narrative_pass
     and therefore HOP-4A) when --target-company is supplied.
  3. narrative_pass.py imports and calls generate_headline.

These tests are STRUCTURAL — they do not invoke the LLM. Live verification
happens in W4.P1.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest


class TestHop4AImportable:
    """HOP-4A-HEADLINE module is importable and exposes generate_headline."""

    def test_headline_ensemble_module_imports(self):
        from apps_rg.integrations.hops import headline_ensemble  # noqa: F401

    def test_generate_headline_exported(self):
        from apps_rg.integrations.hops.headline_ensemble import generate_headline
        assert callable(generate_headline)

    def test_generate_headline_accepts_target_role(self):
        """generate_headline must accept target_role kwarg (P6.1 fix)."""
        from apps_rg.integrations.hops.headline_ensemble import generate_headline
        sig = inspect.signature(generate_headline)
        assert "target_role" in sig.parameters


class TestNarrativePassWiresHop4A:
    """narrative_pass.py imports generate_headline and calls it."""

    def test_narrative_pass_imports_generate_headline(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "scripts" / "narrative_pass.py"
        ).read_text(encoding="utf-8")
        assert "from apps_rg.integrations.hops.headline_ensemble import generate_headline" in source

    def test_narrative_pass_calls_generate_headline(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "scripts" / "narrative_pass.py"
        ).read_text(encoding="utf-8")
        # Must invoke generate_headline, not just import it
        assert "generate_headline(" in source


class TestMainDelegatesToCoreRecipe:
    """main() delegates all L2 execution to core-resolved recipe (post shim refactor).

    Legacy main_canonical() and _run_post_pipeline() were removed — all post-pipeline
    steps (narrative pass, docx export) are now L2 step adapters resolved by core.
    """

    def test_main_has_no_post_pipeline(self):
        """__main__.py no longer contains _run_post_pipeline (moved to L2 steps)."""
        source = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "__main__.py"
        ).read_text(encoding="utf-8")
        assert "_run_post_pipeline" not in source, (
            "_run_post_pipeline was removed — post-pipeline steps are L2 step adapters"
        )

    def test_main_has_no_main_canonical(self):
        """__main__.py no longer contains main_canonical (single main() shim)."""
        source = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "__main__.py"
        ).read_text(encoding="utf-8")
        assert "def main_canonical(" not in source, (
            "main_canonical was removed — main() is the sole entrypoint"
        )
