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
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

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
from apps_lic.runtime.bindings.c0_binding import (
    C0_READY,
    C0_READINESS_INPUT_KEY,
    c0_blocking_status_from_fec,
    c0_readiness_status_from_fec,
    c0_ready_for_pa,
    c0_recipient_class_confidence_from_fec,
    c0_recipient_class_status_from_fec,
    c0_recipient_class_value_from_fec,
    c0_retrieve_apps_lic,
)
from apps_lic.runtime.bindings.c03_binding import (
    build_c03_sender_proof_for_pa,
    c03_ready_for_pa,
)
from apps_lic.runtime.bindings.c03_postgen_binding import (
    c03_postgen_claims_pass,
    validate_l2_c03_postgen_claims,
)
from apps_lic.runtime.bindings.w4_candidate_batch_binding import (
    materialize_w4_candidate_batch,
    w4_candidate_batch_ready,
)
from apps_lic.runtime.bindings.w5_validation_exit_binding import (
    materialize_w5_validation_exit,
    w5_validation_exit_clear,
)
from apps_lic.runtime.bindings.exit_binding import (
    exit_finalize_apps_lic,
    terminal_r5_exit_disposition_apps_lic,
)
from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt

from apps_lic.runtime.dispatch.canonical_manifest_fields import (
    w4_manifest_fields as _w4_manifest_fields,
    w5_manifest_fields as _w5_manifest_fields,
)
from apps_lic.runtime.dispatch.spine_run_result import SpineRunResult, x3_manifest_fields
from apps_lic.runtime.dispatch import stage_receipts as _sr
from apps_lic.runtime.dispatch.runtime_proof_bundle import (
    FILENAME_RUNTIME_PROOF_BUNDLE,
    write_runtime_proof_bundle,
)
from apps_lic.policy.reasoning_intensity import (
    apply_evidence_support,
    policy_from_reason_codes,
)
from apps_lic.engines.x1d_claude_judge_adapter import (
    AnthropicClaudeX1DTransport,
    run_claude_x1d_judges,
)
from apps_lic.types.linkedin_route_envelope import resolve_linkedin_route_envelope

ROUTE_FAMILY_R4 = ROUTE_FAMILY_R4_MANAGED_DRAFT
ROUTE_FAMILY_R3R4 = ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT  # deprecated guard only
ROUTE_FAMILY_R5 = ROUTE_FAMILY_R5_FALLBACK

_EXECUTION_MANAGED = "managed_workflow"
_EXECUTION_TERMINAL = "terminal_fallback"
_APPS_RESEARCH_DEPRECATED_REASON = "APPS_RESEARCH_DEPRECATED"
_APPS_LIC_RUN_LIVE_CLAUDE_X1D = "APPS_LIC_RUN_LIVE_CLAUDE_X1D"


