"""Section spine CLI runners — invoked only via apps_rg_spine_run (d8f4a2)."""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.orchestration.canonical_dispatch import (
    build_raw_request_for_r4,
    _effective_lane_provider,
    _read_optional_brief,
    _resolve_lane_manual_brief,
)
from apps_rg.runtime.section_cli_defaults import default_lane_provider_for_section
from apps_rg.runtime.spine.section_x3_finalize import (
    lane_outcome_authorized_from_x3,
    lane_x3_code_from_x3,
)


def _lane_dispatch_status_from_x3(x3: Any) -> tuple[bool, str, str]:
    """Map lane ctx x3 (dict or dataclass) to CLI dispatch exit fields."""
    authorized = lane_outcome_authorized_from_x3(x3)
    exit_status = "success" if authorized else "error"
    return authorized, exit_status, lane_x3_code_from_x3(x3)

def run_section_competencies_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Section-only competencies lane — mirrors executive_summary CLI wiring."""
    from apps_rg.runtime.sections import competencies_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = (
        str(jp.get("description") or jp.get("title") or "").strip()
    )
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    resolved_manual_brief = str(raw_request.get("manual_brief") or manual_brief or "").strip()
    briefing = _read_optional_brief(resolved_manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    lane_provider_eff = str(lane_provider or "").strip() or default_lane_provider_for_section("competencies")

    args = lane.build_competencies_lane_args(
        provider=lane_provider_eff,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        target_role=str(target_role).strip() or None,
        base_resume_ref=str(resume_path or ""),
    )

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_competencies_lane_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])
    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
        "competencies_cli_output_text": str(ctx.get("output_text") or ""),
    }


def run_section_headline_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_test_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
) -> dict[str, Any]:
    """Section-only headline lane via ``apps_rg.runtime.sections.headline_lane``."""
    from apps_rg.runtime.sections import headline_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    resolved_manual_brief = str(raw_request.get("manual_brief") or manual_brief or "").strip()
    briefing = _read_optional_brief(resolved_manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    eff_prov = _effective_lane_provider(lane_provider)
    args = lane.build_headline_lane_args(
        provider=eff_prov,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        allow_non_allow_exit_zero=bool(lane_allow_non_allow_exit_zero),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        base_resume_ref=str(resume_path or ""),
    )

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_headline_lane_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])
    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": str(ctx.get("output_text") or ""),
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
        "competencies_cli_output_text": "",
    }


def run_section_executive_summary_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_provider_resolution_source: str | None,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_test_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
) -> dict[str, Any]:
    """Section-only run: same artifacts as legacy dispatch; does not invoke ``dispatch_apps_rg_run``."""
    from apps_rg.runtime.sections import executive_summary_lane as lane

    tc = str(target_company).strip()
    tr = str(target_role).strip()
    if not tc or not tr:
        return {
            "exit_status": "error",
            "execution_status": "failed",
            "outcome_authorized": False,
            "error": "executive_summary requires --target-company and --target-role",
            "x3_disposition": "",
            "fault": "missing_targeting_inputs",
            "artifact_dir": "",
            "run_id": "",
            "request_id": "",
            "l7_how_trace_emitted": False,
            "terminal_r5": False,
        }

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
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    briefing = _resolve_lane_manual_brief(manual_brief)
    if not str(briefing).strip():
        return {
            "exit_status": "error",
            "execution_status": "failed",
            "outcome_authorized": False,
            "error": (
                "executive_summary requires run-specific briefing material "
                "(--manual-brief path/URI or inline text)"
            ),
            "x3_disposition": "",
            "fault": "missing_targeting_inputs",
            "artifact_dir": "",
            "run_id": "",
            "request_id": "",
            "l7_how_trace_emitted": False,
            "terminal_r5": False,
        }

    import os

    from apps_rg.runtime.targeting_input_freshness import (
        is_stale_default_targeting_briefing,
        is_stale_default_targeting_jd,
    )

    allow_stale = os.environ.get("APPS_RG_ALLOW_STALE_TARGETING_SSOT", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }
    stale_parts: list[str] = []
    if not allow_stale:
        if is_stale_default_targeting_jd(jd_text):
            stale_parts.append("JD")
        if is_stale_default_targeting_briefing(briefing):
            stale_parts.append("briefing")
    if stale_parts:
        return {
            "exit_status": "error",
            "execution_status": "failed",
            "outcome_authorized": False,
            "error": (
                "executive_summary targeting inputs are not updated (still DEFAULT_SSOT placeholder): "
                + ", ".join(stale_parts)
                + ". Edit apps_rg/config/default_* files is not sufficient — pass run-specific "
                "--jd and --manual-brief material."
            ),
            "x3_disposition": "",
            "fault": "stale_targeting_inputs",
            "artifact_dir": "",
            "run_id": "",
            "request_id": "",
            "l7_how_trace_emitted": False,
            "terminal_r5": False,
        }

    eff_prov = _effective_lane_provider(lane_provider)
    from apps_rg.runtime.section_cli_defaults import coalesce_lane_provider_resolution_source

    prov_src = coalesce_lane_provider_resolution_source(
        explicit=lane_provider_resolution_source,
        resolved_provider=eff_prov,
    )
    args = SimpleNamespace(
        provider=eff_prov,
        provider_resolution_source=prov_src,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        allow_non_allow_exit_zero=bool(lane_allow_non_allow_exit_zero),
        target_title=tr,
        target_company=tc,
        jd_text=jd_text,
        briefing=briefing,
        target_role=tr,
        base_resume_ref=str(resume_path or ""),
    )
    if eff_prov == "external_claude":
        lo, hi = lane.EXEC_SUMMARY_TEMP_RANGE
        if args.temperature < lo or args.temperature > hi:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": (
                    f"temperature {args.temperature} outside executive_summary profile ({lo}-{hi})"
                ),
                "x3_disposition": "",
                "fault": "temperature_range",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_executive_summary_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])
    from apps_rg.runtime.embedding_settings import (
        resolve_apps_rg_embedding_settings,
        write_embedding_settings_receipt,
    )

    _emb_settings = resolve_apps_rg_embedding_settings(route_section="executive_summary")
    write_embedding_settings_receipt(artifact_path, _emb_settings)
    os.environ["APPS_RG_ARTIFACT_DIR"] = str(artifact_path)

    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": ctx.get("output_text", ""),
        "token_budget_operator_message": str(ctx.get("token_budget_operator_message") or ""),
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
    }


def run_section_unify_bullets_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_non_allow_exit_zero: bool = False,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Section-only unify_bullets lane; legacy ``python -m`` dispatch entry is never imported here."""
    from apps_rg.runtime.sections import unify_bullets_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    lane_provider_eff = str(lane_provider or "").strip() or default_lane_provider_for_section(
        "unify_narrative"
    )

    args = SimpleNamespace(
        provider=lane_provider_eff,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        allow_non_allow_exit_zero=bool(lane_allow_non_allow_exit_zero),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        base_resume_ref=str(resume_path or ""),
    )
    if lane_provider_eff == "external_claude":
        lo, hi = lane.UNIFY_TEMP_RANGE
        if args.temperature < lo or args.temperature > hi:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": (
                    f"temperature {args.temperature} outside unify_bullets profile ({lo}-{hi})"
                ),
                "x3_disposition": "",
                "fault": "temperature_range",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_unify_bullets_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": ctx.get("output_text", ""),
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
    }


