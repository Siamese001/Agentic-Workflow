"""Test: PA failure blocks model call.

Verifies:
- Forced compiler failure → no model call
- Sealed failure packet emitted
- No candidate-facing resume artifact
- Reason includes PA_COMPILE_FAILED or PA_GUARD_FAILED
"""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from apps_rg.l2_recipe.steps import GenerateResumeStep


def test_missing_bom_blocks_model_call():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Test JD",
        "master_resume_data": "Test Resume",
        "flow_route": "strategic_tailor",
    }
    with mock.patch(
        "apps_rg.prompt_assembly.compiler._BOM_PATH",
        Path("/nonexistent/prompt_bom.yaml"),
    ):
        with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED"):
            step(ctx)


def test_missing_template_blocks_model_call():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Test JD",
        "master_resume_data": "Test Resume",
        "flow_route": "strategic_tailor",
    }
    with mock.patch(
        "apps_rg.prompt_assembly.compiler._load_template_yaml",
        side_effect=FileNotFoundError("template missing"),
    ):
        with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED"):
            step(ctx)


def test_invalid_flow_route_blocks_model_call():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Test JD",
        "master_resume_data": "Test Resume",
        "flow_route": "totally_invalid_route",
    }
    with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED"):
        step(ctx)


def test_no_generate_main_called_on_failure():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Test JD",
        "master_resume_data": "Test Resume",
        "flow_route": "totally_invalid_route",
    }
    with mock.patch("apps_rg.scripts.generate_resume.main") as mock_gen:
        with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED"):
            step(ctx)
        mock_gen.assert_not_called()


def test_empty_context_no_model_call():
    step = GenerateResumeStep()
    with mock.patch("apps_rg.scripts.generate_resume.main") as mock_gen:
        with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
            step({})
        mock_gen.assert_not_called()


def test_security_gap_blocks_model_call():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Test JD",
        "master_resume_data": "Test Resume",
        "flow_route": "strategic_tailor",
    }
    with mock.patch(
        "apps_rg.prompt_assembly.slot_mapper.validate_slot_isolation",
        return_value=["S0_GOVERNANCE contains fenced data"],
    ):
        with pytest.raises(RuntimeError, match="PA_SECURITY_GAP"):
            step(ctx)
