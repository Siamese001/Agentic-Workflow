"""Wave 9 judge minimization and compact-packet policy tests."""
from __future__ import annotations

from apps_rg.runtime.judges.grade_only_judge_packet import build_grade_only_judge_packet
from apps_rg.runtime.section_cli_defaults import (
    resolve_cli_x1d_judges,
    resolve_section_default_x1d_judges,
    summarize_section_x1d_minimization_policy,
)


def test_wave9_minimized_defaults_match_lane_x2_requirements(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)

    assert resolve_section_default_x1d_judges("competencies") == "gemini_pro,openai_chatgpt"
    assert resolve_section_default_x1d_judges("unify_bullets") == "gemini_pro"
    assert resolve_section_default_x1d_judges("ibm_bullets") == "gemini_pro"

    # All bullets + all narratives -> single cross-provider judge.
    for section_id in (
        "insurtech_bullets",
        "ey_bullets",
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    ):
        assert resolve_section_default_x1d_judges(section_id) == "gemini_pro"

    # Summaries / headline / aggregate -> dual cross-provider panel.
    dual_panel = "gemini_pro,openai_chatgpt"
    for section_id in ("headline", "executive_summary", "final_aggregate_resume"):
        assert resolve_section_default_x1d_judges(section_id) == dual_panel


def test_wave9_overrides_preserve_diagnostic_full_panel(monkeypatch) -> None:
    cli_panel = "gemini_pro,openai_chatgpt,anthropic_claude"
    env_panel = "gemini_pro,anthropic_claude"

    monkeypatch.setenv("APPS_RG_E2E_X1D_JUDGES", env_panel)
    assert resolve_cli_x1d_judges(None, section_id="ibm_bullets") == "gemini_pro"
    assert resolve_cli_x1d_judges(cli_panel, section_id="ibm_bullets") == "gemini_pro,openai_chatgpt"
    assert resolve_cli_x1d_judges(cli_panel, section_id="competencies") == "gemini_pro,openai_chatgpt"
    assert resolve_cli_x1d_judges("anthropic_claude", section_id="competencies") == "gemini_pro,openai_chatgpt"
    assert resolve_cli_x1d_judges(cli_panel, section_id="executive_summary") == "gemini_pro,openai_chatgpt"
    assert resolve_cli_x1d_judges(cli_panel, section_id="headline") == "gemini_pro,openai_chatgpt"


def test_wave9_policy_summary_is_rare_non_repairing_and_compact(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    summary = summarize_section_x1d_minimization_policy()

    assert summary["competencies"]["judge_required_for_proof"] is True
    assert summary["competencies"]["default_x1d_judges"] == ["gemini_pro", "openai_chatgpt"]
    # Recalibrated: cross-provider single judge for bullets (no anthropic_claude self-judge).
    assert summary["unify_bullets"]["default_x1d_judges"] == ["gemini_pro"]
    assert summary["ibm_bullets"]["default_x1d_judges"] == ["gemini_pro"]
    # No judge roster includes the generator family (anthropic_claude).
    assert all(
        "anthropic_claude" not in row["default_x1d_judges"] for row in summary.values()
    )

    minimized = [
        sid
        for sid, row in summary.items()
        if row["default_judge_count"] == 1
    ]
    # Single-judge lanes: all 4 bullets + all 4 narratives.
    assert set(minimized) == {
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    }
    assert all(row["repair_allowed"] is False for row in summary.values())
    assert all(row["packet_scope"] == "compact_grade_only" for row in summary.values())


def test_grade_only_packet_keeps_judges_compact_and_non_repairing() -> None:
    packet = build_grade_only_judge_packet(
        section_id="headline",
        candidate_output={"headline_line": "SVP Engineering | Platform | AI | Reliability"},
        section_rubric="Score only against the rubric.",
        rubric_ref="tests/wave9/headline",
        targeting_context={"jd_text": "targeting only", "briefing": "targeting only"},
        deterministic_gate_summary={"x2_no_repair": True},
    )

    boundary = packet["proof_boundary"]
    assert boundary["judges_must_not_rewrite"] is True
    assert boundary["jd_is_targeting_context_only"] is True
    assert boundary["briefing_is_targeting_context_only"] is True
    assert packet["judge_task"] == "GRADE_ONLY"
    assert "Do NOT write replacement" in packet["grading_only_instructions"]
    assert packet["deterministic_gate_summary"] == {"x2_no_repair": True}