def run_section_unify_narrative_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Section-only unify_narrative lane; legacy ``python -m`` dispatch entry is not used."""
    from apps_rg.runtime.sections import unify_narrative_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    lane_provider_eff = str(lane_provider or "").strip() or default_lane_provider_for_section(
        "ibm_narrative"
    )

    args = SimpleNamespace(
        provider=lane_provider_eff,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        base_resume_ref=str(resume_path or ""),
    )
    if lane_provider_eff == "external_claude":
        lo, hi = lane.NARRATIVE_TEMP_RANGE
        if args.temperature < lo or args.temperature > hi:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": (
                    f"temperature {args.temperature} outside unify_narrative profile ({lo}-{hi})"
                ),
                "x3_disposition": "",
                "fault": "temperature_range",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_unify_narrative_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": ctx.get("output_text", ""),
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
    }


def run_section_ibm_bullets_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_non_allow_exit_zero: bool = False,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Section-only ibm_bullets lane via ``ibm_bullets_lane`` (legacy CLI wrapper not invoked)."""
    from apps_rg.runtime.sections import ibm_bullets_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    lane_provider_eff = _effective_lane_provider(lane_provider)

    args = SimpleNamespace(
        provider=lane_provider_eff,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        allow_non_allow_exit_zero=bool(lane_allow_non_allow_exit_zero),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        base_resume_ref=str(resume_path or ""),
    )
    if lane_provider_eff == "external_claude":
        lo, hi = lane.IBM_TEMP_RANGE
        if args.temperature < lo or args.temperature > hi:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": (
                    f"temperature {args.temperature} outside ibm_bullets profile ({lo}-{hi})"
                ),
                "x3_disposition": "",
                "fault": "temperature_range",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_ibm_bullets_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": ctx.get("output_text", ""),
        "ibm_narrative_cli_output_text": "",
    }