def _live_x1d_judge_runner():
    if str(os.environ.get(_APPS_LIC_RUN_LIVE_CLAUDE_X1D) or "").strip() != "1":
        return None
    if not str(os.environ.get("ANTHROPIC_API_KEY") or "").strip():
        return None
    transport = AnthropicClaudeX1DTransport()
    return lambda request, candidate: run_claude_x1d_judges(
        request,
        candidate,
        transport=transport,
    )

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
    connection_status: str = "NOT_CONNECTED",
    premium_available: bool = True,
    route_override: str = "",
    manual_brief: str = "",
    allow_research: bool = False,
    lead_profile: Mapping[str, Any] | None = None,
    campaign_objective: str | None = None,
    audience_segment: str = "recruiting",
    governed_opportunity_facts: Iterable[Mapping[str, Any]] | None = None,
    c0_required_namespaces: Iterable[str] | None = None,
    message_type_hint: str = "",
    message_modifiers: Mapping[str, bool] | None = None,
    application_status: str = "",
    desired_next_step: str = "",
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

    route_envelope = resolve_linkedin_route_envelope(
        channel=channel,
        connection_status=connection_status,
        premium_available=premium_available,
        route_override=route_override,
    )
    normalized_channel = "linkedin"
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
    if governed_opportunity_facts is not None:
        personalization_inputs[C0_READINESS_INPUT_KEY] = [
            dict(fact) for fact in governed_opportunity_facts
        ]
    if c0_required_namespaces is not None:
        personalization_inputs["c0_required_namespaces"] = [
            str(namespace) for namespace in c0_required_namespaces
        ]
    if message_type_hint:
        personalization_inputs["message_type_hint"] = str(message_type_hint)
    if message_modifiers is not None:
        personalization_inputs["message_modifiers"] = {
            str(key): bool(value)
            for key, value in message_modifiers.items()
        }
    if application_status:
        personalization_inputs["application_status"] = str(application_status)
    if desired_next_step:
        personalization_inputs["desired_next_step"] = str(desired_next_step)
    personalization_inputs["linkedin_route_envelope"] = route_envelope.to_packet()

    research_req: dict[str, Any] = {
        "allow_research": False,
        "research_disabled_by_policy": True,
        "deprecation_reason": _APPS_RESEARCH_DEPRECATED_REASON,
        "apps_research_deprecated": True,
    }
    if allow_research:
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
            "include_subject_line": route_envelope.subject_required,
            "max_paragraphs": 4 if route_envelope.subject_required else 2,
            "output_schema_ref": (
                "apps_lic.linkedin_inmail_outreach.v1"
                if route_envelope.subject_required
                else "apps_lic.linkedin_recruiter_outreach.v1"
            ),
        },
        "research_requirements": research_req,
        "routing_policy": {"outreach_mode": normalized_outreach_mode},
        "validation_policy": {"max_body_length": route_envelope.hard_cap_chars},
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
            "package_digest": "",
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
    x3 = terminal_r5_exit_disposition_apps_lic(
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        terminal_reason=terminal_reason,
        route_family=ROUTE_FAMILY_R5,
        deprecated_route_family=deprecated_route_family or "",
    )
    x3_str, x3_exit_status, x3_outcome_authorized = x3_manifest_fields(x3)
    x3_final_output = dict(x3.final_output) if x3.final_output else {}
    exit_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_EXIT_DISPOSITION,
        _sr.build_exit_receipt(
            x3,
            x3_disposition=x3_str,
            exit_status=x3_exit_status,
            outcome_authorized=x3_outcome_authorized,
            upstream_receipt_refs=(_sr.FILENAME_ROUTE_CONTRACT,),
        ),
    )
    artifacts.append(exit_path)

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
        "trace_root": trace_id,
        "route_family": ROUTE_FAMILY_R5,
        "execution_form": _EXECUTION_TERMINAL,
        "l3_required": False,
        "terminal_r5": True,
        "terminal_reason": terminal_reason,
        "terminal_r5_reason": terminal_reason,
        "x3_disposition": x3_str,
        "exit_disposition": x3_exit_status,
        "exit_status": x3_exit_status,
        "outcome_authorized": x3_outcome_authorized,
        "exit_stage_policy": exit_stage_policy,
        "exit_disposition_receipt_ref": _sr.FILENAME_EXIT_DISPOSITION,
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "r3r4_research_invoked": False,
        "deprecated_route_family": deprecated_route_family or "",
        "l3_participated": False,
        "c0_invoked": False,
        "pa_invoked": False,
        "l2_executed": False,
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "no_send_receipt": x3_final_output.get("no_send_receipt", ""),
        "no_l4_write_receipt": x3_final_output.get("no_l4_write_receipt", ""),
        "runtime_exhaust_ref": x3_final_output.get("runtime_exhaust_ref", ""),
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


def _write_c0_block_manifest(
    *,
    artifact_dir: Path,
    artifacts: list[str],
    route_payload: Mapping[str, Any],
    route_reasoning_policy: Mapping[str, Any],
    fec: Any,
    c0_block_status: str,
) -> None:
    stage_refs = _sr.c0_block_stage_receipt_refs()
    readiness_status = c0_readiness_status_from_fec(fec)
    recipient_class_status = c0_recipient_class_status_from_fec(fec)
    manifest = {
        **dict(route_payload),
        "reasoning_policy": dict(route_reasoning_policy),
        "sc_level": route_reasoning_policy["sc_level"],
        "reasoning_intensity": route_reasoning_policy["reasoning_intensity"],
        "judge_profile": route_reasoning_policy["judge_profile"],
        "active_judges": list(route_reasoning_policy["judges"]),
        "judge_count": len(route_reasoning_policy["judges"]),
        "max_candidates": route_reasoning_policy["max_candidates"],
        "evidence_support_status": route_reasoning_policy.get(
            "evidence_support_status",
            "",
        ),
        "evidence_action": route_reasoning_policy.get("evidence_action", ""),
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "trace_id": fec.trace_id,
        "terminal_r5": False,
        "terminal_c0_block": True,
        "c0_block_status": c0_block_status,
        "c0_readiness_status": readiness_status,
        "c0_recipient_class_status": recipient_class_status,
        "derived_recipient_class": c0_recipient_class_value_from_fec(fec),
        "recipient_class_confidence": c0_recipient_class_confidence_from_fec(fec),
        "source_snapshot_ids": list(getattr(fec, "snapshot_refs", ()) or ()),
        "freshness_receipts": list(getattr(fec, "freshness_receipts", ()) or ()),
        "c0_gate_verdict_refs": list(getattr(fec, "gate_verdict_refs", ()) or ()),
        "x3_disposition": "DENY",
        "exit_status": "blocked",
        "outcome_authorized": False,
        "exit_stage_policy": "c0_readiness_block_no_pa_no_l2_no_exit_receipt",
        "l3_participated": False,
        "c0_invoked": True,
        "pa_invoked": False,
        "l2_executed": False,
        "l2_execution_status": "not_executed:c0_block",
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "r3r4_research_invoked": False,
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "research_note": "",
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
        terminal_r5=False,
        c0_blocked=True,
    )
    artifacts.append(proof_path)
    _assert_runtime_proof_bundle_pass(artifact_dir)


