"""Unit tests for shared InsurTech/EY role-episode X1D judge module (e8c1a5d36b)."""

from __future__ import annotations

from pathlib import Path
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


def test_role_episode_rubric_embeds_ssot_narrative_limits() -> None:
    assert str(NARRATIVE_MAX_WORDS) in ROLE_EPISODE_RUBRIC
    assert str(NARRATIVE_MAX_CHARS) in ROLE_EPISODE_RUBRIC
    assert "no more than" in ROLE_EPISODE_RUBRIC.lower()


def test_role_episode_rubric_covers_proof_and_shape_invariants() -> None:
    lowered = ROLE_EPISODE_RUBRIC.lower()
    for marker in (
        "factual_support",
        "claim_ledger_grounding",
        "jd_briefing_targeting_discipline",
        "role_fit_targeting",
        "decisive failure",
        "bul_insurtech_",
        "bul_ey_",
        "exactly 3 bullets",
        "exactly one sentence",
    ):
        assert marker in lowered, f"missing rubric marker: {marker}"


def test_role_episode_rubric_default_threshold_documented() -> None:
    assert str(DEFAULT_THRESHOLD) in ROLE_EPISODE_RUBRIC


@pytest.mark.parametrize(
    ("candidate_output", "expected_display"),
    [
        ({"resume_display_text": "Display wins."}, "Display wins."),
        ({"narrative_sentence": "One narrative sentence."}, "One narrative sentence."),
        (
            {
                "bullets": [
                    {"bullet_text": "First bullet."},
                    {"bullet_text": "Second bullet."},
                ]
            },
            "First bullet.\nSecond bullet.",
        ),
    ],
)
def test_run_role_episode_judges_resume_display_text_precedence(
    candidate_output: dict,
    expected_display: str,
) -> None:
    captured: dict = {}

    def _fake_run_policy_section_judges(
        section_id: str,
        *,
        candidate_output: dict,
        section_rubric: str,
        rubric_ref: str,
        claim_ledger: list,
        judge_keys: list,
        allowed_fact_packet: dict | None = None,
        targeting_context: dict | None = None,
        deterministic_gate_summary: dict | None = None,
        resume_display_text: str = "",
        mode: str = "blocked_if_unavailable",
        artifact_base: Path | None = None,
        judge_packet_path: Path | None = None,
        **kwargs,
    ) -> list[JudgeOutput]:
        captured["section_id"] = section_id
        captured["section_rubric"] = section_rubric
        captured["rubric_ref"] = rubric_ref
        captured["resume_display_text"] = resume_display_text
        captured["judge_packet_path"] = judge_packet_path
        return [
            JudgeOutput(
                judge_id="stub",
                provider_name="stub",
                provider_key="openai_chatgpt",
                evaluator_mode="MOCKED",
                provider_status="MODEL_BACKED_PASS",
                model_name="stub",
                provider_available=True,
                provider_blocked=False,
                exact_provider_error=None,
            )
        ]

    with patch(
        "apps_rg.runtime.judges.role_episode_x1d.run_policy_section_judges",
        side_effect=_fake_run_policy_section_judges,
    ):
        outputs = run_role_episode_judges(
            section_id="insurtech_bullets",
            candidate_output=candidate_output,
            claim_ledger=[],
            judge_keys=["openai_chatgpt"],
            artifact_base=Path("/tmp/role_episode_test"),
        )

    assert captured["resume_display_text"] == expected_display
    assert captured["section_rubric"] == ROLE_EPISODE_RUBRIC
    assert captured["rubric_ref"] == JUDGE_RUBRIC_REF
    assert captured["section_id"] == "insurtech_bullets"
    assert captured["judge_packet_path"] == Path(
        "/tmp/role_episode_test/insurtech_bullets_judge_packet.json"
    )
    assert len(outputs) == 1
    assert outputs[0].judge_id == "x1d_openai_chatgpt_insurtech_bullets"
    assert outputs[0].rubric_version == JUDGE_RUBRIC_VERSION
