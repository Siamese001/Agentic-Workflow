"""Unit coverage for section spine CLI runners."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.spine.section_cli_runners import run_section_competencies_spine


def test_competencies_spine_uses_generated_raw_request_brief(tmp_path: Path, monkeypatch) -> None:
    generated = tmp_path / "briefing.md"
    generated.write_text("Generated company brief for Acme.", encoding="utf-8")

    captured: dict[str, str] = {}

    def fake_build_raw_request_for_r4(**kwargs):
        return {
            "jd_payload": {"description": "Run the platform team."},
            "manual_brief": str(generated),
            "jd_hash": "jd-hash",
            "brief_hash": "brief-hash",
            "resume_hash": "resume-hash",
        }

    def fake_build_competencies_lane_args(**kwargs):
        captured["briefing"] = str(kwargs.get("briefing") or "")
        captured["jd_text"] = str(kwargs.get("jd_text") or "")
        return SimpleNamespace()

    def fake_run_competencies_lane_execution(args, *, artifact_dir_override=None):
        return {
            "artifact_dir": str(artifact_dir_override or (tmp_path / "run")),
            "runtime_payload": {"run_id": "run-1"},
            "x3": SimpleNamespace(pass_=True, x3_code="X3_ALLOW"),
            "output_text": "COMPETENCIES_STUB",
        }

    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_cli_runners.build_raw_request_for_r4",
        fake_build_raw_request_for_r4,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.competencies_lane.BRIEFING_DEFAULT",
        "STATIC DEFAULT BRIEF",
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.competencies_lane.build_competencies_lane_args",
        fake_build_competencies_lane_args,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.competencies_lane.run_competencies_lane_execution",
        fake_run_competencies_lane_execution,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_cli_runners._lane_dispatch_status_from_x3",
        lambda x3: (True, "success", "X3_ALLOW"),
    )

    result = run_section_competencies_spine(
        target_company="Acme",
        target_role="SVP IT Strategy",
        target_level="",
        jd="",
        job_description_ref="",
        job_description_text="",
        manual_brief="",
        resume_path=str(tmp_path / "resume.json"),
        source_resume_text="",
        generation_mode="strategic_tailor",
        artifact_dir=str(tmp_path / "out"),
        lane_provider="external_openai",
        lane_temperature=0.38,
        lane_x1d_judges="gemini_pro",
        lane_mock_judges=False,
        lane_allow_test_mock_judges=False,
    )

    assert captured["jd_text"] == "Run the platform team."
    assert captured["briefing"].strip() == "Generated company brief for Acme."
    assert result["outcome_authorized"] is True
    assert result["competencies_cli_output_text"] == "COMPETENCIES_STUB"