def _write_c03_block_manifest(
    *,
    artifact_dir: Path,
    artifacts: list[str],
    route_payload: Mapping[str, Any],
    route_reasoning_policy: Mapping[str, Any],
    fec: Any,
    c03: Any,
) -> None:
    stage_refs = _sr.c03_block_stage_receipt_refs()
    readiness_status = c0_readiness_status_from_fec(fec)
    recipient_class_status = c0_recipient_class_status_from_fec(fec)
    manifest = {
        **dict(route_payload),
        "reasoning_policy": dict(route_reasoning_policy),
        "sc_level": route_reasoning_policy["sc_level"],
        "reasoning_intensity": route_reasoning_policy["reasoning_intensity"],
        "judge_profile": route_reasoning_policy["judge_profile"],
        "active_judges": list(route_reasoning_policy["judges"]),
        "judge_count": len(route_reasoning_policy["judges"]),
        "max_candidates": route_reasoning_policy["max_candidates"],
        "evidence_support_status": route_reasoning_policy.get(
            "evidence_support_status",
            "",
        ),
        "evidence_action": route_reasoning_policy.get("evidence_action", ""),
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "trace_id": fec.trace_id,
        "terminal_r5": False,
        "terminal_c0_block": False,
        "terminal_c03_block": True,
        "c0_block_status": "",
        "c0_readiness_status": readiness_status,
        "c0_recipient_class_status": recipient_class_status,
        "derived_recipient_class": c0_recipient_class_value_from_fec(fec),
        "recipient_class_confidence": c0_recipient_class_confidence_from_fec(fec),
        "source_snapshot_ids": list(getattr(fec, "snapshot_refs", ()) or ()),
        "freshness_receipts": list(getattr(fec, "freshness_receipts", ()) or ()),
        "c0_gate_verdict_refs": list(getattr(fec, "gate_verdict_refs", ()) or ()),
        "c03_invoked": True,
        "c03_status": c03.status,
        "c03_blocking_reasons": list(c03.blocking_reasons),
        "c03_message_type": c03.message_gate_result.message_type,
        "c03_message_requirements_status": c03.message_gate_result.status,
        "c03_missing_fields": list(c03.message_gate_result.missing_fields),
        "c03_sender_proof_status": c03.sender_proof_packet.status,
        "c03_proof_packet_id": c03.proof_packet_id,
        "c03_allowed_claim_ids": list(c03.sender_proof_packet.proof_ids),
        "c03_length_budget": c03.length_budget.to_packet(),
        "c03_source_snapshot_ids": list(c03.source_snapshot_ids),
        "x3_disposition": "DENY",
        "exit_status": "blocked",
        "outcome_authorized": False,
        "exit_stage_policy": "c03_sender_proof_block_no_pa_no_l2_no_exit_receipt",
        "l3_participated": False,
        "c0_invoked": True,
        "pa_invoked": False,
        "l2_executed": False,
        "l2_execution_status": "not_executed:c03_block",
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "r3r4_research_invoked": False,
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "research_note": "",
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
        terminal_r5=False,
        c03_blocked=True,
    )
    artifacts.append(proof_path)
    _assert_runtime_proof_bundle_pass(artifact_dir)


