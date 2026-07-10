"""Whole-run CLI: U0→L1→L0 route governance + optional R3R4 apps_research → R4 draft leg."""
from __future__ import annotations

import dataclasses
import json
import os
import shutil
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.prerequisites.briefing_validator import validate_apps_research_handoff
from apps_rg.runtime.bindings.briefing_mode_classifier import classify_briefing_mode
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.u0_binding import u0_validate_apps_rg
from apps_rg.runtime.dispatch import spine_stage_receipts as sr
from apps_rg.runtime.executive_summary_certification import (
    EXECUTIVE_SUMMARY_JUDGE_REVIEW_X3,
    executive_summary_certification_block,
)
from apps_rg.runtime.full_resume_review_bundle import (
    REVIEW_BUNDLE_FILENAME,
    emit_full_resume_review_bundle,
)
from apps_rg.runtime.orchestration.integrated_spine_runner import (
    run_integrated_single_action_spine,
)
from apps_rg.runtime.run_bundle_index import emit_integrated_run_bundle_index
from apps_rg.runtime.runtime_proof_layout import (
    allocate_full_resume_artifact_dir,
    find_repo_root,
    is_integrated_whole_run_artifact_dir,
)

ROUTE_FAMILY_R3R4 = "R3R4_MANAGED_WORKFLOW"
DRAFT_LEG_ROUTE_FAMILY = "R4_SINGLE_ACTION"
_SUCCESS_X3 = frozenset({"X3C", "X3D", "EXIT_OK", "EXIT_PARTIAL"})


def _aggregate_x3_for_outcome(raw_x3: str | None, *, outcome: bool) -> str:
    """Preserve the source X3 decision; completion status carries later failures."""
    del outcome
    return str(raw_x3 or "")


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
    _ = research_via
    return bool(auto_research_internal)


def briefing_input_present(manual_brief: str) -> bool:
    return bool(_read_optional_brief(manual_brief).strip())


def apps_research_handoff_authorized(manual_brief: str, *, jd_ref: str = "") -> bool:
    validation = validate_apps_research_handoff(
        brief_ref=manual_brief,
        jd_ref=jd_ref,
        require_observed=True,
        require_x1_x3_authorization=True,
    )
    return bool(validation.valid)


def should_delegate_apps_research(
    *,
    route_family: str,
    manual_brief: str,
    auto_research_internal: bool,
    research_via: str | None,
    jd_ref: str = "",
) -> bool:
    if route_family != ROUTE_FAMILY_R3R4:
        return False
    if not research_delegation_enabled(
        auto_research_internal=auto_research_internal,
        research_via=research_via,
    ):
        return False
    if not briefing_input_present(manual_brief):
        return True
    return not apps_research_handoff_authorized(manual_brief, jd_ref=jd_ref)


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
    # G23 (plan apps-rg-e2e-gap-remediation-7e2d9c): the CLI ``--jd`` value arrives as ``jd`` but was
    # never written into app_payload, so U0 fell back to DEFAULT_SSOT generic targeting and the resume
    # ignored the job description. Map it into the canonical fields when an explicit ref/text was not
    # supplied: an existing path becomes job_description_ref; inline text becomes job_description_text.
    jd_cli = str(jd or "").strip()
    if jd_cli and not str(job_description_ref or "").strip() and not str(job_description_text or "").strip():
        try:
            _jd_is_path = Path(jd_cli).expanduser().exists()
        except OSError:
            _jd_is_path = False
        if _jd_is_path:
            job_description_ref = jd_cli
        else:
            job_description_text = jd_cli
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


