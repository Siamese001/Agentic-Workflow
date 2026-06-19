"""Canonical apps_rg product dispatch — CLI primitives → R4 integrated spine.

``dispatch_apps_rg_run`` in ``agentic_core.runtime.entry.apps_rg_dispatch`` delegates
here so core stays a thin surface and app-owned orchestration holds request shaping.

On success, the R4 entrypoint emits L7 artifacts under ``artifact_dir`` (e.g.
``agentic_core_how_trace.json``).
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from apps_rg.runtime.orchestration.integrated_spine_runner import (
    run_integrated_single_action_spine,
)

from apps_rg.runtime.jd_resolution import resolve_jd_for_lanes
from apps_rg.runtime.resume_resolution import resolve_resume_for_lanes
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import find_repo_root, load_latest_pointer, proof_bucket_for_provider
from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS

# V6 terminal codes short values (integrated R4); legacy strings retained.
_SUCCESS_X3 = frozenset({"X3C", "X3D", "EXIT_OK", "EXIT_PARTIAL"})
# Soft-fail review codes that should NOT cascade-block downstream lanes per Author-Gate
# decision dec_19e6e344d5db19589 (architecture_choice, 2026-05-28).
_REVIEW_BUT_NOT_BLOCKING_X3 = frozenset({"X3_REVIEW_JUDGE_SOFT_FAIL", "X3_REVIEW"})
_HEADLINE_SECTION_ID = "headline"
_EXEC_SUMMARY_SECTION_ID = "executive_summary"
_UNIFY_BULLETS_SECTION_ID = "unify_bullets"
_UNIFY_NARRATIVE_SECTION_ID = "unify_narrative"
_IBM_BULLETS_SECTION_ID = "ibm_bullets"
_IBM_NARRATIVE_SECTION_ID = "ibm_narrative"
_COMPETENCIES_SECTION_ID = "competencies"
_DEFAULT_X1D_JUDGES = ",".join(REQUIRED_JUDGE_PROVIDER_KEYS)
# Single pool-selector judge (graph_8x8); not the executive-summary triple panel.
COMPETENCIES_LANE_X1D_JUDGES_DEFAULT = "gemini_pro"


def _effective_lane_provider(raw: str | None) -> str:
    """Non-empty CLI value wins; empty uses ``APPS_RG_MODULAR_LANE_PROVIDER`` / modular default."""
    from apps_rg.l2_recipe.r4_generation_mode import resolve_apps_rg_modular_lane_provider

    s = str(raw or "").strip()
    return s if s else resolve_apps_rg_modular_lane_provider()


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


def _materialize_fallback_brief(
    *,
    target_company: str,
    target_role: str = "",
    jd_path: Path | None,
    request_id: str,
    run_id: str,
    trace_id: str,
) -> str:
    """Generate a repo-local briefing.md when the caller omitted a brief.

    Prefer the managed apps_research delegation path so the resulting brief
    is JD-grounded and contract-sealed. Fall back to the older materializer
    only if the managed bridge cannot produce a usable brief.
    """
    if not str(target_company).strip():
        return ""

    repo_root = find_repo_root()
    artifact_root = repo_root / "artifacts" / "apps_rg" / "generated_briefs"
    try:
        from apps_rg.integrations.apps_research_bridge import AppsResearchBridge
        from apps_rg.integrations.managed_research_delegation import (
            RequestForResumeBriefing,
            ResumeBriefingReady,
            dispatch_resume_research_briefing,
        )

        bridge = AppsResearchBridge(capability_ref="apps_research.v1")
        req = RequestForResumeBriefing(
            request_id=str(request_id or f"req-{uuid.uuid4().hex[:12]}"),
            run_id=str(run_id or f"research-{uuid.uuid4().hex[:12]}"),
            trace_id=str(trace_id or f"trace-{uuid.uuid4().hex[:12]}"),
            company_name=target_company,
            job_title=str(target_role or target_company).strip(),
            research_authorized=True,
        )
        outcome = dispatch_resume_research_briefing(req, bridge=bridge)
        if isinstance(outcome, ResumeBriefingReady):
            brief_path = (
                artifact_root
                / f"research_{(outcome.research_run_id or req.run_id)[:8]}"
                / "briefing.md"
            )
            brief_path.parent.mkdir(parents=True, exist_ok=True)
            brief_path.write_text(outcome.briefing_text.rstrip() + "\n", encoding="utf-8")
            return str(brief_path)
    except (ImportError, OSError, TypeError, ValueError):
        pass

    return ""


def _resolve_lane_manual_brief(manual_brief: str) -> str:
    """Resolve briefing for section lanes (path, URI, inline, or lane resolver fallback)."""
    briefing = _read_optional_brief(manual_brief)
    if str(briefing).strip():
        return briefing
    ref = str(manual_brief or "").strip()
    if not ref:
        return ""
    from apps_rg.runtime.briefing_resolution import BriefingResolutionError, resolve_briefing_for_lanes

    try:
        resolved = resolve_briefing_for_lanes(briefing_artifact_ref=ref, require_run_specific=True)
    except BriefingResolutionError:
        return ""
    return str(resolved.text or "").strip()


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
    """Shape a raw_request dict for ``run_integrated_single_action_spine``."""
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
    resolved_manual_brief = str(manual_brief or "").strip()
    brief_text = _read_optional_brief(manual_brief)
    if not brief_text:
        fallback_jd_path: Path | None = None
        for candidate in (jd_ref, jd_legacy):
            if candidate and Path(candidate).is_file():
                fallback_jd_path = Path(candidate)
                break
        generated_brief = _materialize_fallback_brief(
            target_company=str(target_company),
            target_role=str(target_role),
            jd_path=fallback_jd_path,
            request_id="",
            run_id="",
            trace_id="",
        )
        if generated_brief:
            resolved_manual_brief = generated_brief
            brief_text = _read_optional_brief(generated_brief)
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
        "manual_brief": resolved_manual_brief,
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
    from apps_rg.runtime.runtime_proof_layout import (
        allocate_full_resume_artifact_dir,
        find_repo_root,
    )

    return allocate_full_resume_artifact_dir(find_repo_root(), explicit)


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
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
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
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
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
    except OSError:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return


def run_canonical_full_resume_from_cli_primitives(
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
    lane_temperature: float = 0.45,
    lane_x1d_judges: str = _DEFAULT_X1D_JUDGES,
    lane_mock_judges: bool = False,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Full résumé integrated R4 spine (no ``--section``)."""
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

    from apps_rg.cache.whole_run_entrypoint_preflight import (
        ENTRYPOINT_CANONICAL_DISPATCH,
        build_cache_hit_dispatch_result,
        maybe_ingest_r1b_post_exit,
        run_whole_run_cache_preflight,
    )

    preflight = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request=raw_request,
        target_company=target_company,
        target_role=target_role,
        artifact_dir=art,
        runs_dir=art.parent,
        policy_hash=os.environ.get("APPS_RG_POLICY_HASH"),
        blueprint_hash=os.environ.get("APPS_RG_BLUEPRINT_HASH"),
        section=section,
    )
    from apps_rg.cache.cache_preflight_evidence import (
        build_cache_preflight_evidence,
        write_cache_hit_receipt,
        write_cache_miss_receipt,
        write_whole_run_cache_preflight_artifact,
    )

    evidence = build_cache_preflight_evidence(preflight, artifact_dir=art)
    write_whole_run_cache_preflight_artifact(art, preflight, evidence)

    if not preflight.generation_required:
        write_cache_hit_receipt(art, preflight, evidence)
        hit_result = build_cache_hit_dispatch_result(preflight)
        hit_result["cache_preflight"] = evidence
        if preflight.r1a_hit:
            hit_result["artifact_dir"] = preflight.r1a_artifact_dir
        return hit_result

    write_cache_miss_receipt(art, preflight, evidence)

    result = run_integrated_single_action_spine(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=art,
        route_family="R4_SINGLE_ACTION",
        cache_preflight_evidence=evidence,
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

    maybe_ingest_r1b_post_exit(
        raw_request=raw_request,
        artifact_dir=art,
        runs_dir=art.parent,
    )

    l7_path = art / "agentic_core_how_trace.json"
    l7_ok = bool(result.fault == "" and l7_path.is_file())
    soft_fail_review = (
        result.fault == ""
        and result.x3_disposition in _REVIEW_BUT_NOT_BLOCKING_X3
    )
    outcome = (
        result.fault == ""
        and (result.x3_disposition in _SUCCESS_X3 or soft_fail_review)
    )
    # success_with_review keeps exit_status == "success" so phase1_dispatch_hard_failed()
    # does NOT cascade-block downstream lanes; the review packet preserves the soft-fail
    # for human inspection.
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
    lane_x1d_judges: str = _DEFAULT_X1D_JUDGES,
    lane_mock_judges: bool = False,
    lane_allow_non_allow_exit_zero: bool = False,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """CLI dispatch — delegates to single ``apps_rg_spine_run`` entry (d8f4a2)."""
    from apps_rg.runtime.spine.apps_rg_spine_run import run_apps_rg_spine

    sid = str(section).strip()
    scope = "section" if sid else "full"
    return run_apps_rg_spine(
        scope=scope,
        section_id=sid,
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
        lane_allow_non_allow_exit_zero=lane_allow_non_allow_exit_zero,
        lane_allow_test_mock_judges=lane_allow_test_mock_judges,
    )


def execute_executive_summary_section_from_cli(
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
    lane_provider: str = "",
    lane_provider_resolution_source: str | None = None,
    lane_temperature: float = 0.45,
    lane_x1d_judges: str = _DEFAULT_X1D_JUDGES,
    lane_mock_judges: bool = False,
    lane_allow_test_mock_judges: bool = False,
) -> dict[str, Any]:
    """Section-only executive_summary CLI primitive (compat for integrated materialization tests)."""
    from apps_rg.runtime.spine.section_cli_runners import run_section_executive_summary_spine

    return run_section_executive_summary_spine(
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
        lane_temperature=lane_temperature,
        lane_x1d_judges=lane_x1d_judges,
        lane_mock_judges=lane_mock_judges,
        lane_allow_test_mock_judges=lane_allow_test_mock_judges,
    )


__all__ = [
    "build_raw_request_for_r4",
    "execute_executive_summary_section_from_cli",
    "run_canonical_apps_rg_from_cli_primitives",
    "run_canonical_full_resume_from_cli_primitives",
]