def _write_w4_candidate_block_manifest(
    *,
    artifact_dir: Path,
    artifacts: list[str],
    route_payload: Mapping[str, Any],
    route_reasoning_policy: Mapping[str, Any],
    fec: Any,
    c03: Any,
    w4: Any,
    l2_status: str,
    l3_receipt: Any,
) -> None:
    stage_refs = _sr.w4_candidate_block_stage_receipt_refs()
    readiness_status = c0_readiness_status_from_fec(fec)
    recipient_class_status = c0_recipient_class_status_from_fec(fec)
    manifest = {
        **dict(route_payload),
        "reasoning_policy": dict(route_reasoning_policy),
        "sc_level": route_reasoning_policy["sc_level"],
        "reasoning_intensity": route_reasoning_policy["reasoning_intensity"],
        "judge_profile": route_reasoning_policy["judge_profile"],
        "active_judges": list(route_reasoning_policy["judges"]),
        "judge_count": len(route_reasoning_policy["judges"]),
        "max_candidates": route_reasoning_policy["max_candidates"],
        "evidence_support_status": route_reasoning_policy.get(
            "evidence_support_status",
            "",
        ),
        "evidence_action": route_reasoning_policy.get("evidence_action", ""),
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "trace_id": fec.trace_id,
        "terminal_r5": False,
        "terminal_c0_block": False,
        "terminal_c03_block": False,
        "terminal_w4_candidate_block": True,
        "terminal_c03_postgen_block": False,
        "terminal_w5_validation_exit_block": False,
        "c0_block_status": "",
        "c0_readiness_status": readiness_status,
        "c0_recipient_class_status": recipient_class_status,
        "derived_recipient_class": c0_recipient_class_value_from_fec(fec),
        "recipient_class_confidence": c0_recipient_class_confidence_from_fec(fec),
        "source_snapshot_ids": list(getattr(fec, "snapshot_refs", ()) or ()),
        "freshness_receipts": list(getattr(fec, "freshness_receipts", ()) or ()),
        "c0_gate_verdict_refs": list(getattr(fec, "gate_verdict_refs", ()) or ()),
        "c03_invoked": True,
        "c03_status": c03.status,
        "c03_blocking_reasons": list(c03.blocking_reasons),
        "c03_message_type": c03.message_gate_result.message_type,
        "c03_message_requirements_status": c03.message_gate_result.status,
        "c03_missing_fields": list(c03.message_gate_result.missing_fields),
        "c03_sender_proof_status": c03.sender_proof_packet.status,
        "c03_proof_packet_id": c03.proof_packet_id,
        "c03_allowed_claim_ids": list(c03.sender_proof_packet.proof_ids),
        "c03_length_budget": c03.length_budget.to_packet(),
        "c03_source_snapshot_ids": list(c03.source_snapshot_ids),
        **_w4_manifest_fields(w4),
        "c03_postgen_invoked": False,
        "c03_postgen_status": "",
        "c03_postgen_selected_candidate_id": "",
        "c03_postgen_claims_used": [],
        "c03_postgen_blocked_claims": [],
        "c03_postgen_blocking_reasons": [],
        "c03_postgen_proof_packet_id": "",
        "c03_postgen_source_snapshot_ids": [],
        **_w5_manifest_fields(None),
        "x3_disposition": "DENY",
        "exit_status": "blocked",
        "outcome_authorized": False,
        "exit_stage_policy": "w4_candidate_batch_block_no_c03_postgen_no_exit_receipt",
        "l3_participated": True,
        "c0_invoked": True,
        "pa_invoked": True,
        "l2_executed": True,
        "l2_execution_status": l2_status,
        "l3_receipt_id": getattr(l3_receipt, "deterministic_digest", "")[:32],
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "r3r4_research_invoked": False,
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "research_note": "",
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
        terminal_r5=False,
        w4_candidate_blocked=True,
    )
    artifacts.append(proof_path)
    _assert_runtime_proof_bundle_pass(artifact_dir)