def _pre_u0_research_route(envelope: Any) -> SimpleNamespace:
    """Stable delegation identity used only to dispatch apps_research before U0."""
    return SimpleNamespace(
        route_id=ROUTE_FAMILY_R3R4,
        route_family=ROUTE_FAMILY_R3R4,
        execution_form="MANAGED_WORKFLOW",
        l3_required=True,
        grounding_required=True,
        route_profile_ref="pre_u0_research_delegation.v1",
        reason_codes=("PRE_U0_APPS_RESEARCH_DELEGATION",),
        request_id=str(envelope.request_id),
        run_id=str(envelope.run_id),
        trace_id=str(envelope.trace_id),
    )


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
    job_description_ref: str = "",
    job_description_text: str = "",
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
        job_description_ref=job_description_ref,
        job_description_text=job_description_text,
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
        producer_run_dir = Path(str(outcome.research_artifact_dir or ""))
        producer_briefing = Path(str(outcome.research_briefing_path or ""))
        if (
            not producer_run_dir.is_dir()
            or not producer_briefing.is_file()
            or not producer_briefing.resolve().is_relative_to(producer_run_dir.resolve())
        ):
            sr.write_stage_receipt(
                artifact_dir / sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
                {
                    "outcome": "ResearchDispatchFailure",
                    "r5_reason_code": "APPS_RESEARCH_ARTIFACT_MISSING",
                    "detail": "ResumeBriefingReady lacked producer-owned persisted briefing evidence",
                    "research_artifact_dir": str(outcome.research_artifact_dir or ""),
                    "research_briefing_path": str(outcome.research_briefing_path or ""),
                },
            )
            return False, "APPS_RESEARCH_ARTIFACT_MISSING", ""
        sr.write_stage_receipt(
            artifact_dir / sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
            {
                "outcome": "ResumeBriefingReady",
                "research_run_id": outcome.research_run_id,
                "research_evidence_count": outcome.research_evidence_count,
                "confidence_score": outcome.confidence_score,
                "evidence_lineage": list(outcome.evidence_lineage),
                "research_artifact_dir": outcome.research_artifact_dir,
                "research_briefing_path": outcome.research_briefing_path,
                "apps_research_handoff_envelope": outcome.apps_research_handoff_envelope,
            },
        )
        brief_path = artifact_dir / sr.FILENAME_DELEGATED_BRIEFING
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(producer_briefing, brief_path)
        handoff_envelope = dict(outcome.apps_research_handoff_envelope)
        handoff_envelope["consumer_delegated_briefing_path"] = str(
            brief_path.resolve()
        )
        sr.write_stage_receipt(
            brief_path.parent / "apps_research_briefing_envelope.json",
            handoff_envelope,
        )
        fec_path = artifact_dir / sr.FILENAME_RESEARCH_EVIDENCE_CONTRACT
        sr.write_stage_receipt(
            fec_path,
            {
                "schema_version": "apps_rg.research_fec_stub.v1",
                "research_run_id": outcome.research_run_id,
                "result_hash": outcome.result_hash,
                "evidence_lineage": list(outcome.evidence_lineage),
                "confidence_score": outcome.confidence_score,
                "apps_research_handoff_envelope": handoff_envelope,
                "proof_note": "FEC-shaped contract for external review; full FEC lives under apps_research run when present.",
            },
        )
        sr.write_stage_receipt(
            artifact_dir / "research" / "research_artifact_ref.json",
            {
                "research_run_id": outcome.research_run_id,
                "research_artifact_dir": str(producer_run_dir.resolve()),
                "research_briefing_path": str(producer_briefing.resolve()),
                "research_company_brief_path": handoff_envelope.get(
                    "company_brief_path", ""
                ),
                "research_envelope_path": str(
                    (producer_run_dir / "apps_research_briefing_envelope.json").resolve()
                ),
                "consumer_delegated_briefing_path": str(brief_path.resolve()),
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
        "route_family": route.route_family,
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
        "route_family": route.route_family,
        "spine_run_manifest": str(artifact_dir / sr.FILENAME_SPINE_MANIFEST),
        "research_note": reason,
    }


def _emit_terminal_mandatory_closeout(
    *,
    artifact_dir: Path,
    repo_root: Path,
    payload: dict[str, Any],
    final_resume_outputs_pre_emitted: bool = False,
) -> dict[str, Any]:
    """Emit and enforce every mandatory terminal artifact for any E2E outcome."""
    from apps_rg.runtime.mandatory_run_outputs import (
        MANDATORY_OUTPUT_HARD_STOP_GATE_ID,
        emit_mandatory_run_outputs,
    )
    from apps_rg.runtime.section_failure_forensics import (
        E2E_SECTION_FORENSICS_GATE_ID,
    )

    try:
        mandatory_emit = emit_mandatory_run_outputs(
            artifact_dir,
            repo_root=repo_root,
            result=payload,
            print_stdout=False,
            emit_final_outputs=not final_resume_outputs_pre_emitted,
        )
    except OSError as exc:
        prior_fault = str(payload.get("fault") or "")
        payload.update(
            {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "completion_status": "BLOCKED",
                "fault": prior_fault or MANDATORY_OUTPUT_HARD_STOP_GATE_ID,
                "completion_fault": MANDATORY_OUTPUT_HARD_STOP_GATE_ID,
                "mandatory_output_upstream_fault": prior_fault,
                "mandatory_output_emit_error": str(exc),
            }
        )
        return payload

    payload.update(
        {
            "mandatory_run_output_json": str(mandatory_emit["json_path"]),
            "mandatory_run_output_md": str(mandatory_emit["markdown_path"]),
            "bcg_executive_output_md": str(mandatory_emit["bcg_markdown_path"]),
        }
    )
    emitted_payload = (
        mandatory_emit.get("payload") if isinstance(mandatory_emit, dict) else {}
    )
    forensics_gate = (
        emitted_payload.get("section_failure_forensics")
        if isinstance(emitted_payload, dict)
        and isinstance(emitted_payload.get("section_failure_forensics"), dict)
        else {}
    )
    if forensics_gate.get("required") and not bool(forensics_gate.get("pass")):
        prior_fault = str(payload.get("fault") or "")
        payload.update(
            {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "completion_status": "BLOCKED",
                "fault": prior_fault or E2E_SECTION_FORENSICS_GATE_ID,
                "completion_fault": E2E_SECTION_FORENSICS_GATE_ID,
                "section_failure_forensics_gate": forensics_gate,
                "mandatory_output_upstream_fault": prior_fault,
            }
        )
    mandatory_gate = (
        mandatory_emit.get("mandatory_output_gate")
        if isinstance(mandatory_emit, dict)
        and isinstance(mandatory_emit.get("mandatory_output_gate"), dict)
        else {}
    )
    if mandatory_gate.get("required") and not bool(mandatory_gate.get("pass")):
        prior_fault = str(payload.get("fault") or "")
        payload.update(
            {
                "exit_status": "error",
                "execution_status": "failed",
                "outcome_authorized": False,
                "completion_status": "BLOCKED",
                "fault": prior_fault or (
                    E2E_SECTION_FORENSICS_GATE_ID
                    if not bool(forensics_gate.get("pass", True))
                    else MANDATORY_OUTPUT_HARD_STOP_GATE_ID
                ),
                "completion_fault": (
                    E2E_SECTION_FORENSICS_GATE_ID
                    if not bool(forensics_gate.get("pass", True))
                    else MANDATORY_OUTPUT_HARD_STOP_GATE_ID
                ),
                "mandatory_output_hard_stop": mandatory_gate,
                "mandatory_output_upstream_fault": prior_fault,
            }
        )
    return payload


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
    from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger

    stage_ledger = E2EStageLedger.create(
        artifact_dir=art,
        e2e_run_id=str(envelope.run_id),
    )
    handoff_jd_ref = (
        str(job_description_ref or "").strip()
        or str(jd or "").strip()
        or str(job_description_text or "").strip()
    )
    initial_handoff_validation = validate_apps_research_handoff(
        brief_ref=manual_brief,
        jd_ref=handoff_jd_ref,
        require_observed=research_delegation_enabled(
            auto_research_internal=auto_research_internal,
            research_via=research_via,
        )
        and briefing_input_present(manual_brief),
        require_x1_x3_authorization=research_delegation_enabled(
            auto_research_internal=auto_research_internal,
            research_via=research_via,
        )
        and briefing_input_present(manual_brief),
    )
    manual_brief_eff = manual_brief
    research_ran = False
    research_note = ""
    delegated_briefing_ref: str | None = None
    research_enabled = research_delegation_enabled(
        auto_research_internal=auto_research_internal,
        research_via=research_via,
    )
    should_delegate_pre_u0 = research_enabled and not (
        initial_handoff_validation.observed and initial_handoff_validation.valid
    )
    if should_delegate_pre_u0:
        delegation_route = _pre_u0_research_route(envelope)
        ok, research_note, brief_path = _run_r3r4_research_hop(
            route=delegation_route,
            validated_request=envelope,
            artifact_dir=art,
            target_company=target_company,
            target_role=target_role,
            job_description_ref=str(job_description_ref or jd or "").strip(),
            job_description_text=job_description_text,
        )
        research_ran = True
        if not ok:
            stage_ledger.record(
                stage_id="RESEARCH",
                status="FAIL",
                reason_code=research_note,
                output_refs={
                    "research_bridge_response": sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
                },
            )
            route_decision = {
                "route_profile_ref": delegation_route.route_profile_ref,
                "route_family": delegation_route.route_family,
                "route_id": delegation_route.route_id,
                "execution_form": delegation_route.execution_form,
                "research_delegation_enabled": True,
                "research_delegation_executed": True,
                "research_outcome": research_note,
                "research_failure": research_note,
                "research_failure_reason": "apps_research_hop_failed_without_authorized_handoff",
            }
            failed = _failure_payload(
                artifact_dir=art,
                route=delegation_route,
                reason=research_note,
                route_decision=route_decision,
            )
            failed["completion_status"] = "BLOCKED"
            _emit_terminal_mandatory_closeout(
                artifact_dir=art,
                repo_root=repo,
                payload=failed,
            )
            stage_ledger.record(
                stage_id="CLOSEOUT",
                status="PASS",
                reason_code="FAILED_RUN_REPORTED",
                output_refs={"spine_run_manifest": sr.FILENAME_SPINE_MANIFEST},
            )
            failed["e2e_stage_ledger"] = str(stage_ledger.path)
            return failed
        manual_brief_eff = brief_path
        delegated_briefing_ref = sr.FILENAME_DELEGATED_BRIEFING
        stage_ledger.record(
            stage_id="RESEARCH",
            status="PASS",
            reason_code=research_note,
            output_refs={
                "research_bridge_response": sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
                "delegated_briefing": sr.FILENAME_DELEGATED_BRIEFING,
            },
        )
    else:
        research_note = (
            "AUTHORIZED_HANDOFF_REUSED"
            if initial_handoff_validation.observed and initial_handoff_validation.valid
            else "RESEARCH_DISABLED"
        )
        stage_ledger.record(
            stage_id="RESEARCH",
            status="SKIPPED",
            reason_code=research_note,
            input_refs={"manual_brief": str(manual_brief or "")},
        )

    envelope.app_payload["manual_brief_path"] = manual_brief_eff
    envelope.app_payload["briefing_artifact_ref"] = manual_brief_eff
    from apps_rg.runtime.bindings.u0_rejection import AppsRgU0RejectedError

    try:
        validated_request = u0_validate_apps_rg(
            envelope,
            allow_missing_profiles=False,
        )
    except AppsRgU0RejectedError as exc:
        reason = f"U0_REJECTED:{exc.notice.rejection_reason.value}"
        stage_ledger.record(
            stage_id="U0",
            status="FAIL",
            reason_code=reason,
            output_refs={
                "rejection_detail": dict(exc.notice.machine_readable_detail or {})
            },
        )
        rejection_route = _pre_u0_research_route(envelope)
        route_decision = {
            "route_profile_ref": rejection_route.route_profile_ref,
            "route_family": rejection_route.route_family,
            "route_id": rejection_route.route_id,
            "execution_form": rejection_route.execution_form,
            "research_delegation_enabled": research_enabled,
            "research_delegation_executed": research_ran,
            "research_outcome": research_note,
            "u0_rejection_reason": exc.notice.rejection_reason.value,
        }
        failed = _failure_payload(
            artifact_dir=art,
            route=rejection_route,
            reason=reason,
            route_decision=route_decision,
        )
        failed["completion_status"] = "BLOCKED"
        _emit_terminal_mandatory_closeout(
            artifact_dir=art,
            repo_root=repo,
            payload=failed,
        )
        stage_ledger.record(
            stage_id="CLOSEOUT",
            status="FAIL",
            reason_code=str(failed.get("completion_fault") or reason),
            output_refs={
                "mandatory_run_output_json": str(
                    failed.get("mandatory_run_output_json") or ""
                )
            },
        )
        failed["e2e_stage_ledger"] = str(stage_ledger.path)
        return failed
    stage_ledger.record(
        stage_id="U0",
        status="PASS",
        output_refs={"u0_receipt": sr.FILENAME_U0_RECEIPT},
    )
    l1_plan = l1_plan_apps_rg(validated_request)
    stage_ledger.record(
        stage_id="L1",
        status="PASS",
        output_refs={"l1_plan": sr.FILENAME_L1_PLAN},
    )
    route = l0_route_apps_rg(l1_plan)
    stage_ledger.record(
        stage_id="L0",
        status="PASS",
        output_refs={"route_contract": sr.FILENAME_ROUTE_CONTRACT},
    )

    briefing_mode = classify_briefing_mode(
        validated_request.app_payload or {},
        chroma_path_resolved=None,
        research_via="apps_research" if research_ran else research_via,
    )
    handoff_validation = validate_apps_research_handoff(
        brief_ref=manual_brief_eff,
        jd_ref=handoff_jd_ref,
        require_observed=research_enabled and briefing_input_present(manual_brief_eff),
        require_x1_x3_authorization=research_enabled and briefing_input_present(manual_brief_eff),
    )
    route_decision = {
        "route_profile_ref": route.route_profile_ref,
        "route_family": route.route_family,
        "route_id": route.route_id,
        "execution_form": route.execution_form,
        "briefing_mode": briefing_mode.retrieval_mode,
        "briefing_classified_from": briefing_mode.classified_from,
        "research_delegation_enabled": research_enabled,
        "briefing_input_present": briefing_input_present(manual_brief_eff),
        "incoming_apps_research_handoff_authorized": (
            handoff_validation.observed and handoff_validation.valid
        ),
        "incoming_apps_research_handoff_reason": handoff_validation.reason,
        "incoming_apps_research_handoff_observed": handoff_validation.observed,
        "research_delegation_executed": research_ran,
        "research_outcome": research_note,
    }
    if research_ran:
        route_decision["delegated_briefing_path"] = manual_brief_eff
    if research_ran and route.route_family != ROUTE_FAMILY_R3R4:
        reason = "APPS_RESEARCH_ROUTE_MISMATCH"
        route_decision["research_failure"] = reason
        route_decision["research_failure_reason"] = (
            f"apps_research_completed_before_non_managed_route_{route.route_family}"
        )
        failed = _failure_payload(
            artifact_dir=art,
            route=route,
            reason=reason,
            route_decision=route_decision,
        )
        failed["completion_status"] = "BLOCKED"
        _emit_terminal_mandatory_closeout(
            artifact_dir=art,
            repo_root=repo,
            payload=failed,
        )
        stage_ledger.record(
            stage_id="CLOSEOUT",
            status="PASS",
            reason_code="FAILED_RUN_REPORTED",
            output_refs={"spine_run_manifest": sr.FILENAME_SPINE_MANIFEST},
        )
        failed["e2e_stage_ledger"] = str(stage_ledger.path)
        return failed

    sr.write_stage_receipt(
        art / sr.FILENAME_INGRESS_RAW,
        {
            "target_company": target_company,
            "target_role": target_role,
            "generation_mode": generation_mode,
            "manual_brief": manual_brief_eff,
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
            "delegated_briefing": delegated_briefing_ref,
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

    from apps_rg.cache.cache_preflight_evidence import (
        build_cache_preflight_evidence,
        write_cache_hit_receipt,
        write_cache_miss_receipt,
        write_whole_run_cache_preflight_artifact,
    )
    from apps_rg.cache.whole_run_entrypoint_preflight import (
        ENTRYPOINT_CANONICAL_DISPATCH,
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
        section="",
    )
    evidence = build_cache_preflight_evidence(preflight, artifact_dir=art)
    write_whole_run_cache_preflight_artifact(art, preflight, evidence)

    if not preflight.generation_required:
        write_cache_hit_receipt(art, preflight, evidence)
        r1b_result = preflight.r1b_result
        cache_candidate_dir = str(preflight.r1a_artifact_dir or "").strip()
        if not cache_candidate_dir and r1b_result is not None:
            cache_candidate_dir = str(
                getattr(r1b_result, "artifact_dir", "")
                or getattr(r1b_result, "run_dir", "")
                or ""
            ).strip()
        from apps_rg.runtime.e2e_stage_ledger import validate_cached_e2e_completion

        cache_completion = validate_cached_e2e_completion(
            Path(cache_candidate_dir)
            if cache_candidate_dir
            else art / "__missing_cache_candidate__"
        )
        failed = _failure_payload(
            artifact_dir=art,
            route=route,
            reason="E2E_FRESH_RUN_REQUIRES_CACHE_MISS",
            route_decision=route_decision,
        )
        failed.update(
            {
                "completion_status": "BLOCKED",
                "cache_preflight": evidence,
                "cache_candidate_dir": cache_candidate_dir,
                "cache_candidate_completion_valid": cache_completion.valid,
                "cache_candidate_completion_errors": list(cache_completion.errors),
            }
        )
        _emit_terminal_mandatory_closeout(
            artifact_dir=art,
            repo_root=repo,
            payload=failed,
        )
        stage_ledger.record(
            stage_id="CLOSEOUT",
            status="FAIL",
            reason_code="E2E_FRESH_RUN_REQUIRES_CACHE_MISS",
            output_refs={
                "mandatory_run_output_json": str(
                    failed.get("mandatory_run_output_json") or ""
                )
            },
        )
        failed["e2e_stage_ledger"] = str(stage_ledger.path)
        return failed

    write_cache_miss_receipt(art, preflight, evidence)

    result = run_integrated_single_action_spine(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=art,
        route_family=DRAFT_LEG_ROUTE_FAMILY,
        cache_preflight_evidence=evidence,
        front_continuation={
            "validated_request": validated_request,
            "plan_contract": l1_plan,
            "route_contract": route,
            "execution_route_id": DRAFT_LEG_ROUTE_FAMILY,
        },
    )
    execution_witness = dict(getattr(result, "execution_witness", {}) or {})
    stage_ledger.record(
        stage_id="C0",
        status="PASS",
        reason_code=str(
            (execution_witness.get("c0") or {}).get("status")
            if isinstance(execution_witness.get("c0"), dict)
            else "CORE_C0_RECEIPT_EMITTED"
        ),
        output_refs={"runtime_execution_witness": "runtime_execution_witness.json"},
    )
    if result.fault:
        stage_ledger.record(
            stage_id="L2",
            status="FAIL",
            reason_code=str(result.fault),
            output_refs={"terminal_ret_packet": "terminal_ret_packet.json"},
        )
    else:
        stage_ledger.record(
            stage_id="L2",
            status="PASS",
            output_refs={"terminal_ret_packet": "terminal_ret_packet.json"},
        )
        stage_ledger.record(
            stage_id="X1",
            status="PASS",
            output_refs={"exit_review_packet": "exit_review_packet.json"},
        )
        stage_ledger.record(
            stage_id="X2",
            status="PASS",
            reason_code=str(
                (execution_witness.get("x2") or {}).get("disposition")
                if isinstance(execution_witness.get("x2"), dict)
                else "EXIT_X2_AGGREGATED"
            ),
            output_refs={"runtime_execution_witness": "runtime_execution_witness.json"},
        )
        stage_ledger.record(
            stage_id="X3",
            status="PASS",
            reason_code=str(result.x3_disposition),
            output_refs={"x3_disposition_receipt": "x3_disposition_receipt.json"},
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
    final_resume_outputs_pre_emitted = False
    if result.fault == "":
        from apps_rg.runtime.final_resume_outputs import emit_final_resume_product_outputs

        emit_final_resume_product_outputs(art, repo_root=repo, required=True)
        final_resume_outputs_pre_emitted = True
        stage_ledger.record(
            stage_id="CANDIDATE",
            status="PASS",
            output_refs={"apps_rg_output_manifest": "apps_rg_output_manifest.json"},
        )

    section_status_md: str | None = None
    if is_integrated_whole_run_artifact_dir(art):
        try:
            from apps_rg.runtime.full_run_section_status import emit_full_run_section_status

            status_emit = emit_full_run_section_status(art, repo_root=repo, print_stdout=False)
            section_status_md = str(status_emit["markdown_path"])
        except OSError:
            section_status_md = None

    exec_summary_block = executive_summary_certification_block(art)
    exec_summary_blocked = bool(exec_summary_block.get("blocked"))
    effective_x3 = (
        str(exec_summary_block.get("x3_disposition") or EXECUTIVE_SUMMARY_JUDGE_REVIEW_X3)
        if exec_summary_blocked
        else result.x3_disposition
    )
    outcome = (
        result.fault == ""
        and not exec_summary_blocked
        and effective_x3 in _SUCCESS_X3
    )
    post_x3_completion: dict[str, Any] = {}
    result_fault = result.fault
    if outcome:
        from apps_rg.runtime.post_x3_completion import complete_apps_rg_post_x3

        post_x3_completion = complete_apps_rg_post_x3(
            artifact_dir=art,
            result={
                "exit_status": "success",
                "execution_status": "completed",
                "outcome_authorized": True,
                "x3_disposition": result.x3_disposition,
                "completion_disposition": effective_x3,
                "fault": result.fault,
                "artifact_dir": str(art),
                "run_id": result.run_id,
                "request_id": result.request_id,
            },
            raw_request=raw_request,
        )
        if not (
            post_x3_completion.get("completed")
            and post_x3_completion.get("x3_to_uwg_to_eval_to_l6_completed")
        ):
            outcome = False
            result_fault = str(
                post_x3_completion.get("failure_stage")
                or "post_x3_completion"
            )
    if final_resume_outputs_pre_emitted:
        apps_eval_completion = (
            post_x3_completion.get("apps_eval")
            if isinstance(post_x3_completion.get("apps_eval"), dict)
            else {}
        )
        coverage = (
            apps_eval_completion.get("coverage_summary")
            if isinstance(apps_eval_completion.get("coverage_summary"), dict)
            else {}
        )
        eval_pass = bool(
            coverage.get("release_blocked") is False
            and coverage.get("coverage_complete") is True
        )
        if not post_x3_completion:
            stage_ledger.record(
                stage_id="APPS_EVAL",
                status="BLOCKED",
                reason_code="X3_OR_EXECUTIVE_SUMMARY_NOT_AUTHORIZED",
            )
        elif not eval_pass:
            stage_ledger.record(
                stage_id="APPS_EVAL",
                status="FAIL",
                reason_code=str(
                    post_x3_completion.get("failure_stage") or "APPS_EVAL_FAILED"
                ),
                output_refs={
                    "eval_record": str(apps_eval_completion.get("eval_record_ref") or "")
                },
            )
        else:
            stage_ledger.record(
                stage_id="APPS_EVAL",
                status="PASS",
                output_refs={
                    "eval_record": str(apps_eval_completion.get("eval_record_ref") or "")
                },
            )
            l6_completion = (
                post_x3_completion.get("l6_shadow")
                if isinstance(post_x3_completion.get("l6_shadow"), dict)
                else {}
            )
            l6_pass = bool(
                l6_completion.get("l6_shadow_bridge_ref")
                and l6_completion.get("grain_parity_status") == "PASS"
                and l6_completion.get("apps_eval_rows_bound") is True
            )
            stage_ledger.record(
                stage_id="L6_SHADOW",
                status="PASS" if l6_pass else "FAIL",
                reason_code="L6_APPS_EVAL_BOUND" if l6_pass else "L6_CLOSURE_INCOMPLETE",
                output_refs={
                    "l6_shadow_bridge": str(
                        l6_completion.get("l6_shadow_bridge_ref") or ""
                    )
                },
            )
            if l6_pass:
                promotion_pass = bool(
                    post_x3_completion.get("completed")
                    and post_x3_completion.get("durable_promotion_committed") is True
                    and (post_x3_completion.get("fact_vector_writeback") or {}).get(
                        "status"
                    )
                    != "FAIL"
                )
                stage_ledger.record(
                    stage_id="STATE_PROMOTION",
                    status="PASS" if promotion_pass else "FAIL",
                    reason_code=(
                        "DURABLE_PROMOTION_COMMITTED"
                        if promotion_pass
                        else str(
                            post_x3_completion.get("failure_stage")
                            or "DURABLE_PROMOTION_INCOMPLETE"
                        )
                    ),
                    output_refs={
                        "post_x3_completion": "apps_rg_post_x3_completion_receipt.json"
                    },
                )
    payload: dict[str, Any] = {
        "exit_status": "success" if outcome else "error",
        "execution_status": "completed" if outcome else "failed",
        "outcome_authorized": outcome,
        "x3_disposition": result.x3_disposition,
        "completion_disposition": effective_x3,
        "completion_status": "PASS" if outcome else "BLOCKED",
        "fault": result_fault,
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
        "executive_summary_certification_block": exec_summary_block,
        "post_x3_completion": post_x3_completion,
        "uwg_commit_receipt_ref": (
            (post_x3_completion.get("uwg") or {})
            .get("artifacts", {})
            .get("uwg_commit_receipt", "")
            if isinstance(post_x3_completion.get("uwg"), dict)
            else ""
        ),
        "apps_eval_record_ref": (
            (post_x3_completion.get("apps_eval") or {}).get("eval_record_ref", "")
            if isinstance(post_x3_completion.get("apps_eval"), dict)
            else ""
        ),
        "l6_shadow_bridge_ref": (
            (post_x3_completion.get("l6_shadow") or {}).get("l6_shadow_bridge_ref", "")
            if isinstance(post_x3_completion.get("l6_shadow"), dict)
            else ""
        ),
    }
    if research_ran:
        payload["delegated_briefing"] = str(art / sr.FILENAME_DELEGATED_BRIEFING)
        payload["research_bridge_response"] = str(art / sr.FILENAME_RESEARCH_BRIDGE_RESPONSE)
    _emit_terminal_mandatory_closeout(
        artifact_dir=art,
        repo_root=repo,
        payload=payload,
        final_resume_outputs_pre_emitted=final_resume_outputs_pre_emitted,
    )
    review_zip = None
    if is_integrated_whole_run_artifact_dir(art):
        try:
            review_zip = emit_full_resume_review_bundle(art)
        except OSError:
            review_zip = None
    if review_zip is not None:
        payload["review_bundle_zip"] = str(review_zip)
        payload["review_bundle_relpath"] = REVIEW_BUNDLE_FILENAME
    if section_status_md is not None:
        payload["full_run_section_status_md"] = section_status_md
    stage_ledger.record(
        stage_id="CLOSEOUT",
        status="PASS" if payload.get("outcome_authorized") is True else "FAIL",
        reason_code=(
            "MANDATORY_CLOSEOUT_COMPLETE"
            if payload.get("outcome_authorized") is True
            else str(payload.get("fault") or "RUN_NOT_AUTHORIZED")
        ),
        output_refs={
            "mandatory_run_output_json": str(
                payload.get("mandatory_run_output_json") or ""
            ),
            "bcg_executive_output_md": str(
                payload.get("bcg_executive_output_md") or ""
            ),
        },
    )
    from apps_rg.runtime.e2e_stage_ledger import verify_e2e_stage_ledger

    ledger_report = verify_e2e_stage_ledger(stage_ledger.path)
    payload["e2e_stage_ledger"] = str(stage_ledger.path)
    payload["e2e_stage_ledger_valid"] = ledger_report.valid
    payload["e2e_stage_ledger_complete"] = ledger_report.complete
    if payload.get("outcome_authorized") is True and not ledger_report.complete:
        payload["exit_status"] = "error"
        payload["execution_status"] = "failed"
        payload["outcome_authorized"] = False
        payload["completion_status"] = "BLOCKED"
        payload["fault"] = "E2E_STAGE_LEDGER_INCOMPLETE"
        payload["e2e_stage_ledger_errors"] = list(ledger_report.errors)
    return payload


__all__ = [
    "ROUTE_FAMILY_R3R4",
    "apps_research_handoff_authorized",
    "briefing_input_present",
    "research_delegation_enabled",
    "run_whole_run_with_route_governance",
    "should_delegate_apps_research",
]
