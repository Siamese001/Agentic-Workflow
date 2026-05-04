"""Test 6: LLM-backed L2 steps fail closed without PA artifact.

Proves:
  - GenerateResumeStep (REQUIRES_PA=True) raises RuntimeError without PA
  - NarrativePassStep (REQUIRES_PA=False) does NOT require PA
  - DocxExportStep (REQUIRES_PA=False) does NOT require PA
  - PA guard passes when pa_compatible=True or prompt_bom_dir set
"""

from __future__ import annotations

import pytest


class TestLlmStepRequiresPAGuard:
    """LLM-backed steps must have PA-compatible prompt artifacts."""

    def test_generate_resume_fails_without_pa(self):
        """GenerateResumeStep raises RuntimeError without PA artifact."""
        from apps_rg.l2_recipe.steps import GenerateResumeStep

        step = GenerateResumeStep()
        context = {
            "target_company": "TestCo",
            "target_role": "Engineer",
            # No pa_compatible, no prompt_bom_dir, no pa_artifact_ref
        }

        with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
            step(context)

    def test_generate_resume_passes_with_pa_compatible(self):
        """GenerateResumeStep passes PA guard when pa_compatible=True."""
        from apps_rg.l2_recipe.steps import GenerateResumeStep
        from unittest import mock

        step = GenerateResumeStep()
        context = {
            "target_company": "TestCo",
            "target_role": "Engineer",
            "pa_compatible": True,
        }

        # Mock the actual generate_resume.main to avoid running real pipeline
        with mock.patch("apps_rg.scripts.generate_resume.main", new_callable=mock.AsyncMock):
            with mock.patch("pathlib.Path.exists", return_value=False):
                result = step(context)

        assert result["step_id"] == "hop_4_generate_resume"
        assert result["exit_code"] == 0

    def test_generate_resume_passes_with_prompt_bom_dir(self):
        """GenerateResumeStep passes PA guard when prompt_bom_dir set."""
        from apps_rg.l2_recipe.steps import GenerateResumeStep
        from unittest import mock

        step = GenerateResumeStep()
        context = {
            "target_company": "TestCo",
            "target_role": "Engineer",
            "prompt_bom_dir": "/tmp/prompt_boms",
        }

        with mock.patch("apps_rg.scripts.generate_resume.main", new_callable=mock.AsyncMock):
            with mock.patch("pathlib.Path.exists", return_value=False):
                result = step(context)

        assert result["exit_code"] == 0

    def test_narrative_step_does_not_require_pa(self):
        """NarrativePassStep has REQUIRES_PA=False — no PA check."""
        from apps_rg.l2_recipe.steps import NarrativePassStep

        step = NarrativePassStep()
        assert step.REQUIRES_PA is False

        # Should not raise even without PA context
        context = {"target_company": "", "target_role": "Eng"}
        result = step(context)
        assert result["exit_code"] == 0  # skipped due to empty target_company

    def test_docx_step_does_not_require_pa(self):
        """DocxExportStep has REQUIRES_PA=False — no PA check."""
        from apps_rg.l2_recipe.steps import DocxExportStep

        step = DocxExportStep()
        assert step.REQUIRES_PA is False

    def test_pa_guard_error_message_includes_step_name(self):
        """PA guard error message identifies the failing step."""
        from apps_rg.l2_recipe.steps import GenerateResumeStep

        step = GenerateResumeStep()
        context = {"target_company": "X", "target_role": "Y"}

        with pytest.raises(RuntimeError) as exc_info:
            step(context)

        assert "hop_4_generate_resume" in str(exc_info.value)
        assert "PA_GUARD_FAILED" in str(exc_info.value)

    def test_requires_pa_flag_on_step_classes(self):
        """Verify REQUIRES_PA class attribute on all step classes."""
        from apps_rg.l2_recipe.steps import (
            DocxExportStep,
            GenerateResumeStep,
            NarrativePassStep,
        )

        assert GenerateResumeStep.REQUIRES_PA is True
        assert NarrativePassStep.REQUIRES_PA is False
        assert DocxExportStep.REQUIRES_PA is False