def run_section_ibm_narrative_spine(
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_test_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
) -> dict[str, Any]:
    """Section-only ibm_narrative lane (``ibm_narrative_dispatch`` module is implementation-only; CLI retired)."""
    from apps_rg.runtime.sections import ibm_narrative_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    if not jd_text:
        jd_text = lane.JD_TEXT_DEFAULT
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    lane_provider_eff = _effective_lane_provider(lane_provider)

    args = SimpleNamespace(
        provider=lane_provider_eff,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        allow_non_allow_exit_zero=bool(lane_allow_non_allow_exit_zero),
        base_resume_ref=str(resume_path or ""),
    )
    if lane_provider_eff == "external_claude":
        lo, hi = lane.IBM_NARRATIVE_TEMP_RANGE
        if args.temperature < lo or args.temperature > hi:
            return {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "error": (
                    f"temperature {args.temperature} outside ibm_narrative profile ({lo}-{hi})"
                ),
                "x3_disposition": "",
                "fault": "temperature_range",
                "artifact_dir": "",
                "run_id": "",
                "request_id": "",
                "l7_how_trace_emitted": False,
                "terminal_r5": False,
            }

    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_ibm_narrative_lane_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": ctx.get("output_text", ""),
    }


def _run_section_role_episode_spine(
    section_id: str,
    *,
    target_company: str,
    target_role: str,
    target_level: str,
    jd: str,
    job_description_ref: str,
    job_description_text: str,
    manual_brief: str,
    resume_path: str,
    source_resume_text: str,
    generation_mode: str,
    artifact_dir: str,
    lane_provider: str,
    lane_temperature: float,
    lane_x1d_judges: str,
    lane_mock_judges: bool,
    lane_allow_test_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
) -> dict[str, Any]:
    """Section-only generic role episode lane for InsurTech/EY bullets/narratives."""
    from apps_rg.runtime.sections import role_episode_lane as lane

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    jp = raw_request.get("jd_payload") if isinstance(raw_request.get("jd_payload"), dict) else {}
    jd_text = str(jp.get("description") or jp.get("title") or "").strip()
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        briefing = _resolve_lane_manual_brief(raw_request)

    lane_provider_eff = str(lane_provider or "").strip() or default_lane_provider_for_section(section_id)

    args = lane.build_role_episode_lane_args(
        provider=lane_provider_eff,
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        allow_non_allow_exit_zero=bool(lane_allow_non_allow_exit_zero),
        target_title=str(target_role).strip(),
        target_company=str(target_company).strip(),
        jd_text=jd_text,
        briefing=briefing,
        target_role=str(target_role).strip() or None,
        base_resume_ref=str(resume_path or ""),
    )
    override = Path(artifact_dir) if (artifact_dir is not None and str(artifact_dir).strip()) else None
    ctx = lane.run_role_episode_lane_execution(section_id, args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])
    x3 = ctx["x3"]
    outcome_authorized, exit_status, x3_code = _lane_dispatch_status_from_x3(x3)
    output_field = f"{section_id}_cli_output_text"
    out = {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": x3_code,
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": "",
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
        "insurtech_bullets_cli_output_text": "",
        "insurtech_narrative_cli_output_text": "",
        "ey_bullets_cli_output_text": "",
        "ey_narrative_cli_output_text": "",
    }
    out[output_field] = str(ctx.get("output_text") or "")
    return out


def run_section_insurtech_bullets_spine(**kwargs: Any) -> dict[str, Any]:
    kwargs.pop("lane_provider_resolution_source", None)
    return _run_section_role_episode_spine("insurtech_bullets", **kwargs)


def run_section_ey_bullets_spine(**kwargs: Any) -> dict[str, Any]:
    kwargs.pop("lane_provider_resolution_source", None)
    return _run_section_role_episode_spine("ey_bullets", **kwargs)


def run_section_insurtech_narrative_spine(**kwargs: Any) -> dict[str, Any]:
    kwargs.pop("lane_provider_resolution_source", None)
    return _run_section_role_episode_spine("insurtech_narrative", **kwargs)


def run_section_ey_narrative_spine(**kwargs: Any) -> dict[str, Any]:
    kwargs.pop("lane_provider_resolution_source", None)
    return _run_section_role_episode_spine("ey_narrative", **kwargs)
