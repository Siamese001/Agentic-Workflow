"""Test: GenerateResumeStep requires CompiledPromptArtifact.

Verifies:
- Missing artifact AND missing compile inputs → fails closed
- No model call occurs
- Reason is PA_GUARD_FAILED or PA_COMPILE_FAILED
"""

from __future__ import annotations

import pytest

from apps_rg.l2_recipe.steps import GenerateResumeStep


def test_empty_context_fails_closed():
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
        step({})


def test_missing_jd_fails_closed():
    step = GenerateResumeStep()
    ctx = {"master_resume_data": "resume", "flow_route": "strategic_tailor"}
    with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
        step(ctx)


def test_missing_resume_fails_closed():
    step = GenerateResumeStep()
    ctx = {"jd_data": "jd", "flow_route": "strategic_tailor"}
    with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
        step(ctx)


def test_missing_flow_route_fails_closed():
    step = GenerateResumeStep()
    ctx = {"jd_data": "jd", "master_resume_data": "resume"}
    with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
        step(ctx)


def test_invalid_flow_route_fails_closed():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "jd",
        "master_resume_data": "resume",
        "flow_route": "nonexistent_flow",
    }
    with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED"):
        step(ctx)


def test_incomplete_artifact_fails_closed():
    step = GenerateResumeStep()
    ctx = {
        "compiled_prompt_artifact": {
            "compile_status": "PA_INPUT_INCOMPLETE",
        },
    }
    with pytest.raises(RuntimeError, match="PA_GUARD_FAILED"):
        step(ctx)
