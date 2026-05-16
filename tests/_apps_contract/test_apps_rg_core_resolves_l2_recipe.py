"""Test 2: agentic_core resolves L2 recipe for apps_rg from registry.

Proves:
  - resolve_l2_recipe("apps_rg", ...) returns a callable
  - The callable chains GenerateResumeStep → DocxExportStep
  - The resolver imports apps_rg.l2_recipe.registry (core pulls from app)
  - registered_app_names() includes "apps_rg"
"""

from __future__ import annotations

from unittest import mock

import pytest


class TestCoreResolvesL2Recipe:
    """agentic_core must own L2 recipe resolution for apps_rg."""

    def test_resolve_returns_callable(self):
        """resolve_l2_recipe returns a zero-arg callable."""
        from agentic_core.runtime.l2_recipe_resolver import resolve_l2_recipe

        raw_request = {
            "target_company": "TestCo",
            "target_role": "Engineer",
        }
        result = resolve_l2_recipe("apps_rg", raw_request)
        assert callable(result)

    def test_apps_rg_is_registered(self):
        """apps_rg appears in registered_app_names."""
        from agentic_core.runtime.l2_recipe_resolver import registered_app_names

        assert "apps_rg" in registered_app_names()

    def test_is_recipe_registered(self):
        """is_recipe_registered returns True for apps_rg."""
        from agentic_core.runtime.l2_recipe_resolver import is_recipe_registered

        assert is_recipe_registered("apps_rg") is True
        assert is_recipe_registered("nonexistent_app") is False

    def test_resolved_callable_chains_generate_then_docx(self):
        """The composite invokes GenerateResumeStep then DocxExportStep."""
        from agentic_core.runtime.l2_recipe_resolver import resolve_l2_recipe

        raw_request = {
            "target_company": "TestCo",
            "target_role": "Engineer",
        }

        call_log: list[str] = []

        from apps_rg.l2_recipe.steps import (
            DocxExportStep,
            GenerateResumeStep,
        )

        def _mock_generate(self, ctx):
            call_log.append("generate")
            return {
                "step_id": "hop_4_generate_resume",
                "exit_code": 0,
                "generated_resume": {"name": "Test", "headline": "Eng"},
            }

        def _mock_docx(self, ctx):
            call_log.append("docx")
            return {"step_id": "hop_6_docx_export", "exit_code": 0}

        with mock.patch.object(GenerateResumeStep, "__call__", _mock_generate), \
             mock.patch.object(DocxExportStep, "__call__", _mock_docx):
            fn = resolve_l2_recipe("apps_rg", raw_request)
            result = fn()

        assert call_log == ["generate", "docx"]
        assert result["recipe_app_name"] == "apps_rg"
        assert len(result["step_results"]) == 2

    def test_recipe_metadata_exposes_step_classes(self):
        """Recipe metadata lists GenerateResumeStep then DocxExportStep."""
        from apps_rg.l2_recipe.registry import get_apps_rg_recipe_metadata
        from apps_rg.l2_recipe.steps import DocxExportStep, GenerateResumeStep

        meta = get_apps_rg_recipe_metadata()
        assert meta["steps"] == (GenerateResumeStep, DocxExportStep)
        assert meta["dag_id"] == "apps_rg_resume_r4_v1"
