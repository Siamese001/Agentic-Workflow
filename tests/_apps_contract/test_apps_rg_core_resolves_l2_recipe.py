"""Test 2: agentic_core resolves L2 recipe for apps_rg from registry.

Proves:
  - resolve_l2_recipe("apps_rg", ...) returns a callable
  - The callable chains GenerateResumeStep → NarrativePassStep → DocxExportStep
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

    def test_resolved_callable_chains_three_steps(self):
        """The composite callable invokes all three step adapters in order."""
        from agentic_core.runtime.l2_recipe_resolver import resolve_l2_recipe

        raw_request = {
            "target_company": "TestCo",
            "target_role": "Engineer",
        }

        call_log: list[str] = []

        from apps_rg.l2_recipe.steps import (
            DocxExportStep,
            GenerateResumeStep,
            NarrativePassStep,
        )

        def _mock_generate(self, ctx):
            call_log.append("generate")
            return {"step_id": "hop_4_generate_resume", "exit_code": 0, "run_dir": "/tmp/fake"}

        def _mock_narrative(self, ctx):
            call_log.append("narrative")
            return {"step_id": "hop_5_narrative_pass", "exit_code": 0}

        def _mock_docx(self, ctx):
            call_log.append("docx")
            return {"step_id": "hop_6_docx_export", "exit_code": 0}

        with mock.patch.object(GenerateResumeStep, "__call__", _mock_generate), \
             mock.patch.object(NarrativePassStep, "__call__", _mock_narrative), \
             mock.patch.object(DocxExportStep, "__call__", _mock_docx):
            fn = resolve_l2_recipe("apps_rg", raw_request)
            result = fn()

        assert call_log == ["generate", "narrative", "docx"]
        assert result["recipe_app_name"] == "apps_rg"
        assert len(result["step_results"]) == 3

    def test_recipe_metadata_exposes_step_ids(self):
        """Recipe metadata includes correct step IDs."""
        from apps_rg.l2_recipe.registry import get_apps_rg_recipe_metadata

        meta = get_apps_rg_recipe_metadata()
        assert meta["step_ids"] == (
            "hop_4_generate_resume",
            "hop_5_narrative_pass",
            "hop_6_docx_export",
        )
        assert meta["dag_id"] == "apps_rg.resume_generation_v1.static_dag"
