"""Single governed spine entry for apps_rg CLI (d8f4a2).

``python -m apps_rg`` and ``python -m apps_rg --section <id>`` both route here.
"""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Literal

from apps_rg.runtime.spine.section_cli_runners import (
    run_section_competencies_spine,
    run_section_executive_summary_spine,
    run_section_headline_spine,
    run_section_ibm_bullets_spine,
    run_section_ibm_narrative_spine,
    run_section_unify_bullets_spine,
    run_section_unify_narrative_spine,
)

_SECTION_RUNNERS: dict[str, Any] = {
    "headline": run_section_headline_spine,
    "executive_summary": run_section_executive_summary_spine,
    "unify_bullets": run_section_unify_bullets_spine,
    "unify_narrative": run_section_unify_narrative_spine,
    "ibm_bullets": run_section_ibm_bullets_spine,
    "ibm_narrative": run_section_ibm_narrative_spine,
    "competencies": run_section_competencies_spine,
}


def run_apps_rg_spine(
    *,
    scope: Literal["section", "full"],
    section_id: str = "",
    target_company: str,
    target_role: str,
    target_level: str = "",
    jd: str = "",
    job_description_ref: str = "",
    job_description_text: str = "",
    manual_brief: str = "",
    resume_path: str = "",
    source_resume_text: str = "",
    generation_mode: str = "strategic_tailor",
    artifact_dir: str = "",
    lane_provider: str = "",
    lane_provider_resolution_source: str | None = None,
    lane_temperature: float = 0.45,
    lane_x1d_judges: str = "gemini_pro,openai_chatgpt,anthropic_claude",
    lane_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Run apps_rg governed spine for section-only or full résumé scope."""
    tc = str(target_company).strip()
    tr = str(target_role).strip()
    if not tc or not tr:
        return {
            "exit_status": "error",
            "execution_status": "failed",
            "outcome_authorized": False,
            "error": "target_company and target_role are required",
            "x3_disposition": "",
            "fault": "missing_targeting_inputs",
            "artifact_dir": "",
            "run_id": "",
            "request_id": "",
            "l7_how_trace_emitted": False,
            "terminal_r5": False,
        }

    if scope == "section":
        sid = str(section_id).strip().lower()
        if not sid:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": "scope=section requires non-empty section_id",
                "x3_disposition": "",
                "fault": "missing_section_id",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }
        runner = _SECTION_RUNNERS.get(sid)
        if runner is None:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": f"unknown section_id: {section_id!r}",
                "x3_disposition": "",
                "fault": "unknown_section",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }
        section_kwargs = {
            "target_company": tc,
            "target_role": tr,
            "target_level": target_level,
            "jd": jd,
            "job_description_ref": job_description_ref,
            "job_description_text": job_description_text,
            "manual_brief": manual_brief,
            "resume_path": resume_path,
            "source_resume_text": source_resume_text,
            "generation_mode": generation_mode,
            "artifact_dir": artifact_dir,
            "lane_provider": lane_provider,
            "lane_provider_resolution_source": lane_provider_resolution_source,
            "lane_temperature": float(lane_temperature),
            "lane_x1d_judges": lane_x1d_judges,
            "lane_mock_judges": lane_mock_judges,
            "lane_allow_non_allow_exit_zero": lane_allow_non_allow_exit_zero,
            "lane_allow_test_mock_judges": lane_allow_test_mock_judges,
        }
        accepted = inspect.signature(runner).parameters
        filtered = {k: v for k, v in section_kwargs.items() if k in accepted}
        return runner(**filtered)

    from apps_rg.runtime.orchestration.canonical_dispatch import (
        run_canonical_full_resume_from_cli_primitives,
    )

    return run_canonical_full_resume_from_cli_primitives(
        target_company=tc,
        target_role=tr,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
        artifact_dir=artifact_dir,
        section=section_id,
        lane_provider=lane_provider,
        lane_temperature=lane_temperature,
        lane_x1d_judges=lane_x1d_judges,
        lane_mock_judges=lane_mock_judges,
        lane_allow_test_mock_judges=lane_allow_test_mock_judges,
    )


__all__ = ["run_apps_rg_spine"]
