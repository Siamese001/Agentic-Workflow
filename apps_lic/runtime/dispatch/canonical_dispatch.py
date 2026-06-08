"""Canonical apps_lic product spine: U0 → L1 → L0 → C0 → PA → L3 → L2 → Exit.

No integrated_r4_lic shortcut, no GovernedLicRun, no YAML L2 recipe
resolver, no direct HOP bypass from CLI, and no apps_research managed
workflow support path. apps_research is deprecated for apps_lic; requests
that would have selected the old R3R4 research-then-draft route fail closed
instead of invoking any bridge, dispatcher, or support workflow.
"""

from __future__ import annotations

import dataclasses
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_lic.runtime.bindings.l0_binding import (
    ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
    ROUTE_FAMILY_R4_MANAGED_DRAFT,
    ROUTE_FAMILY_R5_FALLBACK,
    l0_route_apps_lic,
)
from apps_lic.runtime.bindings.l1_binding import l1_plan_apps_lic
from apps_lic.runtime.bindings.l2_binding import l2_execute_apps_lic
from apps_lic.runtime.bindings.l3_binding import l3_orchestrate_apps_lic
from apps_lic.runtime.bindings.pa_binding import pa_compose_apps_lic
from apps_lic.runtime.bindings.c0_binding import c0_retrieve_apps_lic
from apps_lic.runtime.bindings.exit_binding import exit_finalize_apps_lic
from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt

from apps_lic.runtime.dispatch.spine_run_result import SpineRunResult, x3_manifest_fields
from apps_lic.runtime.dispatch import stage_receipts as _sr
from apps_lic.runtime.dispatch.runtime_proof_bundle import (
    FILENAME_RUNTIME_PROOF_BUNDLE,
    write_runtime_proof_bundle,
)

ROUTE_FAMILY_R4 = ROUTE_FAMILY_R4_MANAGED_DRAFT
ROUTE_FAMILY_R3R4 = ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT  # deprecated guard only
ROUTE_FAMILY_R5 = ROUTE_FAMILY_R5_FALLBACK

_EXECUTION_MANAGED = "managed_workflow"
_EXECUTION_TERMINAL = "terminal_fallback"
_APPS_RESEARCH_DEPRECATED_REASON = "APPS_RESEARCH_DEPRECATED"

_DEFAULT_CAMPAIGN_OBJECTIVE = (
    "Start a concise recruiting conversation around relevant AI / agentic AI "
    "engineering leadership roles."
)


def _assert_runtime_proof_bundle_pass(artifact_dir: Path) -> None:
    path = artifact_dir / FILENAME_RUNTIME_PROOF_BUNDLE
    if not path.is_file():
        raise RuntimeError(f"runtime_proof_bundle_missing:{path}")
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if bundle.get("status") != "PASS":
        raise RuntimeError(
            f"runtime_proof_bundle_failed:{bundle.get('violations')}"
        )


