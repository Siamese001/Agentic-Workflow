from __future__ import annotations

import pytest

from apps_rg.l2_recipe.steps import GenerateSectionStep


def test_generate_section_step_returns_x3_block_without_l2_fault(monkeypatch: pytest.MonkeyPatch) -> None:
    def _blocked_lane(section_id: str, **kwargs: object) -> dict[str, object]:
        del kwargs
        return {
            "section_id": section_id,
            "exit_status": "error",
            "outcome_authorized": False,
            "x3_disposition": "X3_BLOCK",
            "artifact_dir": "artifacts/apps_rg/runtime_proofs/full_resume_lane",
        }

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_cli_runners.run_registered_section_lane",
        _blocked_lane,
    )

    result = GenerateSectionStep()(
        {
            "section_id": "headline",
            "target_company": "Anthropic",
            "target_role": "Manager of Applied AI Architecture, Partnerships",
        }
    )

    assert result["status"] == "blocked"
    assert result["section_blocked"] is True
    assert result["outcome_authorized"] is False
    assert result["x3_disposition"] == "X3_BLOCK"
    assert result["section_result"]["section_id"] == "headline"


def test_generate_section_step_still_raises_pre_x3_fault(monkeypatch: pytest.MonkeyPatch) -> None:
    def _pre_x3_fault(section_id: str, **kwargs: object) -> dict[str, object]:
        del section_id, kwargs
        return {
            "exit_status": "error",
            "outcome_authorized": False,
            "fault": "missing_run_specific_briefing",
        }

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_cli_runners.run_registered_section_lane",
        _pre_x3_fault,
    )

    with pytest.raises(
        RuntimeError,
        match="SECTION_SCOPE_RECIPE_FAILED:headline::missing_run_specific_briefing",
    ):
        GenerateSectionStep()(
            {
                "section_id": "headline",
                "target_company": "Anthropic",
                "target_role": "Manager of Applied AI Architecture, Partnerships",
            }
        )
