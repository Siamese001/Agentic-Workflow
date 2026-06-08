"""Whole-run CLI: U0→L1→L0 route governance + optional R3R4 apps_research → R4 draft leg."""
from __future__ import annotations

import dataclasses
import json
import os
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.orchestration.integrated_spine_runner import (
    run_integrated_single_action_spine,
)

from apps_rg.runtime.bindings.briefing_mode_classifier import classify_briefing_mode
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.dispatch import spine_stage_receipts as sr
from apps_rg.runtime.full_resume_review_bundle import (
    REVIEW_BUNDLE_FILENAME,
    emit_full_resume_review_bundle,
)
from apps_rg.runtime.proof.x3_disposition_normalize import normalize_x3_code
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import (
    allocate_full_resume_artifact_dir,
    find_repo_root,
    is_integrated_whole_run_dir_name,
)

ROUTE_FAMILY_R3R4 = "R3R4_MANAGED_WORKFLOW"
DRAFT_LEG_ROUTE_FAMILY = "R4_SINGLE_ACTION"
_SUCCESS_X3 = frozenset({"X3C", "X3D", "EXIT_OK", "EXIT_PARTIAL"})


def _aggregate_x3_for_outcome(raw_x3: str | None, *, outcome: bool) -> str:
    """G16: a whole run that authorized zero lanes surfaces an explicit BLOCK.

    The frozen AIG/Brown failure reported ``X3A`` (which normalizes to UNKNOWN — never an allow)
    while every lane was ``X3_BLOCK``. When the run is not authorized AND the disposition is the
    ambiguous UNKNOWN bucket, force an explicit ``X3_BLOCK`` so the aggregate reads honestly and
    matches the lanes. Authorized runs, and runs with an already-explicit block/review/allow
    disposition, are left untouched.
    """
    x3 = str(raw_x3 or "")
    if not outcome and normalize_x3_code(x3) == "UNKNOWN":
        return "X3_BLOCK"
    return x3


def _default_artifact_dir(explicit: str) -> Path:
    if str(explicit).strip():
        return Path(explicit)
    return allocate_full_resume_artifact_dir(find_repo_root())


def _read_optional_brief(path_or_url: str) -> str:
    from apps_rg.runtime.orchestration.canonical_dispatch import _read_optional_brief as _rob

    return _rob(path_or_url)


def research_delegation_enabled(
    *,
    auto_research_internal: bool,
    research_via: str | None,
) -> bool:
    _ = auto_research_internal, research_via
    return False


def briefing_input_present(manual_brief: str) -> bool:
    return bool(_read_optional_brief(manual_brief).strip())


def should_delegate_apps_research(
    *,
    route_family: str,
    manual_brief: str,
    auto_research_internal: bool,
    research_via: str | None,
) -> bool:
    if route_family != ROUTE_FAMILY_R3R4:
        return False
    if briefing_input_present(manual_brief):
        return False
    return research_delegation_enabled(
        auto_research_internal=auto_research_internal,
        research_via=research_via,
    )