def build_cli_ingress_raw(
    *,
    run_id: str | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
    recipient_class: str = "recruiter",
    channel: str = "linkedin",
    outreach_mode: str = "cold",
    manual_brief: str = "",
    allow_research: bool = False,
    lead_profile: Mapping[str, Any] | None = None,
    campaign_objective: str | None = None,
    audience_segment: str = "recruiting",
) -> dict[str, Any]:
    """Map CLI kwargs to AppsLicIngressContractV1-shaped raw JSON for U0.

    ``allow_research`` is accepted only for backward CLI compatibility. It no
    longer authorizes the deprecated apps_research managed workflow; the emitted
    payload marks research disabled by policy so L0 cannot select R3R4 through
    the normal profile interpreter.
    """
    rid = run_id or f"run_lic_{uuid.uuid4().hex[:12]}"
    req_id = request_id or f"req_lic_{uuid.uuid4().hex[:12]}"
    tid = trace_id or f"trace_lic_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    has_brief = bool(manual_brief.strip())

    normalized_channel = (channel or "linkedin").strip().lower() or "linkedin"
    normalized_outreach_mode = (outreach_mode or "cold").strip().lower() or "cold"
    normalized_recipient_class = (recipient_class or "recruiter").strip() or "recruiter"

    lead = dict(lead_profile) if lead_profile else {
        "verified_name": "Recruiter",
        "title": "Recruiter",
        "seniority_class": normalized_recipient_class.upper(),
        "company_name": "Unknown",
        "industry": "Recruiting",
        "consent_attested": True,
    }

    personalization_inputs: dict[str, Any] = {}
    if has_brief:
        personalization_inputs["manual_brief"] = manual_brief.strip()

    research_req: dict[str, Any] = {
        "allow_research": False,
        "research_disabled_by_policy": True,
        "deprecation_reason": _APPS_RESEARCH_DEPRECATED_REASON,
    }
    if allow_research and not has_brief:
        research_req["requested_but_disabled"] = True

    return {
        "apps_lic_contract_version": "v1",
        "transport": {
            "app_id": "apps_lic",
            "task_class": "outreach_message",
            "request_id": req_id,
            "run_id": rid,
            "tenant_id": "apps_lic",
            "trace_id": tid,
            "submitted_at": now,
        },
        "campaign": {
            "request_type": "linkedin_recruiter_outreach_draft",
            "campaign_objective": campaign_objective or _DEFAULT_CAMPAIGN_OBJECTIVE,
            "channel": normalized_channel,
            "audience_segment": audience_segment,
            "recipient_class": normalized_recipient_class,
            "outreach_mode": normalized_outreach_mode,
            "action_required": "draft_and_cert",
            "workflow_required": "managed_workflow_hop",
            "grounding_required": True,
            "side_effect_class": "read_only",
        },
        "forbidden_send_modes": {
            "modes": [
                "send_now",
                "auto_send",
                "connector_send",
                "email_outbox_send",
                "linkedin_send",
                "sms_send",
                "external_http_post",
            ],
        },
        "entity_refs": {
            "lead_profile": lead,
            "lead_ref": None,
            "sender_profile": {
                "sender_id": "sender_cli",
                "name": "Amit Ayer",
                "title": "Senior Agentic AI / AI Engineering Leader",
            },
            "sender_ref": None,
            "company_profile": None,
            "company_ref": None,
        },
        "personalization": {"inputs": personalization_inputs},
        "generation_hints": {},
        "tone_constraints": {},
        "output_format": {
            "format": "linkedin_message_json",
            "message_text_max_chars": 600,
            "subject_required": False,
        },
        "research_requirements": research_req,
        "routing_policy": {},
        "validation_policy": {},
        "gate_decision_policy": {"halt_on_validation_failure": True},
        "qa_report": {},
        "integration_target": None,
        "hitl_policy": {"bypass_hitl_freeze": False},
        "pii_policy": {
            "pii_detection_mode": "strict",
            "redact_on_warn": True,
            "fail_on_pii_detect": True,
        },
        "governance_shield": {"shield_required": True},
        "antipattern_policy": {"enabled": True},
        "source_lineage": {"source_lineage_required": True},
        "ab_test": {},
        "replay_audit": {
            "idempotency_key": f"idem_{rid}",
            "replay_refs": [],
            "audit_refs": [],
        },
        "runtime_customization_package": {
            "package_digest": (
                "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
            ),
        },
        "payload_digest": "",
    }


def _inject_context_signals(
    validated_request: Any,
    raw_ingress: Mapping[str, Any],
) -> Any:
    """Attach L0 routing context_signals to app_payload post-U0.

    Context is considered fresh only when the user supplied a manual/preloaded
    briefing in the ingress payload. Deprecated apps_research output is not
    produced or merged here.
    """
    merged = dict(validated_request.app_payload)
    inputs = (raw_ingress.get("personalization") or {}).get("inputs") or {}
    entity = merged.get("entity_refs") or {}
    lead = entity.get("lead_profile") or {}
    has_brief = bool(inputs.get("manual_brief") or inputs.get("managed_briefing"))
    merged["context_signals"] = {
        "briefing_fresh": has_brief,
        "lead_profile_valid": bool(lead.get("verified_name")),
        "context_grounded": has_brief,
    }
    return dataclasses.replace(validated_request, app_payload=merged)


def _write_terminal_manifest(
    *,
    artifact_dir: Path,
    artifacts: list[str],
    route_payload: Mapping[str, Any],
    request_id: str,
    run_id: str,
    trace_id: str,
    terminal_reason: str,
    exit_stage_policy: str,
    deprecated_route_family: str | None = None,
) -> None:
    stage_refs = _sr.standard_stage_receipt_refs(
        terminal_r5=True,
        c0_invoked=False,
        pa_invoked=False,
        l3_participated=False,
    )
    manifest = {
        **dict(route_payload),
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "route_family": ROUTE_FAMILY_R5,
        "execution_form": _EXECUTION_TERMINAL,
        "l3_required": False,
        "terminal_r5": True,
        "terminal_r5_reason": terminal_reason,
        "x3_disposition": "DENY",
        "exit_status": "failure",
        "outcome_authorized": False,
        "exit_stage_policy": exit_stage_policy,
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "deprecated_route_family": deprecated_route_family or "",
        "stage_receipt_refs": list(stage_refs),
    }
    manifest_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_SPINE_MANIFEST,
        manifest,
    )
    artifacts.append(manifest_path)
    proof_path = write_runtime_proof_bundle(
        artifact_dir,
        manifest,
        terminal_r5=True,
    )
    artifacts.append(proof_path)
    _assert_runtime_proof_bundle_pass(artifact_dir)


