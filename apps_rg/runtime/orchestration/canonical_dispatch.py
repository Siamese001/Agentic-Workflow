"""Canonical apps_rg product dispatch — CLI primitives → R4 integrated spine.

``dispatch_apps_rg_run`` in ``agentic_core.runtime.entry.apps_rg_dispatch`` delegates
here so core stays a thin surface and app-owned orchestration holds request shaping.

On success, the R4 entrypoint emits L7 artifacts under ``artifact_dir`` (e.g.
``agentic_core_how_trace.json``).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import (
    run_integrated_r4_deterministic_pipeline,
)

from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import resolve_resume_for_lanes
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import find_repo_root, load_latest_pointer, proof_bucket_for_provider

# V6 terminal codes short values (integrated R4); legacy strings retained.
_SUCCESS_X3 = frozenset({"X3C", "X3D", "EXIT_OK", "EXIT_PARTIAL"})
_HEADLINE_SECTION_ID = "headline"
_EXEC_SUMMARY_SECTION_ID = "executive_summary"
_UNIFY_BULLETS_SECTION_ID = "unify_bullets"
_UNIFY_NARRATIVE_SECTION_ID = "unify_narrative"
_IBM_BULLETS_SECTION_ID = "ibm_bullets"
_IBM_NARRATIVE_SECTION_ID = "ibm_narrative"
_COMPETENCIES_SECTION_ID = "competencies"


def _effective_lane_provider(raw: str | None) -> str:
    """Non-empty CLI value wins; empty uses ``APPS_RG_MODULAR_LANE_PROVIDER`` / modular default."""
    from apps_rg.l2_recipe.r4_generation_mode import resolve_apps_rg_modular_lane_provider

    s = str(raw or "").strip()
    return s if s else resolve_apps_rg_modular_lane_provider()


def _run_competencies_lane_from_cli(
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
    selected_role_fact_set: str = "",
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
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        briefing = lane.BRIEFING_DEFAULT

    args = lane.build_competencies_lane_args(
        provider=_effective_lane_provider(lane_provider),
        temperature=float(lane_temperature),
        x1d_judges=str(lane_x1d_judges),
        mock_judges=bool(lane_mock_judges),
        allow_test_mock_judges=bool(lane_allow_test_mock_judges),
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        target_role=str(target_role).strip() or None,
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_competencies_lane_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])
    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
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


def _run_headline_lane_from_cli(
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
    selected_role_fact_set: str = "",
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
    briefing = _read_optional_brief(manual_brief)
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
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_headline_lane_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])
    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
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


def _run_executive_summary_lane_from_cli(
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
    selected_role_fact_set: str = "",
) -> dict[str, Any]:
    """Section-only run: same artifacts as legacy dispatch; does not invoke ``dispatch_apps_rg_run``."""
    from apps_rg.runtime.sections import executive_summary_lane as lane

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
    briefing = _read_optional_brief(manual_brief)
    if not str(briefing).strip():
        from apps_rg.runtime.section_cli_defaults import default_targeting_briefing_text

        briefing = default_targeting_briefing_text()

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
        target_title=str(target_role).strip() or lane.TARGET_TITLE_DEFAULT,
        target_company=str(target_company).strip() or lane.TARGET_COMPANY_DEFAULT,
        jd_text=jd_text,
        briefing=briefing,
        target_role=str(target_role).strip() or None,
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )
    if eff_prov == "qwen_vllm":
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

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_executive_summary_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
        "fault": "",
        "artifact_dir": str(artifact_path),
        "run_id": str(ctx["runtime_payload"].get("run_id", "")),
        "request_id": "",
        "l7_how_trace_emitted": False,
        "terminal_r5": False,
        "executive_summary_cli_output_text": ctx.get("output_text", ""),
        "headline_cli_output_text": "",
        "unify_bullets_cli_output_text": "",
        "unify_narrative_cli_output_text": "",
        "ibm_bullets_cli_output_text": "",
        "ibm_narrative_cli_output_text": "",
    }


def _run_unify_bullets_lane_from_cli(
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
    selected_role_fact_set: str = "",
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

    lane_provider_eff = _effective_lane_provider(lane_provider)

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
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )
    if lane_provider_eff == "qwen_vllm":
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

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_unify_bullets_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
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


def _run_unify_narrative_lane_from_cli(
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
    selected_role_fact_set: str = "",
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
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )
    if lane_provider_eff == "qwen_vllm":
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

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_unify_narrative_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
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


def _run_ibm_bullets_lane_from_cli(
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
    selected_role_fact_set: str = "",
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
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )
    if lane_provider_eff == "qwen_vllm":
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

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_ibm_bullets_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
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


def _run_ibm_narrative_lane_from_cli(
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
    selected_role_fact_set: str = "",
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
        selected_role_fact_set=str(selected_role_fact_set or ""),
    )
    if lane_provider_eff == "qwen_vllm":
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

    override = Path(artifact_dir) if str(artifact_dir).strip() else None
    ctx = lane.run_ibm_narrative_lane_execution(args, artifact_dir_override=override)
    artifact_path = Path(ctx["artifact_dir"])

    x3 = ctx["x3"]
    outcome_authorized = bool(getattr(x3, "pass_", False))
    exit_status = "success" if outcome_authorized else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome_authorized else "failed",
        "outcome_authorized": outcome_authorized,
        "x3_disposition": getattr(x3, "x3_code", ""),
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


_BRIEF_FETCH_MAX_BYTES = 2_000_000


def _fetch_url_text(url: str, *, max_bytes: int = _BRIEF_FETCH_MAX_BYTES) -> str:
    """Fetch brief content from http(s); bounded read for CLI safety."""
    req = Request(url, headers={"User-Agent": "apps_rg-cli/1"})
    with urlopen(req, timeout=45) as resp:  # noqa: S310 — intentional user-supplied brief URL
        raw = resp.read(max_bytes + 1)
    if len(raw) > max_bytes:
        return ""
    return raw.decode("utf-8", errors="replace")


def _read_optional_brief(path_or_url: str) -> str:
    """Load research brief from local path or http(s) URL."""
    s = str(path_or_url).strip()
    if not s:
        return ""
    if s.startswith(("http://", "https://")):
        try:
            return _fetch_url_text(s)
        except (HTTPError, URLError, OSError, ValueError):
            return ""
    return _read_optional_file(s)


def _read_optional_file(path_str: str) -> str:
    if not str(path_str).strip():
        return ""
    p = Path(path_str)
    if p.is_file():
        try:
            return p.read_text(encoding="utf-8")
        except OSError:
            return ""
    return str(path_str)


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build_raw_request_for_r4(
    *,
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
) -> dict[str, Any]:
    """Shape a raw_request dict for ``run_integrated_r4_deterministic_pipeline``."""
    jd_legacy = str(jd).strip()
    jd_ref = str(job_description_ref).strip()
    jd_txt = str(job_description_text).strip()
    if jd_legacy and not jd_ref and not jd_txt:
        p = Path(jd_legacy)
        if p.is_file():
            jd_ref = jd_legacy
        else:
            jd_txt = jd_legacy

    jd_resolved = resolve_jd_for_lanes(
        job_description_ref=jd_ref or None,
        job_description_text=jd_txt or None,
        target_company=str(target_company),
        target_role=str(target_role),
    )
    jd_payload = {
        "title": jd_resolved.title,
        "description": jd_resolved.description,
        "company": jd_resolved.company,
    }
    brief_text = _read_optional_brief(manual_brief)
    rp = str(resume_path).strip()
    st = str(source_resume_text).strip()
    res_resolved = resolve_resume_for_lanes(
        source_resume_text=st or None,
        source_resume_ref=rp or None,
        require_json_document=False,
    )

    master_resume_data = ""
    if res_resolved.resume_dict is not None:
        master_resume_data = json.dumps(
            res_resolved.resume_dict,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    jd_blob = json.dumps(jd_payload, sort_keys=True, separators=(",", ":"))
    jd_hash = jd_resolved.jd_digest
    brief_hash = hashlib.sha256(brief_text.encode("utf-8")).hexdigest() if brief_text else _sha16("no_brief")
    resume_hash = res_resolved.resume_digest

    return {
        # E1 intake allowlist excludes "cli"; local CLI runs are user-driven → "ui".
        "transport": "ui",
        "method": "POST",
        "content_type": "application/json",
        "source_channel": "apps_rg_cli",
        "declared_schema": "apps_rg_jd_v1",
        "tenant_id": "default",
        "user_id": "apps_rg_cli_user",
        "target_company": target_company,
        "target_role": target_role,
        "target_level": target_level,
        "manual_brief": manual_brief or "",
        "generation_mode": generation_mode,
        "jd_payload": jd_payload,
        "jd_hash": jd_hash,
        "brief_hash": brief_hash,
        "resume_hash": resume_hash,
        "master_resume_data": master_resume_data,
        "flow_route": "tailor_existing",
        "body_text": jd_blob,
    }


def _default_artifact_dir(explicit: str) -> Path:
    if str(explicit).strip():
        return Path(explicit)
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            root = parent
            break
    else:
        root = Path.cwd()
    rid = uuid.uuid4().hex[:12]
    out = root / "artifacts" / "apps_rg" / "runs" / f"cli_{rid}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _augment_integrated_manifest_with_apps_rg_docx(artifact_dir: Path) -> None:
    """Add DOCX pointer fields when ``outputs/resume.docx`` exists.

    Does not modify ``artifact_filenames`` — SSOT chain enumerations stay stable.
    """
    docx = artifact_dir / "outputs" / "resume.docx"
    manifest_path = artifact_dir / "integrated_runtime_artifact_manifest.json"
    if not docx.is_file() or not manifest_path.is_file():
        return
    try:
        digest = hashlib.sha256(docx.read_bytes()).hexdigest()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["apps_rg_resume_docx_relpath"] = "outputs/resume.docx"
        data["apps_rg_resume_docx_sha256"] = f"sha256:{digest}"
        manifest_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, TypeError):
        return


def _augment_r4_run_manifest_for_apps_rg_l2_fault(
    artifact_dir: Path,
    *,
    fault: str,
    x3_disposition: str,
) -> None:
    """Align ``r4_run_manifest.json`` with apps_rg full-résumé product truth when L2 faults.

    Core R4 already coerces ``x3_disposition`` to DENY (X3A) when ``l2_fault`` is set;
    this adds explicit product fields so operators are not misled by envelope-only X3
    history and records missing résumé artifacts.
    """
    if not str(fault).strip():
        return
    path = artifact_dir / "r4_run_manifest.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return

    gen_status = "L2_EXECUTION_FAILED"
    if "BLOCKED_STUB_PROVIDER" in fault:
        gen_status = "BLOCKED_STUB_PROVIDER"
    elif "BLOCKED_PROVIDER_LANE" in fault:
        gen_status = "BLOCKED_PROVIDER_LANE"
    elif "FAILED_PROVIDER" in fault:
        gen_status = "FAILED_PROVIDER"
    elif "FAILED_ARTIFACT_GATE" in fault:
        gen_status = "FAILED_ARTIFACT_GATE"

    data["x3_disposition"] = x3_disposition
    data["apps_rg_terminal_class"] = "failure"
    data["apps_rg_product_outcome_authorized"] = False
    data["apps_rg_generation_status"] = gen_status
    data["apps_rg_full_resume_generated"] = False
    data["apps_rg_required_resume_artifacts"] = {
        "outputs/generated_resume.json": "missing",
        "outputs/resume.docx": "missing",
    }
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return


def run_canonical_apps_rg_from_cli_primitives(
    *,
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
    section: str = "",
    lane_provider: str = "",
    lane_provider_resolution_source: str | None = None,
    lane_temperature: float = 0.45,
    lane_x1d_judges: str = "gemini_pro,openai_chatgpt,anthropic_claude",
    lane_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
    lane_allow_test_mock_judges: bool = False,
    selected_role_fact_set: str = "",
) -> dict[str, Any]:
    """Run governed R4 spine for apps_rg; return CLI-shaped result dict."""
    if str(section).strip().lower() == _HEADLINE_SECTION_ID:
        return _run_headline_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            lane_allow_non_allow_exit_zero=lane_allow_non_allow_exit_zero,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )
    if str(section).strip().lower() == _EXEC_SUMMARY_SECTION_ID:
        return _run_executive_summary_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_provider_resolution_source=lane_provider_resolution_source,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )
    if str(section).strip().lower() == _UNIFY_BULLETS_SECTION_ID:
        return _run_unify_bullets_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_non_allow_exit_zero=lane_allow_non_allow_exit_zero,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )
    if str(section).strip().lower() == _UNIFY_NARRATIVE_SECTION_ID:
        return _run_unify_narrative_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )
    if str(section).strip().lower() == _IBM_BULLETS_SECTION_ID:
        return _run_ibm_bullets_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_non_allow_exit_zero=lane_allow_non_allow_exit_zero,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )
    if str(section).strip().lower() == _IBM_NARRATIVE_SECTION_ID:
        return _run_ibm_narrative_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            lane_allow_non_allow_exit_zero=lane_allow_non_allow_exit_zero,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )
    if str(section).strip().lower() == _COMPETENCIES_SECTION_ID:
        return _run_competencies_lane_from_cli(
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
            artifact_dir=artifact_dir,
            lane_provider=lane_provider,
            lane_temperature=float(lane_temperature),
            lane_x1d_judges=lane_x1d_judges,
            lane_mock_judges=lane_mock_judges,
            lane_allow_test_mock_judges=lane_allow_test_mock_judges,
            selected_role_fact_set=str(selected_role_fact_set or ""),
        )

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
    art = _default_artifact_dir(artifact_dir)

    result = run_integrated_r4_deterministic_pipeline(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=art,
    )
    _augment_integrated_manifest_with_apps_rg_docx(art)
    _augment_r4_run_manifest_for_apps_rg_l2_fault(
        art,
        fault=result.fault,
        x3_disposition=result.x3_disposition,
    )

    rid = str(getattr(result, "run_id", "") or "").strip()
    emit_integrated_run_bundle_index(
        find_repo_root(),
        art,
        run_id=rid or None,
        correlation_id=rid or None,
    )

    l7_path = art / "agentic_core_how_trace.json"
    l7_ok = bool(result.fault == "" and l7_path.is_file())
    outcome = (
        result.fault == ""
        and result.x3_disposition in _SUCCESS_X3
    )
    exit_status = "success" if outcome else "error"

    return {
        "exit_status": exit_status,
        "execution_status": "completed" if outcome else "failed",
        "outcome_authorized": outcome,
        "x3_disposition": result.x3_disposition,
        "fault": result.fault,
        "artifact_dir": str(art),
        "run_id": result.run_id,
        "request_id": result.request_id,
        "l7_how_trace_emitted": l7_ok,
        "terminal_r5": result.terminal_r5,
    }


__all__ = [
    "build_raw_request_for_r4",
    "run_canonical_apps_rg_from_cli_primitives",
]