def _research_bridge() -> Any:
    import importlib

    if os.environ.get("APPS_RG_MOCK_RESEARCH", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        MockAppsResearchBridge = getattr(
            importlib.import_module("apps_rg.integrations.apps_research_bridge"),
            "MockAppsResearchBridge",
        )
        return MockAppsResearchBridge(confidence_score=0.88)

    AppsResearchBridge = getattr(
        importlib.import_module("apps_rg.integrations.apps_research_bridge"),
        "AppsResearchBridge",
    )
    return AppsResearchBridge(capability_ref="apps_research.v1")


def _build_cli_ingress_envelope(
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
    auto_research_internal: bool,
    research_via: str | None,
) -> SimpleNamespace:
    request_id = f"req-{uuid.uuid4().hex}"
    run_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    app_payload: dict[str, Any] = {
        "target_company": target_company,
        "target_role": target_role,
        "target_title": target_role,
        "target_level": target_level,
        "job_description_text": job_description_text,
        "jd_text": job_description_text,
        "job_description_ref": job_description_ref,
        "manual_brief_path": manual_brief,
        "briefing_artifact_ref": manual_brief,
        "source_resume_ref": resume_path,
        "source_resume_text": source_resume_text,
        "generation_mode": generation_mode,
        "task_spec": {"generation_mode": generation_mode},
        "transport": "ui",
        "source_channel": "apps_rg_cli",
        "auto_research_internal": auto_research_internal,
        "research_via": research_via,
    }
    return SimpleNamespace(
        app_payload=app_payload,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        app_id="apps_rg",
        tenant_id="default",
    )


def _route_contract_payload(route: Any) -> dict[str, Any]:
    return {
        "route_id": route.route_id,
        "route_family": route.route_family,
        "execution_form": route.execution_form,
        "l3_required": route.l3_required,
        "grounding_required": route.grounding_required,
        "route_profile_ref": route.route_profile_ref,
        "reason_codes": list(route.reason_codes),
        "request_id": route.request_id,
        "run_id": route.run_id,
        "trace_id": route.trace_id,
    }


def _write_mock_elimination_proof(artifact_dir: Path, bridge: Any) -> None:
    sr.write_stage_receipt(
        artifact_dir / sr.FILENAME_MOCK_ELIMINATION_PROOF,
        {
            "APPS_RG_MOCK_RESEARCH": os.environ.get("APPS_RG_MOCK_RESEARCH", ""),
            "bridge_class": type(bridge).__name__,
            "mock_env_active": os.environ.get("APPS_RG_MOCK_RESEARCH", "").strip().lower()
            in ("1", "true", "yes"),
        },
    )


def _run_r3r4_research_hop(
    *,
    route: Any,
    validated_request: Any,
    artifact_dir: Path,
    target_company: str,
    target_role: str,
) -> tuple[bool, str, str]:
    import importlib

    _delegation = importlib.import_module(
        "apps_rg.integrations.managed_research_delegation"
    )
    RequestForResumeBriefing = _delegation.RequestForResumeBriefing
    ResearchDispatchFailure = _delegation.ResearchDispatchFailure
    ResumeBriefingReady = _delegation.ResumeBriefingReady
    dispatch_resume_research_briefing = _delegation.dispatch_resume_research_briefing

    req = RequestForResumeBriefing(
        request_id=route.request_id,
        run_id=route.run_id,
        trace_id=route.trace_id,
        company_name=target_company,
        job_title=target_role,
        research_authorized=True,
    )
    bridge = _research_bridge()
    _write_mock_elimination_proof(artifact_dir, bridge)
    sr.write_stage_receipt(
        artifact_dir / sr.FILENAME_ROUTE_PRE_RESEARCH,
        _route_contract_payload(route),
    )
    sr.write_stage_receipt(
        artifact_dir / sr.FILENAME_RESEARCH_BRIDGE_REQUEST,
        dataclasses.asdict(req),
    )

    outcome = dispatch_resume_research_briefing(req, bridge=bridge)

    if isinstance(outcome, ResumeBriefingReady):
        sr.write_stage_receipt(
            artifact_dir / sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
            {
                "outcome": "ResumeBriefingReady",
                "research_run_id": outcome.research_run_id,
                "research_evidence_count": outcome.research_evidence_count,
                "confidence_score": outcome.confidence_score,
                "evidence_lineage": list(outcome.evidence_lineage),
                "research_artifact_dir": outcome.research_artifact_dir,
            },
        )
        brief_path = artifact_dir / sr.FILENAME_DELEGATED_BRIEFING
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(outcome.briefing_text + "\n", encoding="utf-8")
        fec_path = artifact_dir / sr.FILENAME_RESEARCH_EVIDENCE_CONTRACT
        sr.write_stage_receipt(
            fec_path,
            {
                "schema_version": "apps_rg.research_fec_stub.v1",
                "research_run_id": outcome.research_run_id,
                "result_hash": outcome.result_hash,
                "evidence_lineage": list(outcome.evidence_lineage),
                "confidence_score": outcome.confidence_score,
                "proof_note": "FEC-shaped contract for external review; full FEC lives under apps_research run when present.",
            },
        )
        if outcome.research_artifact_dir:
            sr.write_stage_receipt(
                artifact_dir / "research" / "research_artifact_ref.json",
                {
                    "research_run_id": outcome.research_run_id,
                    "research_artifact_dir": outcome.research_artifact_dir,
                },
            )
        return True, "ResumeBriefingReady", str(brief_path)

    if isinstance(outcome, ResearchDispatchFailure):
        sr.write_stage_receipt(
            artifact_dir / sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
            {
                "outcome": "ResearchDispatchFailure",
                "r5_reason_code": outcome.r5_reason_code,
                "detail": outcome.detail,
            },
        )
        return False, outcome.r5_reason_code, ""

    return False, "unknown_dispatch_outcome", ""


def _augment_r4_manifest_draft_leg_only(artifact_dir: Path, *, spine_manifest_ref: str) -> None:
    path = artifact_dir / sr.FILENAME_DRAFT_LEG_MANIFEST
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return
    data["apps_rg_proof_scope"] = "draft_leg_only"
    data["apps_rg_orchestration_manifest_ref"] = spine_manifest_ref
    data["apps_rg_whole_run_route_family"] = ROUTE_FAMILY_R3R4
    data["apps_rg_draft_leg_route_family"] = DRAFT_LEG_ROUTE_FAMILY
    data["apps_rg_whole_dag_proof_authority"] = spine_manifest_ref
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return


def _failure_payload(
    *,
    artifact_dir: Path,
    route: Any,
    reason: str,
    route_decision: dict[str, Any],
) -> dict[str, Any]:
    spine = {
        "schema_version": "apps_rg.spine_run_manifest.v1",
        "route_family": ROUTE_FAMILY_R3R4,
        "route_id": route.route_id,
        "execution_form": route.execution_form,
        "proof_authority": "spine_run_manifest.json",
        "draft_leg_manifest": sr.FILENAME_DRAFT_LEG_MANIFEST,
        "draft_leg_proof_scope": "draft_leg_only",
        "research_delegation_required": True,
        "research_delegation_outcome": reason,
        "route_decision": route_decision,
        "terminal_r5": True,
        "x3_disposition": "X3_BLOCK",
        "exit_status": "error",
        "outcome_authorized": False,
    }
    sr.write_stage_receipt(artifact_dir / sr.FILENAME_SPINE_MANIFEST, spine)
    return {
        "exit_status": "error",
        "execution_status": "failed",
        "outcome_authorized": False,
        "x3_disposition": "X3_BLOCK",
        "fault": reason,
        "artifact_dir": str(artifact_dir),
        "route_family": ROUTE_FAMILY_R3R4,
        "spine_run_manifest": str(artifact_dir / sr.FILENAME_SPINE_MANIFEST),
        "research_note": reason,
    }


def run_whole_run_with_route_governance(
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
    auto_research_internal: bool = True,
    research_via: str | None = None,
) -> dict[str, Any]:
    """Canonical whole-run path: L0 route + optional R3R4 research + R4 draft leg."""
    art = _default_artifact_dir(artifact_dir)
    repo = find_repo_root()

    from apps_rg.runtime.embedding_settings import (
        apply_apps_rg_embedding_env_guards,
        bootstrap_apps_rg_embedding_env,
        write_embedding_settings_receipt,
    )

    bootstrap_apps_rg_embedding_env(repo_root=repo)
    emb = apply_apps_rg_embedding_env_guards(chroma_persist_dir=os.environ.get("CHROMA_PERSIST_DIR"))
    write_embedding_settings_receipt(art, emb)

    envelope = _build_cli_ingress_envelope(
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
        auto_research_internal=auto_research_internal,
        research_via=research_via,
    )
    validated_request = u0_validate_apps_rg(envelope, allow_missing_profiles=False)
    l1_plan = l1_plan_apps_rg(validated_request)
    route = l0_route_apps_rg(l1_plan)

    briefing_mode = classify_briefing_mode(
        validated_request.app_payload or {},
        chroma_path_resolved=None,
        research_via=research_via,
    )
    route_decision = {
        "route_profile_ref": route.route_profile_ref,
        "route_family": route.route_family,
        "route_id": route.route_id,
        "execution_form": route.execution_form,
        "briefing_mode": briefing_mode.retrieval_mode,
        "briefing_classified_from": briefing_mode.classified_from,
        "research_delegation_enabled": research_delegation_enabled(
            auto_research_internal=auto_research_internal,
            research_via=research_via,
        ),
        "briefing_input_present": briefing_input_present(manual_brief),
    }

    sr.write_stage_receipt(
        art / sr.FILENAME_INGRESS_RAW,
        {
            "target_company": target_company,
            "target_role": target_role,
            "generation_mode": generation_mode,
            "manual_brief": manual_brief,
            "auto_research_internal": auto_research_internal,
            "research_via": research_via,
        },
    )
    sr.write_stage_receipt(
        art / sr.FILENAME_U0_RECEIPT,
        {
            "request_id": validated_request.request_id,
            "run_id": validated_request.run_id,
            "trace_id": validated_request.trace_id,
            "payload_digest": validated_request.payload_digest,
        },
    )
    sr.write_stage_receipt(
        art / sr.FILENAME_L1_PLAN,
        {
            "request_id": l1_plan.request_id,
            "merge_required_hint": l1_plan.merge_required_hint,
            "grounding_required": l1_plan.grounding_required,
            "work_shape": l1_plan.work_shape,
        },
    )
    sr.write_stage_receipt(art / sr.FILENAME_ROUTE_CONTRACT, _route_contract_payload(route))

    manual_brief_eff = manual_brief
    research_ran = False
    research_note = ""

    if should_delegate_apps_research(
        route_family=route.route_family,
        manual_brief=manual_brief,
        auto_research_internal=auto_research_internal,
        research_via=research_via,
    ):
        ok, research_note, brief_path = _run_r3r4_research_hop(
            route=route,
            validated_request=validated_request,
            artifact_dir=art,
            target_company=target_company,
            target_role=target_role,
        )
        research_ran = True
        route_decision["research_delegation_executed"] = True
        route_decision["research_outcome"] = research_note
        if not ok:
            route_decision["research_failure"] = research_note
            return _failure_payload(
                artifact_dir=art,
                route=route,
                reason=research_note,
                route_decision=route_decision,
            )
        manual_brief_eff = brief_path
        route_decision["delegated_briefing_path"] = brief_path
    else:
        route_decision["research_delegation_executed"] = False
        if (
            route.route_family == ROUTE_FAMILY_R3R4
            and not briefing_input_present(manual_brief)
            and not research_delegation_enabled(
                auto_research_internal=auto_research_internal,
                research_via=research_via,
            )
        ):
            route_decision["research_skipped_reason"] = "research_disabled"

    spine_pre_draft = {
        "schema_version": "apps_rg.spine_run_manifest.v1",
        "route_family": route.route_family,
        "route_id": route.route_id,
        "execution_form": route.execution_form,
        "proof_authority": "spine_run_manifest.json",
        "draft_leg_manifest": sr.FILENAME_DRAFT_LEG_MANIFEST,
        "draft_leg_proof_scope": "draft_leg_only",
        "research_delegation_executed": research_ran,
        "research_note": research_note,
        "route_decision": route_decision,
        "downstream_refs": {
            "route_contract": sr.FILENAME_ROUTE_CONTRACT,
            "research_bridge_request": sr.FILENAME_RESEARCH_BRIDGE_REQUEST,
            "research_bridge_response": sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
            "delegated_briefing": sr.FILENAME_DELEGATED_BRIEFING if research_ran else None,
        },
    }
    sr.write_stage_receipt(art / sr.FILENAME_SPINE_MANIFEST, spine_pre_draft)

    from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4

    raw_request = build_raw_request_for_r4(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        jd=jd,
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
        manual_brief=manual_brief_eff,
        resume_path=resume_path,
        source_resume_text=source_resume_text,
        generation_mode=generation_mode,
    )
    raw_request["research_via"] = "apps_research" if research_ran else research_via
    raw_request["route_decision_ref"] = sr.FILENAME_SPINE_MANIFEST

    from apps_rg.cache.whole_run_entrypoint_preflight import (
        ENTRYPOINT_CANONICAL_DISPATCH,
        build_cache_hit_dispatch_result,
        maybe_ingest_r1b_post_exit,
        run_whole_run_cache_preflight,
    )
    from apps_rg.cache.cache_preflight_evidence import (
        build_cache_preflight_evidence,
        write_cache_hit_receipt,
        write_cache_miss_receipt,
        write_whole_run_cache_preflight_artifact,
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
        section="",
    )
    evidence = build_cache_preflight_evidence(preflight, artifact_dir=art)
    write_whole_run_cache_preflight_artifact(art, preflight, evidence)

    if not preflight.generation_required:
        write_cache_hit_receipt(art, preflight, evidence)
        hit = build_cache_hit_dispatch_result(preflight)
        hit["cache_preflight"] = evidence
        hit["route_family"] = route.route_family
        hit["spine_run_manifest"] = str(art / sr.FILENAME_SPINE_MANIFEST)
        hit["route_decision"] = route_decision
        if preflight.r1a_hit:
            hit["artifact_dir"] = preflight.r1a_artifact_dir
        return hit

    write_cache_miss_receipt(art, preflight, evidence)

    result = run_integrated_single_action_spine(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=art,
        route_family=DRAFT_LEG_ROUTE_FAMILY,
        cache_preflight_evidence=evidence,
    )
    from apps_rg.runtime.orchestration.canonical_dispatch import (
        _augment_integrated_manifest_with_apps_rg_docx,
        _augment_r4_run_manifest_for_apps_rg_l2_fault,
    )

    _augment_integrated_manifest_with_apps_rg_docx(art)
    _augment_r4_run_manifest_for_apps_rg_l2_fault(
        art,
        fault=result.fault,
        x3_disposition=result.x3_disposition,
    )
    _augment_r4_manifest_draft_leg_only(
        art,
        spine_manifest_ref=sr.FILENAME_SPINE_MANIFEST,
    )

    rid = str(getattr(result, "run_id", "") or "").strip()
    emit_integrated_run_bundle_index(repo, art, run_id=rid or None, correlation_id=rid or None)
    maybe_ingest_r1b_post_exit(raw_request=raw_request, artifact_dir=art, runs_dir=art.parent)

    review_zip = None
    section_status_md: str | None = None
    if is_integrated_whole_run_dir_name(art.name):
        try:
            from apps_rg.runtime.full_run_section_status import emit_full_run_section_status

            status_emit = emit_full_run_section_status(art, repo_root=repo, print_stdout=False)
            section_status_md = str(status_emit["markdown_path"])
        except OSError:
            section_status_md = None
        try:
            review_zip = emit_full_resume_review_bundle(art)
        except OSError:
            review_zip = None

    outcome = result.fault == "" and result.x3_disposition in _SUCCESS_X3
    aggregate_x3 = _aggregate_x3_for_outcome(result.x3_disposition, outcome=outcome)
    payload: dict[str, Any] = {
        "exit_status": "success" if outcome else "error",
        "execution_status": "completed" if outcome else "failed",
        "outcome_authorized": outcome,
        "x3_disposition": aggregate_x3,
        "fault": result.fault,
        "artifact_dir": str(art),
        "run_id": result.run_id,
        "request_id": result.request_id,
        "route_family": route.route_family,
        "draft_leg_route_family": DRAFT_LEG_ROUTE_FAMILY,
        "spine_run_manifest": str(art / sr.FILENAME_SPINE_MANIFEST),
        "route_decision": route_decision,
        "research_delegation_executed": research_ran,
        "l7_how_trace_emitted": bool(result.fault == "" and (art / "agentic_core_how_trace.json").is_file()),
        "terminal_r5": result.terminal_r5,
    }
    if research_ran:
        payload["delegated_briefing"] = str(art / sr.FILENAME_DELEGATED_BRIEFING)
        payload["research_bridge_response"] = str(art / sr.FILENAME_RESEARCH_BRIDGE_RESPONSE)
    if review_zip is not None:
        payload["review_bundle_zip"] = str(review_zip)
        payload["review_bundle_relpath"] = REVIEW_BUNDLE_FILENAME
    if section_status_md is not None:
        payload["full_run_section_status_md"] = section_status_md
    return payload


__all__ = [
    "ROUTE_FAMILY_R3R4",
    "briefing_input_present",
    "research_delegation_enabled",
    "run_whole_run_with_route_governance",
    "should_delegate_apps_research",
]