def run_canonical_apps_lic_spine(
    raw_ingress: dict[str, Any],
    *,
    artifact_root: Path | None = None,
    skip_r3r4_research: bool = False,
) -> SpineRunResult:
    """Execute the canonical AG-8 spine for one apps_lic ingress payload.

    ``skip_r3r4_research`` is retained for backward API compatibility only.
    The old R3R4/apps_research path is removed and never invoked.
    """
    _ = skip_r3r4_research

    validated_request, reflection = apps_lic_u0_adapt(raw_ingress)
    validated_request = _inject_context_signals(validated_request, raw_ingress)
    l1 = l1_plan_apps_lic(validated_request)
    route = l0_route_apps_lic(l1)

    run_id = route.run_id
    artifact_dir = artifact_root or (
        Path("artifacts") / "apps_lic" / "spine_convergence" / "runs" / run_id
    )
    artifacts: list[str] = []

    ingress_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_INGRESS_RAW,
        {
            "schema_version": _sr.STAGE_RECEIPT_SCHEMA_VERSION,
            "stage": "INGRESS",
            "request_id": validated_request.request_id,
            "run_id": validated_request.run_id,
            "trace_id": validated_request.trace_id,
            "digest": _sr._sha256_digest(raw_ingress),
            "artifact_ref": _sr.FILENAME_INGRESS_RAW,
            "upstream_receipt_refs": [],
            "downstream_receipt_refs": [_sr.FILENAME_U0_RECEIPT],
            "payload": {
                "ingress": raw_ingress,
                "reflection_keys": list(reflection.keys()) if isinstance(reflection, dict) else [],
            },
        },
    )
    artifacts.append(ingress_path)

    u0_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_U0_RECEIPT,
        _sr.build_u0_receipt(validated_request, reflection),
    )
    artifacts.append(u0_path)

    l1_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_L1_PLAN,
        _sr.build_l1_receipt(l1),
    )
    artifacts.append(l1_path)

    route_payload = {
        "route_id": route.route_id,
        "route_family": route.route_family,
        "execution_form": route.execution_form,
        "l3_required": route.l3_required,
        "reason_codes": list(route.reason_codes),
        "apps_research_invoked": False,
    }
    will_c0 = bool(l1.grounding_required)
    will_pa = bool(l1.model_generation_required and will_c0)
    route_downstream = (
        _sr.managed_workflow_downstream_refs(c0_invoked=will_c0, pa_invoked=will_pa)
        if route.execution_form == _EXECUTION_MANAGED
        else ()
    )
    route_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_ROUTE_CONTRACT,
        _sr.build_route_receipt(
            route,
            route_payload,
            downstream_receipt_refs=route_downstream,
        ),
    )
    artifacts.append(route_path)

    if route.route_family == ROUTE_FAMILY_R3R4:
        _write_terminal_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            request_id=route.request_id,
            run_id=route.run_id,
            trace_id=route.trace_id,
            terminal_reason=_APPS_RESEARCH_DEPRECATED_REASON,
            exit_stage_policy="deprecated_apps_research_route_fail_closed_no_exit_receipt",
            deprecated_route_family=route.route_family,
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=ROUTE_FAMILY_R5,
            execution_form=_EXECUTION_TERMINAL,
            x3_disposition="DENY",
            terminal_r5=True,
            terminal_r5_reason=_APPS_RESEARCH_DEPRECATED_REASON,
            artifact_dir=artifact_dir,
            artifacts=tuple(artifacts),
        )

    if route.execution_form == _EXECUTION_TERMINAL or route.route_family == ROUTE_FAMILY_R5:
        terminal_reason = "route_family=R5_FALLBACK"
        _write_terminal_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            request_id=route.request_id,
            run_id=route.run_id,
            trace_id=route.trace_id,
            terminal_reason=terminal_reason,
            exit_stage_policy="terminal_r5_short_circuit_no_exit_receipt",
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=route.route_family,
            execution_form=route.execution_form,
            x3_disposition="DENY",
            terminal_r5=True,
            terminal_r5_reason="R5_TERMINAL_FALLBACK",
            artifact_dir=artifact_dir,
            artifacts=tuple(artifacts),
        )

    c0_invoked = False
    pa_invoked = False
    fec = None
    prompt = None

    if l1.grounding_required:
        fec = c0_retrieve_apps_lic(route, validated_request)
        c0_invoked = True
        c0_path = _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_C0_FEC,
            _sr.build_c0_receipt(fec),
        )
        artifacts.append(c0_path)
        fec_summary_path = _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_FEC_SUMMARY,
            _sr.build_c0_summary(fec),
        )
        artifacts.append(fec_summary_path)

    if l1.model_generation_required and fec is not None:
        prompt = pa_compose_apps_lic(
            route=route,
            l1_plan=l1,
            fec=fec,
            validated_request=validated_request,
        )
        pa_invoked = True
        pa_path = _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_PA_RECEIPT,
            _sr.build_pa_receipt(prompt),
        )
        artifacts.append(pa_path)

    if route.execution_form != _EXECUTION_MANAGED:
        raise ValueError(
            f"canonical_dispatch: non-terminal route must be managed_workflow; "
            f"got {route.execution_form!r}"
        )
    if fec is None:
        raise ValueError(
            "canonical_dispatch: managed apps_lic route requires C0 FinalEvidenceContract; "
            "apps_research fallback is removed"
        )

    l3_receipt, step, _bus = l3_orchestrate_apps_lic(route, fec, prompt)
    l3_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_L3_WORKFLOW,
        _sr.build_l3_receipt(l3_receipt, step),
    )
    artifacts.append(l3_path)

    l2_artifact = l2_execute_apps_lic(route, fec, step, prompt)
    l2_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_L2_EXECUTION,
        _sr.build_l2_receipt(l2_artifact),
    )
    artifacts.append(l2_path)

    x3 = exit_finalize_apps_lic(l2_artifact)

    l2_status = getattr(l2_artifact, "execution_status", "") or ""
    x3_str, x3_exit_status, x3_outcome_authorized = x3_manifest_fields(x3)

    exit_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_EXIT_DISPOSITION,
        _sr.build_exit_receipt(
            x3,
            x3_disposition=x3_str,
            exit_status=x3_exit_status,
            outcome_authorized=x3_outcome_authorized,
        ),
    )
    artifacts.append(exit_path)

    stage_refs = _sr.standard_stage_receipt_refs(
        terminal_r5=False,
        c0_invoked=c0_invoked,
        pa_invoked=pa_invoked,
        l3_participated=True,
    )
    manifest = {
        **route_payload,
        "request_id": route.request_id,
        "run_id": route.run_id,
        "trace_id": route.trace_id,
        "terminal_r5": False,
        "x3_disposition": x3_str,
        "exit_status": x3_exit_status,
        "outcome_authorized": x3_outcome_authorized,
        "l3_participated": True,
        "c0_invoked": c0_invoked,
        "pa_invoked": pa_invoked,
        "l2_execution_status": l2_status,
        "l3_receipt_id": getattr(l3_receipt, "deterministic_digest", "")[:32],
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "stage_receipt_refs": list(stage_refs),
    }
    manifest_path = _sr.write_stage_receipt(artifact_dir / _sr.FILENAME_SPINE_MANIFEST, manifest)
    artifacts.append(manifest_path)
    proof_path = write_runtime_proof_bundle(
        artifact_dir,
        manifest,
        terminal_r5=False,
    )
    artifacts.append(proof_path)
    _assert_runtime_proof_bundle_pass(artifact_dir)

    return SpineRunResult(
        run_id=run_id,
        request_id=route.request_id,
        trace_id=route.trace_id,
        route_id=route.route_id,
        route_family=route.route_family,
        execution_form=route.execution_form,
        x3_disposition=x3_str,
        terminal_r5=False,
        terminal_r5_reason="",
        artifact_dir=artifact_dir,
        l3_participated=True,
        c0_invoked=c0_invoked,
        pa_invoked=pa_invoked,
        l2_execution_status=l2_status,
        exit_status=x3_exit_status,
        outcome_authorized=x3_outcome_authorized,
        artifacts=tuple(artifacts),
    )