def _write_c03_postgen_block_manifest(
    *,
    artifact_dir: Path,
    artifacts: list[str],
    route_payload: Mapping[str, Any],
    route_reasoning_policy: Mapping[str, Any],
    fec: Any,
    c03: Any,
    w4: Any,
    postgen: Any,
    l2_status: str,
    l3_receipt: Any,
) -> None:
    stage_refs = _sr.c03_postgen_block_stage_receipt_refs()
    readiness_status = c0_readiness_status_from_fec(fec)
    recipient_class_status = c0_recipient_class_status_from_fec(fec)
    manifest = {
        **dict(route_payload),
        "reasoning_policy": dict(route_reasoning_policy),
        "sc_level": route_reasoning_policy["sc_level"],
        "reasoning_intensity": route_reasoning_policy["reasoning_intensity"],
        "judge_profile": route_reasoning_policy["judge_profile"],
        "active_judges": list(route_reasoning_policy["judges"]),
        "judge_count": len(route_reasoning_policy["judges"]),
        "max_candidates": route_reasoning_policy["max_candidates"],
        "evidence_support_status": route_reasoning_policy.get(
            "evidence_support_status",
            "",
        ),
        "evidence_action": route_reasoning_policy.get("evidence_action", ""),
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "trace_id": fec.trace_id,
        "terminal_r5": False,
        "terminal_c0_block": False,
        "terminal_c03_block": False,
        "terminal_w4_candidate_block": False,
        "terminal_c03_postgen_block": True,
        "terminal_w5_validation_exit_block": False,
        "c0_block_status": "",
        "c0_readiness_status": readiness_status,
        "c0_recipient_class_status": recipient_class_status,
        "derived_recipient_class": c0_recipient_class_value_from_fec(fec),
        "recipient_class_confidence": c0_recipient_class_confidence_from_fec(fec),
        "source_snapshot_ids": list(getattr(fec, "snapshot_refs", ()) or ()),
        "freshness_receipts": list(getattr(fec, "freshness_receipts", ()) or ()),
        "c0_gate_verdict_refs": list(getattr(fec, "gate_verdict_refs", ()) or ()),
        "c03_invoked": True,
        "c03_status": c03.status,
        "c03_blocking_reasons": list(c03.blocking_reasons),
        "c03_message_type": c03.message_gate_result.message_type,
        "c03_message_requirements_status": c03.message_gate_result.status,
        "c03_missing_fields": list(c03.message_gate_result.missing_fields),
        "c03_sender_proof_status": c03.sender_proof_packet.status,
        "c03_proof_packet_id": c03.proof_packet_id,
        "c03_allowed_claim_ids": list(c03.sender_proof_packet.proof_ids),
        "c03_length_budget": c03.length_budget.to_packet(),
        "c03_source_snapshot_ids": list(c03.source_snapshot_ids),
        **_w4_manifest_fields(w4),
        "c03_postgen_invoked": True,
        "c03_postgen_status": postgen.status,
        "c03_postgen_selected_candidate_id": postgen.selected_candidate_id,
        "c03_postgen_claims_used": list(postgen.claims_used),
        "c03_postgen_blocked_claims": [dict(item) for item in postgen.blocked_claims],
        "c03_postgen_blocking_reasons": list(postgen.blocking_reasons),
        "c03_postgen_proof_packet_id": postgen.proof_packet_id,
        "c03_postgen_source_snapshot_ids": list(postgen.source_snapshot_ids),
        **_w5_manifest_fields(None),
        "x3_disposition": "DENY",
        "exit_status": "blocked",
        "outcome_authorized": False,
        "exit_stage_policy": "c03_postgen_claim_block_no_exit_receipt",
        "l3_participated": True,
        "c0_invoked": True,
        "pa_invoked": True,
        "l2_executed": True,
        "l2_execution_status": l2_status,
        "l3_receipt_id": getattr(l3_receipt, "deterministic_digest", "")[:32],
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "r3r4_research_invoked": False,
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "research_note": "",
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
        terminal_r5=False,
        c03_postgen_blocked=True,
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
    route_reasoning_policy = policy_from_reason_codes(route.reason_codes)

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
        "reasoning_policy": route_reasoning_policy,
        "sc_level": route_reasoning_policy["sc_level"],
        "reasoning_intensity": route_reasoning_policy["reasoning_intensity"],
        "judge_profile": route_reasoning_policy["judge_profile"],
        "active_judges": list(route_reasoning_policy["judges"]),
        "judge_count": len(route_reasoning_policy["judges"]),
        "max_candidates": route_reasoning_policy["max_candidates"],
    }
    will_c0 = bool(l1.grounding_required)
    will_pa = bool(l1.model_generation_required and will_c0)
    if (
        route.route_family in {ROUTE_FAMILY_R3R4, ROUTE_FAMILY_R5}
        or route.execution_form == _EXECUTION_TERMINAL
    ):
        route_downstream = (_sr.FILENAME_EXIT_DISPOSITION,)
    elif route.execution_form == _EXECUTION_MANAGED:
        route_downstream = _sr.managed_workflow_downstream_refs(
            c0_invoked=will_c0,
            c03_invoked=will_c0,
            pa_invoked=will_pa,
            w4_candidate_invoked=will_pa,
            c03_postgen_invoked=will_pa,
            w5_validation_exit_invoked=will_pa,
        )
    else:
        route_downstream = ()
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
            exit_stage_policy="deprecated_apps_research_route_exit_compatible_denial_receipt",
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
            exit_status="blocked",
            outcome_authorized=False,
            terminal_r5=True,
            terminal_r5_reason=_APPS_RESEARCH_DEPRECATED_REASON,
            artifact_dir=artifact_dir,
            artifacts=tuple(artifacts),
        )

    if route.execution_form == _EXECUTION_TERMINAL or route.route_family == ROUTE_FAMILY_R5:
        if any("apps_research_deprecated" in code for code in route.reason_codes):
            terminal_reason = _APPS_RESEARCH_DEPRECATED_REASON
        elif any("research_requested_but_disabled" in code for code in route.reason_codes):
            terminal_reason = _APPS_RESEARCH_DEPRECATED_REASON
        else:
            terminal_reason = "route_family=R5_FALLBACK"
        _write_terminal_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            request_id=route.request_id,
            run_id=route.run_id,
            trace_id=route.trace_id,
            terminal_reason=terminal_reason,
            exit_stage_policy="terminal_r5_exit_compatible_denial_receipt",
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=route.route_family,
            execution_form=route.execution_form,
            x3_disposition="DENY",
            exit_status="blocked",
            outcome_authorized=False,
            terminal_r5=True,
            terminal_r5_reason=terminal_reason,
            artifact_dir=artifact_dir,
            artifacts=tuple(artifacts),
        )

    c0_invoked = False
    c03_invoked = False
    pa_invoked = False
    fec = None
    c03 = None
    w4_candidate = None
    prompt = None
    c0_block_status = ""

    if l1.grounding_required:
        fec = c0_retrieve_apps_lic(route, validated_request)
        c0_invoked = True
        route_reasoning_policy = apply_evidence_support(
            route_reasoning_policy,
            str(fec.support_status or ""),
        )
        c0_block_status = c0_blocking_status_from_fec(fec)
        c0_downstream_refs = (
            (_sr.FILENAME_SPINE_MANIFEST,)
            if c0_block_status != C0_READY
            else (_sr.FILENAME_C03_SENDER_PROOF,)
        )
        c0_path = _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_C0_FEC,
            _sr.build_c0_receipt(
                fec,
                downstream_receipt_refs=c0_downstream_refs,
            ),
        )
        artifacts.append(c0_path)
        fec_summary_path = _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_FEC_SUMMARY,
            _sr.build_c0_summary(fec),
        )
        artifacts.append(fec_summary_path)

    if fec is not None and not c0_ready_for_pa(fec):
        _write_c0_block_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            route_reasoning_policy=route_reasoning_policy,
            fec=fec,
            c0_block_status=c0_block_status,
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=route.route_family,
            execution_form=route.execution_form,
            x3_disposition="DENY",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=artifact_dir,
            l3_participated=False,
            c0_invoked=True,
            pa_invoked=False,
            l2_executed=False,
            l2_execution_status="not_executed:c0_block",
            exit_status="blocked",
            outcome_authorized=False,
            artifacts=tuple(artifacts),
        )

    if l1.model_generation_required and fec is not None:
        c03 = build_c03_sender_proof_for_pa(
            route=route,
            l1_plan=l1,
            fec=fec,
            validated_request=validated_request,
        )
        c03_invoked = True
        c03_downstream_refs = (
            (_sr.FILENAME_PA_RECEIPT,)
            if c03_ready_for_pa(c03)
            else (_sr.FILENAME_SPINE_MANIFEST,)
        )
        c03_path = _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_C03_SENDER_PROOF,
            _sr.build_c03_receipt(
                c03,
                downstream_receipt_refs=c03_downstream_refs,
            ),
        )
        artifacts.append(c03_path)

    if c03 is not None and not c03_ready_for_pa(c03):
        _write_c03_block_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            route_reasoning_policy=route_reasoning_policy,
            fec=fec,
            c03=c03,
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=route.route_family,
            execution_form=route.execution_form,
            x3_disposition="DENY",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=artifact_dir,
            l3_participated=False,
            c0_invoked=True,
            pa_invoked=False,
            l2_executed=False,
            l2_execution_status="not_executed:c03_block",
            exit_status="blocked",
            outcome_authorized=False,
            artifacts=tuple(artifacts),
        )

    if l1.model_generation_required and fec is not None:
        prompt = pa_compose_apps_lic(
            route=route,
            l1_plan=l1,
            fec=fec,
            validated_request=validated_request,
            sender_proof_envelope=c03.pa_sender_proof_envelope if c03 else None,
            length_budget=c03.length_budget.to_packet() if c03 else None,
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
        _sr.build_l2_receipt(
            l2_artifact,
            downstream_receipt_refs=(_sr.FILENAME_W4_CANDIDATE_BATCH,),
        ),
    )
    artifacts.append(l2_path)

    if c03 is None:
        raise ValueError("canonical_dispatch: C0.3 proof packet required before L2 postgen gate")
    w4_candidate = materialize_w4_candidate_batch(
        l2_artifact=l2_artifact,
        route_reasoning_policy=route_reasoning_policy,
        c03=c03,
    )
    w4_downstream_refs = (
        (_sr.FILENAME_C03_POSTGEN_VALIDATION,)
        if w4_candidate_batch_ready(w4_candidate)
        else (_sr.FILENAME_SPINE_MANIFEST,)
    )
    w4_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_W4_CANDIDATE_BATCH,
        _sr.build_w4_candidate_batch_receipt(
            w4_candidate,
            downstream_receipt_refs=w4_downstream_refs,
        ),
    )
    artifacts.append(w4_path)

    l2_status = getattr(l2_artifact, "execution_status", "") or ""
    if not w4_candidate_batch_ready(w4_candidate):
        _write_w4_candidate_block_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            route_reasoning_policy=route_reasoning_policy,
            fec=fec,
            c03=c03,
            w4=w4_candidate,
            l2_status=l2_status,
            l3_receipt=l3_receipt,
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=route.route_family,
            execution_form=route.execution_form,
            x3_disposition="DENY",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=artifact_dir,
            l3_participated=True,
            c0_invoked=True,
            pa_invoked=True,
            l2_executed=True,
            l2_execution_status=l2_status,
            exit_status="blocked",
            outcome_authorized=False,
            artifacts=tuple(artifacts),
        )

    c03_postgen = validate_l2_c03_postgen_claims(
        l2_artifact=l2_artifact,
        c03=c03,
    )
    c03_postgen_downstream_refs = (
        (_sr.FILENAME_W5_VALIDATION_EXIT,)
        if c03_postgen_claims_pass(c03_postgen)
        else (_sr.FILENAME_SPINE_MANIFEST,)
    )
    c03_postgen_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_C03_POSTGEN_VALIDATION,
        _sr.build_c03_postgen_receipt(
            c03_postgen,
            upstream_receipt_refs=(_sr.FILENAME_W4_CANDIDATE_BATCH,),
            downstream_receipt_refs=c03_postgen_downstream_refs,
        ),
    )
    artifacts.append(c03_postgen_path)

    if not c03_postgen_claims_pass(c03_postgen):
        _write_c03_postgen_block_manifest(
            artifact_dir=artifact_dir,
            artifacts=artifacts,
            route_payload=route_payload,
            route_reasoning_policy=route_reasoning_policy,
            fec=fec,
            c03=c03,
            w4=w4_candidate,
            postgen=c03_postgen,
            l2_status=l2_status,
            l3_receipt=l3_receipt,
        )
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=route.route_family,
            execution_form=route.execution_form,
            x3_disposition="DENY",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=artifact_dir,
            l3_participated=True,
            c0_invoked=True,
            pa_invoked=True,
            l2_executed=True,
            l2_execution_status=l2_status,
            exit_status="blocked",
            outcome_authorized=False,
            artifacts=tuple(artifacts),
        )

    w5_validation_exit = materialize_w5_validation_exit(
        route=route,
        l1_plan=l1,
        fec=fec,
        validated_request=validated_request,
        c03=c03,
        w4=w4_candidate,
        x1d_judge_runner=_live_x1d_judge_runner(),
    )
    w5_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_W5_VALIDATION_EXIT,
        _sr.build_w5_validation_exit_receipt(
            w5_validation_exit,
            upstream_receipt_refs=(_sr.FILENAME_C03_POSTGEN_VALIDATION,),
            downstream_receipt_refs=(_sr.FILENAME_EXIT_DISPOSITION,),
        ),
    )
    artifacts.append(w5_path)
    w5_clear = w5_validation_exit_clear(w5_validation_exit)

    x3 = exit_finalize_apps_lic(
        l2_artifact,
        validation_exit_proof=w5_validation_exit.exit_proof_bundle,
    )

    x3_str, x3_exit_status, x3_outcome_authorized = x3_manifest_fields(x3)

    exit_path = _sr.write_stage_receipt(
        artifact_dir / _sr.FILENAME_EXIT_DISPOSITION,
        _sr.build_exit_receipt(
            x3,
            x3_disposition=x3_str,
            exit_status=x3_exit_status,
            outcome_authorized=x3_outcome_authorized,
            upstream_receipt_refs=(_sr.FILENAME_W5_VALIDATION_EXIT,),
        ),
    )
    artifacts.append(exit_path)

    stage_refs = _sr.standard_stage_receipt_refs(
        terminal_r5=False,
        c0_invoked=c0_invoked,
        c03_invoked=c03_invoked,
        pa_invoked=pa_invoked,
        w4_candidate_invoked=True,
        c03_postgen_invoked=True,
        w5_validation_exit_invoked=True,
        l3_participated=True,
    )
    manifest = {
        **route_payload,
        "reasoning_policy": route_reasoning_policy,
        "sc_level": route_reasoning_policy["sc_level"],
        "reasoning_intensity": route_reasoning_policy["reasoning_intensity"],
        "judge_profile": route_reasoning_policy["judge_profile"],
        "active_judges": list(route_reasoning_policy["judges"]),
        "judge_count": len(route_reasoning_policy["judges"]),
        "max_candidates": route_reasoning_policy["max_candidates"],
        "evidence_support_status": route_reasoning_policy.get(
            "evidence_support_status", ""
        ),
        "evidence_action": route_reasoning_policy.get("evidence_action", ""),
        "request_id": route.request_id,
        "run_id": route.run_id,
        "trace_id": route.trace_id,
        "terminal_r5": False,
        "terminal_c0_block": False,
        "terminal_c03_block": False,
        "terminal_w4_candidate_block": False,
        "terminal_c03_postgen_block": False,
        "terminal_w5_validation_exit_block": not w5_clear,
        "c0_block_status": "",
        "c0_readiness_status": c0_readiness_status_from_fec(fec),
        "c0_recipient_class_status": c0_recipient_class_status_from_fec(fec),
        "derived_recipient_class": c0_recipient_class_value_from_fec(fec),
        "recipient_class_confidence": c0_recipient_class_confidence_from_fec(fec),
        "source_snapshot_ids": list(getattr(fec, "snapshot_refs", ()) or ()),
        "freshness_receipts": list(getattr(fec, "freshness_receipts", ()) or ()),
        "c03_invoked": c03_invoked,
        "c03_status": c03.status if c03 else "",
        "c03_blocking_reasons": list(c03.blocking_reasons) if c03 else [],
        "c03_message_type": c03.message_gate_result.message_type if c03 else "",
        "c03_message_requirements_status": (
            c03.message_gate_result.status if c03 else ""
        ),
        "c03_missing_fields": (
            list(c03.message_gate_result.missing_fields) if c03 else []
        ),
        "c03_sender_proof_status": c03.sender_proof_packet.status if c03 else "",
        "c03_proof_packet_id": c03.proof_packet_id if c03 else "",
        "c03_allowed_claim_ids": (
            list(c03.sender_proof_packet.proof_ids) if c03 else []
        ),
        "c03_length_budget": c03.length_budget.to_packet() if c03 else {},
        "c03_source_snapshot_ids": list(c03.source_snapshot_ids) if c03 else [],
        **_w4_manifest_fields(w4_candidate),
        "c03_postgen_invoked": True,
        "c03_postgen_status": c03_postgen.status,
        "c03_postgen_selected_candidate_id": c03_postgen.selected_candidate_id,
        "c03_postgen_claims_used": list(c03_postgen.claims_used),
        "c03_postgen_blocked_claims": [
            dict(item) for item in c03_postgen.blocked_claims
        ],
        "c03_postgen_blocking_reasons": list(c03_postgen.blocking_reasons),
        "c03_postgen_proof_packet_id": c03_postgen.proof_packet_id,
        "c03_postgen_source_snapshot_ids": list(c03_postgen.source_snapshot_ids),
        **_w5_manifest_fields(w5_validation_exit),
        "x3_disposition": x3_str,
        "exit_status": x3_exit_status,
        "outcome_authorized": x3_outcome_authorized,
        "l3_participated": True,
        "c0_invoked": c0_invoked,
        "pa_invoked": pa_invoked,
        "l2_executed": True,
        "l2_execution_status": l2_status,
        "l3_receipt_id": getattr(l3_receipt, "deterministic_digest", "")[:32],
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "apps_research_invoked": False,
        "r3r4_research_invoked": False,
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "research_note": "",
        "stage_receipt_refs": list(stage_refs),
    }
    manifest_path = _sr.write_stage_receipt(artifact_dir / _sr.FILENAME_SPINE_MANIFEST, manifest)
    artifacts.append(manifest_path)
    proof_path = write_runtime_proof_bundle(
        artifact_dir,
        manifest,
        terminal_r5=False,
        w5_validation_exit_blocked=not w5_clear,
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
        l2_executed=True,
        l2_execution_status=l2_status,
        exit_status=x3_exit_status,
        outcome_authorized=x3_outcome_authorized,
        artifacts=tuple(artifacts),
    )
