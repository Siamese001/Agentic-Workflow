"""Test 6: LLM-backed L2 steps fail closed without PA artifact.

Proves:
  - GenerateResumeStep (REQUIRES_PA=True) raises RuntimeError without PA
  - ResumeArtifactGateStep (REQUIRES_PA=False) does NOT require PA
  - ResumeArtifactGateStep (REQUIRES_PA=False) does NOT require PA
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
        """GenerateResumeStep passes PA guard with a compiled artifact."""
        from apps_rg.l2_recipe.steps import GenerateResumeStep
        from apps_rg.prompt_assembly.contracts import PACompileStatus
        from unittest import mock

        step = GenerateResumeStep()
        context = {
            "target_company": "TestCo",
            "target_role": "Engineer",
            "compiled_prompt_artifact": {
                "compile_status": PACompileStatus.PA_L2_HANDOFF_READY.value,
                "artifact_id": "test_123",
                "prompt_id": "apps_rg.resume_generation.strategic_tailor.v1",
                "prompt_hash": "abcd1234abcd1234",
                "prompt_template_hash": "tmpl1234tmpl1234",
                "prompt_bom_hash": "bom12345bom12345",
                "replay_key": "replay_test",
                "policy_hash": "",
                "blueprint_hash": "",
                "provider_lane": "default",
                "source_refs": {},
                "output_schema_ref": "generated_resume.json",
                "output_schema_hash": "",
            },
        }

        with mock.patch("apps_rg.scripts.generate_resume.main", new_callable=mock.AsyncMock):
            with mock.patch("apps_rg.l2_recipe.steps.Path") as mock_path:
                mock_path.return_value.exists.return_value = False
                result = step(context)

        assert result["step_id"] == "hop_4_generate_resume"
        assert result["exit_code"] == 0

    def test_generate_resume_passes_with_governed_context(self):
        """GenerateResumeStep passes PA guard when governed context provided."""
        from apps_rg.l2_recipe.steps import GenerateResumeStep
        from unittest import mock

        step = GenerateResumeStep()
        context = {
            "target_company": "TestCo",
            "target_role": "Engineer",
            "jd_data": "Software Engineer at TestCo",
            "master_resume_data": "Experienced developer resume",
            "flow_route": "strategic_tailor",
        }

        with mock.patch("apps_rg.scripts.generate_resume.main", new_callable=mock.AsyncMock):
            with mock.patch("apps_rg.l2_recipe.steps.Path") as mock_path:
                mock_path.return_value.exists.return_value = False
                result = step(context)

        assert result["exit_code"] == 0
        assert "compiled_prompt_artifact" in result

    def test_artifact_gate_step_does_not_require_pa(self):
        """ResumeArtifactGateStep has REQUIRES_PA=False — no PA check."""
        from apps_rg.l2_recipe.steps import ResumeArtifactGateStep

        step = ResumeArtifactGateStep()
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
            GenerateResumeStep,
            ResumeArtifactGateStep,
        )

        assert GenerateResumeStep.REQUIRES_PA is True
        assert ResumeArtifactGateStep.REQUIRES_PA is False
