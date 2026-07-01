"""Single governed spine entry for apps_rg CLI (d8f4a2).

``python -m apps_rg`` and ``python -m apps_rg --section <id>`` both route here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS

_DEFAULT_X1D_JUDGES = ",".join(REQUIRED_JUDGE_PROVIDER_KEYS)
_SECTION_SUCCESS_X3: frozenset[str] = frozenset(
    {"X3C", "X3D", "X3_ALLOW", "EXIT_OK", "EXIT_PARTIAL", "allow"}
)


def _section_cache_preflight_evidence(section_id: str) -> dict[str, Any]:
    """Section scope has no whole-run cache hit path; mark spine entry allowed."""
    return {
        "cache_preflight_completed": True,
        "r1a_preflight_status": "not_applicable_section_scope",
        "r1b_preflight_status": "not_applicable_section_scope",
        "r1b_preflight_reason": "section_scope_uses_core_spine_no_whole_run_cache",
        "r1b_eligibility": "not_applicable",
        "cache_result": "not_applicable",
        "generation_spine_invocation_allowed": True,
        "generation_spine_invocation_blocked_reason": "",
        "route_family": "R4_SINGLE_ACTION",
        "section_id": section_id,
    }


def _section_result_from_l2_result(l2_result: Any) -> dict[str, Any]:
    if not isinstance(l2_result, dict):
        return {}
    for step in l2_result.get("step_results") or ():
        if isinstance(step, dict) and isinstance(step.get("section_result"), dict):
            return dict(step["section_result"])
    return {}


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
    lane_x1d_judges: str = _DEFAULT_X1D_JUDGES,
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
        from apps_rg.runtime.spine.section_cli_runners import SECTION_LANE_RUNNERS

        if sid not in SECTION_LANE_RUNNERS:
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
        from apps_rg.runtime.orchestration.canonical_dispatch import (
            build_raw_request_for_r4,
        )
        from apps_rg.runtime.orchestration.integrated_spine_runner import (
            run_integrated_single_action_spine,
        )
        from apps_rg.runtime.runtime_proof_layout import (
            allocate_full_resume_artifact_dir,
            find_repo_root,
        )

        art = (
            Path(artifact_dir).expanduser().resolve()
            if str(artifact_dir or "").strip()
            else allocate_full_resume_artifact_dir(find_repo_root(), "")
        )
        raw_request = build_raw_request_for_r4(
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
        )
        raw_request.update(
            {
                "execution_scope": "section",
                "section_id": sid,
                "resume_artifact_contract_mode": "section",
                "l2_context": {
                    "section_id": sid,
                    "target_level": target_level,
                    "jd": jd,
                    "job_description_ref": job_description_ref,
                    "job_description_text": job_description_text,
                    "manual_brief": manual_brief,
                    "resume_path": resume_path,
                    "source_resume_text": source_resume_text,
                    "generation_mode": generation_mode or "section_regen",
                    "lane_provider": lane_provider,
                    "lane_provider_resolution_source": lane_provider_resolution_source,
                    "lane_temperature": float(lane_temperature),
                    "lane_x1d_judges": lane_x1d_judges,
                    "lane_mock_judges": lane_mock_judges,
                    "lane_allow_non_allow_exit_zero": lane_allow_non_allow_exit_zero,
                    "lane_allow_test_mock_judges": lane_allow_test_mock_judges,
                },
            }
        )
        result = run_integrated_single_action_spine(
            raw_request=raw_request,
            app_name="apps_rg",
            artifact_dir=art,
            route_family="R4_SINGLE_ACTION",
            cache_preflight_evidence=_section_cache_preflight_evidence(sid),
        )
        section_result = _section_result_from_l2_result(
            getattr(result, "l2_result", None)
        )
        out = dict(section_result)
        if section_result.get("run_id"):
            out["lane_run_id"] = section_result.get("run_id")
        x3 = str(getattr(result, "x3_disposition", "") or "")
        fault = str(getattr(result, "fault", "") or "")
        outcome = not fault and (x3 in _SECTION_SUCCESS_X3 or bool(out.get("outcome_authorized")))
        out.update(
            {
                "exit_status": "success" if outcome else "error",
                "execution_status": "completed" if outcome else "failed",
                "outcome_authorized": outcome,
                "x3_disposition": x3,
                "fault": fault,
                "artifact_dir": str(art),
                "run_id": str(getattr(result, "run_id", "") or ""),
                "request_id": str(getattr(result, "request_id", "") or ""),
                "l7_how_trace_emitted": bool(
                    not fault and (art / "agentic_core_how_trace.json").is_file()
                ),
                "terminal_r5": bool(getattr(result, "terminal_r5", False)),
            }
        )
        return out

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
