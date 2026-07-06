"""Contract tests for shared InsurTech/EY role-episode X1D rubric (role_episode_x1d_v2)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.role_episode_x1d import (
    DEFAULT_THRESHOLD,
    JUDGE_RUBRIC_REF,
    JUDGE_RUBRIC_VERSION,
    ROLE_EPISODE_RUBRIC,
    run_role_episode_judges,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    NARRATIVE_MAX_CHARS,
    NARRATIVE_MAX_WORDS,
)


def test_rubric_embeds_ssot_narrative_budgets() -> None:
    assert str(NARRATIVE_MAX_WORDS) in ROLE_EPISODE_RUBRIC
    assert str(NARRATIVE_MAX_CHARS) in ROLE_EPISODE_RUBRIC


def test_rubric_enforces_proof_namespace_discipline() -> None:
    rubric = ROLE_EPISODE_RUBRIC.lower()
    assert "bul_insurtech" in ROLE_EPISODE_RUBRIC
    assert "bul_ey" in ROLE_EPISODE_RUBRIC
    assert "jd" in rubric and "proof" in rubric
    assert "decisive failure" in rubric


def test_judge_metadata_constants() -> None:
    assert JUDGE_RUBRIC_VERSION == "role_episode_x1d_v2"
    assert JUDGE_RUBRIC_REF.endswith("#ROLE_EPISODE_RUBRIC")
    assert DEFAULT_THRESHOLD == 0.80


def test_run_role_episode_judges_stamps_section_scoped_metadata() -> None:
    fake_output = JudgeOutput(
        judge_id="placeholder",
        provider_name="anthropic",
        provider_key="anthropic_claude",
        evaluator_mode="MOCKED",
        provider_status="MODEL_BACKED_PASS",
        model_name="mock",
        provider_available=True,
        provider_blocked=False,
        exact_provider_error=None,
        pass_=True,
    )

    with patch(
        "apps_rg.runtime.judges.role_episode_x1d.run_policy_section_judges",
        return_value=[fake_output],
    ) as mock_run:
        outputs = run_role_episode_judges(
            section_id="insurtech_bullets",
            candidate_output={
                "bullets": [{"bullet_text": "Delivered regulated platform outcomes."}],
            },
            claim_ledger=[
                {"claim_text": "Delivered regulated platform outcomes.", "source_fact_ids": ["bul_insurtech_001"]},
            ],
            judge_keys=["anthropic_claude"],
            mode="blocked_if_unavailable",
        )

    mock_run.assert_called_once()
    kwargs = mock_run.call_args.kwargs
    assert kwargs["section_rubric"] == ROLE_EPISODE_RUBRIC
    assert kwargs["rubric_ref"] == JUDGE_RUBRIC_REF
    assert len(outputs) == 1
    assert outputs[0].judge_id == "x1d_anthropic_claude_insurtech_bullets"
    assert outputs[0].rubric_version == JUDGE_RUBRIC_VERSION


@pytest.mark.parametrize(
    "section_id,display_key,display_value",
    [
        ("insurtech_narrative", "narrative_sentence", "Led enterprise data modernization."),
        ("ey_bullets", "resume_display_text", "- Built audit-grade controls."),
    ],
)
def test_run_role_episode_judges_resolves_display_text(
    section_id: str, display_key: str, display_value: str
) -> None:
    fake_output = JudgeOutput(
        judge_id="placeholder",
        provider_name="anthropic",
        provider_key="anthropic_claude",
        evaluator_mode="MOCKED",
        provider_status="MODEL_BACKED_PASS",
        model_name="mock",
        provider_available=True,
        provider_blocked=False,
        exact_provider_error=None,
        pass_=True,
    )

    with patch(
        "apps_rg.runtime.judges.role_episode_x1d.run_policy_section_judges",
        return_value=[fake_output],
    ) as mock_run:
        run_role_episode_judges(
            section_id=section_id,
            candidate_output={display_key: display_value},
            claim_ledger=[],
            judge_keys=["anthropic_claude"],
        )

    assert mock_run.call_args.kwargs["resume_display_text"] == display_value
