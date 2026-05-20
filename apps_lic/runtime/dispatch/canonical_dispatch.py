"""Canonical apps_lic product spine: U0 → L1 → L0 → (R3R4 research) → C0 → PA → L3 → L2 → Exit.

No integrated_r4_lic shortcut, no GovernedLicRun, no YAML L2 recipe resolver, no direct HOP
bypass from CLI. R3R4 research uses ``ManagedWorkflowDispatcher`` before re-planning.
"""

from __future__ import annotations

import dataclasses
import json
import os
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
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_lic.runtime.bindings.exit_binding import exit_finalize_apps_lic
from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt

from apps_lic.runtime.dispatch.spine_run_result import SpineRunResult, x3_manifest_fields
from apps_lic.runtime.dispatch import stage_receipts as _sr
from apps_lic.runtime.dispatch.runtime_proof_bundle import (
    FILENAME_RUNTIME_PROOF_BUNDLE,
    write_runtime_proof_bundle,
)

ROUTE_FAMILY_R4 = ROUTE_FAMILY_R4_MANAGED_DRAFT
ROUTE_FAMILY_R3R4 = ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT
ROUTE_FAMILY_R5 = ROUTE_FAMILY_R5_FALLBACK

_EXECUTION_MANAGED = "managed_workflow"
_EXECUTION_TERMINAL = "terminal_fallback"


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
    manual_brief: str = "",
    allow_research: bool = False,
    lead_profile: Mapping[str, Any] | None = None,
    campaign_objective: str = "Drive renewal conversation with enterprise prospect",
) -> dict[str, Any]:
    """Map CLI kwargs to AppsLicIngressContractV1-shaped raw JSON for U0."""
    rid = run_id or f"run_lic_{uuid.uuid4().hex[:12]}"
    req_id = request_id or f"req_lic_{uuid.uuid4().hex[:12]}"
    tid = trace_id or f"trace_lic_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    has_brief = bool(manual_brief.strip())
    lead = dict(lead_profile) if lead_profile else {
        "verified_name": "Jane Smith",
        "title": "VP Technology",
        "seniority_class": "VP",
        "company_name": "Acme Corp",
        "industry": "Technology",
        "consent_attested": True,
    }
    research_req: dict[str, Any] = {}
    if allow_research and not has_brief:
        research_req = {
            "allow_research": True,
            "required_evidence_types": ["company_brief", "lead_context"],
        }
    personalization_inputs: dict[str, Any] = {}
    if has_brief:
        personalization_inputs["manual_brief"] = manual_brief.strip()
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
            "request_type": "outreach_draft",
            "campaign_objective": campaign_objective,
            "channel": "email",
            "audience_segment": "enterprise_renewal",
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
                "title": "SVP AI Solutions",
            },
            "sender_ref": None,
            "company_profile": None,
            "company_ref": None,
        },
        "personalization": {"inputs": personalization_inputs},
        "generation_hints": {},
        "tone_constraints": {},
        "output_format": {},
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _inject_context_signals(
    validated_request: Any,
    raw_ingress: Mapping[str, Any],
) -> Any:
    """Attach L0 routing context_signals to app_payload post-U0 (not ingress-schema fields)."""
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


def _manifest_as_dict(manifest: Any) -> dict[str, Any]:
    if isinstance(manifest, dict):
        return manifest
    if dataclasses.is_dataclass(manifest):
        return dataclasses.asdict(manifest)
    return {}


def _merge_research_manifest(app_payload: dict[str, Any], manifest: Any) -> dict[str, Any]:
    """Inject managed-workflow briefing into app_payload for re-planning."""
    manifest_dict = _manifest_as_dict(manifest)
    merged = dict(app_payload)
    signals = dict(merged.get("context_signals") or {})
    freshness = manifest_dict.get("freshness_status", "fresh")
    signals["briefing_fresh"] = freshness == "fresh"
    signals["context_grounded"] = freshness == "fresh"
    signals.setdefault("lead_profile_valid", True)
    merged["context_signals"] = signals
    personalization = dict(merged.get("personalization") or {})
    inputs = dict(personalization.get("inputs") or {})
    company_brief = manifest_dict.get("company_brief") or manifest_dict.get("briefing_text")
    if company_brief:
        inputs["managed_briefing"] = company_brief
    if manifest_dict.get("recipient_brief"):
        inputs["recipient_brief"] = manifest_dict["recipient_brief"]
    personalization["inputs"] = inputs
    merged["personalization"] = personalization
    return merged


def _build_request_for_briefing(route: RouteContract, validated_request: Any) -> Any:
    from apps_lic.integrations.managed_workflow_dispatcher import RequestForBriefing

    payload = dict(validated_request.app_payload or {})
    transport = payload.get("transport") or {}
    campaign = payload.get("campaign") or {}
    entity = payload.get("entity_refs") or {}
    lead = entity.get("lead_profile") or {}
    research_req = payload.get("research_requirements") or {}
    return RequestForBriefing(
        request_id=route.request_id,
        run_id=route.run_id,
        trace_id=route.trace_id,
        recipient_class=str(lead.get("seniority_class") or "RECRUITER"),
        recipient_name=str(lead.get("verified_name") or "Unknown"),
        company_name=str(lead.get("company_name") or "Unknown"),
        job_title=str(lead.get("title") or ""),
        channel=str(campaign.get("channel") or "email"),
        outreach_mode=str(campaign.get("outreach_mode") or "cold"),
        relationship_distance=str(campaign.get("relationship_distance") or "cold"),
        sender_resume_ref="sha256:cli_sender",
        sender_policy_hash="sha256:cli_policy",
        sender_blueprint_hash="sha256:cli_blueprint",
        research_authorized=bool(research_req.get("allow_research", False)),
        research_capability_ref="apps_research.v1",
        audit_refs=tuple(validated_request.audit_refs or ()),
    )


def _research_bridge() -> Any:
    if os.environ.get("APPS_LIC_MOCK_RESEARCH", "").strip() in ("1", "true", "yes"):
        from apps_lic.integrations.apps_research_bridge import MockAppsResearchBridge

        return MockAppsResearchBridge(confidence_score=0.85)
    from apps_lic.integrations.apps_research_bridge import AppsResearchBridge

    return AppsResearchBridge(capability_ref="apps_research.v1")


def _write_mock_elimination_proof(artifact_dir: Path, bridge: Any) -> str:
    """Record that live research path did not use mock bridge env or class."""
    payload = {
        "APPS_LIC_MOCK_RESEARCH": os.environ.get("APPS_LIC_MOCK_RESEARCH", ""),
        "bridge_class": type(bridge).__name__,
        "bridge_module": type(bridge).__module__,
        "mock_env_active": os.environ.get("APPS_LIC_MOCK_RESEARCH", "").strip().lower()
        in ("1", "true", "yes"),
        "mock_bridge_class": "MockAppsResearchBridge",
    }
    path = artifact_dir / _sr.FILENAME_MOCK_ELIMINATION_PROOF
    _sr.write_stage_receipt(path, payload)
    return str(path)


def _serialize_research_outcome(outcome: Any) -> dict[str, Any]:
    from apps_lic.integrations.managed_workflow_dispatcher import (
        BriefingReady,
        DispatchFailurePacket,
    )

    if isinstance(outcome, BriefingReady):
        return {
            "outcome": "BriefingReady",
            "research_run_id": outcome.research_run_id,
            "research_evidence_count": outcome.research_evidence_count,
            "confidence_score": outcome.confidence_score,
            "manifest_freshness": getattr(outcome.manifest, "freshness_status", None),
        }
    if isinstance(outcome, DispatchFailurePacket):
        return {
            "outcome": "DispatchFailurePacket",
            "r5_reason_code": outcome.r5_reason_code,
            "detail": outcome.detail,
        }
    return {"outcome": type(outcome).__name__}


def _run_r3r4_research(
    *,
    route: RouteContract,
    validated_request: Any,
    artifact_dir: Path | None = None,
) -> tuple[bool, str, Any | None]:
    """Dispatch apps_research via ``dispatch_managed_briefing`` when R3R4 is selected."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        BriefingReady,
        DispatchFailurePacket,
        dispatch_managed_briefing,
    )

    req = _build_request_for_briefing(route, validated_request)
    bridge = _research_bridge()

    if artifact_dir is not None:
        _write_mock_elimination_proof(artifact_dir, bridge)
        pre_route = {
            "route_id": route.route_id,
            "route_family": route.route_family,
            "execution_form": route.execution_form,
            "l3_required": route.l3_required,
        }
        _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_ROUTE_PRE_RESEARCH,
            pre_route,
        )
        _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_RESEARCH_BRIDGE_REQUEST,
            dataclasses.asdict(req),
        )

    outcome = dispatch_managed_briefing(req, bridge=bridge)

    if artifact_dir is not None:
        response_payload: dict[str, Any] = {
            "dispatch_outcome": _serialize_research_outcome(outcome),
        }
        if isinstance(outcome, BriefingReady):
            response_payload["audit_refs"] = list(getattr(outcome, "audit_refs", ()) or ())
            response_payload["research_run_id"] = outcome.research_run_id
            response_payload["research_evidence_count"] = outcome.research_evidence_count
            response_payload["confidence_score"] = outcome.confidence_score
            response_payload["evidence_lineage"] = list(
                getattr(outcome, "evidence_lineage", ()) or ()
            )
        _sr.write_stage_receipt(
            artifact_dir / _sr.FILENAME_RESEARCH_BRIDGE_RESPONSE,
            response_payload,
        )

    if isinstance(outcome, BriefingReady):
        return True, "BriefingReady", outcome.manifest
    if isinstance(outcome, DispatchFailurePacket):
        return False, outcome.r5_reason_code, None
    return False, "unknown_dispatch_outcome", None


def run_canonical_apps_lic_spine(
    raw_ingress: dict[str, Any],
    *,
    artifact_root: Path | None = None,
    skip_r3r4_research: bool = False,
) -> SpineRunResult:
    """Execute the canonical AG-8 spine for one apps_lic ingress payload."""
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

    research_note = ""
    research_failed = False
    if route.route_family == ROUTE_FAMILY_R3R4 and not skip_r3r4_research:
        ok, research_note, manifest = _run_r3r4_research(
            route=route,
            validated_request=validated_request,
            artifact_dir=artifact_dir,
        )
        if ok and manifest is not None:
            merged_payload = _merge_research_manifest(
                dict(validated_request.app_payload),
                manifest,
            )
            validated_request = dataclasses.replace(
                validated_request,
                app_payload=merged_payload,
            )
            l1 = l1_plan_apps_lic(validated_request)
            route = l0_route_apps_lic(l1)
        else:
            research_failed = True

    if research_failed:
        stage_refs = _sr.standard_stage_receipt_refs(
            terminal_r5=True,
            c0_invoked=False,
            pa_invoked=False,
            l3_participated=False,
        )
        terminal_reason = research_note or "APPS_RESEARCH_FAILED"
        manifest = {
            "route_id": route.route_id,
            "route_family": ROUTE_FAMILY_R5,
            "execution_form": _EXECUTION_TERMINAL,
            "l3_required": False,
            "reason_codes": list(route.reason_codes) + [terminal_reason],
            "request_id": route.request_id,
            "run_id": route.run_id,
            "trace_id": route.trace_id,
            "terminal_r5": True,
            "terminal_r5_reason": terminal_reason,
            "x3_disposition": "DENY",
            "exit_status": "failure",
            "outcome_authorized": False,
            "exit_stage_policy": "r3r4_research_fail_closed_no_exit_receipt",
            "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
            "research_note": terminal_reason,
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
        return SpineRunResult(
            run_id=run_id,
            request_id=route.request_id,
            trace_id=route.trace_id,
            route_id=route.route_id,
            route_family=ROUTE_FAMILY_R5,
            execution_form=_EXECUTION_TERMINAL,
            x3_disposition="DENY",
            terminal_r5=True,
            terminal_r5_reason=terminal_reason,
            artifact_dir=artifact_dir,
            artifacts=tuple(artifacts),
        )

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

    if route.execution_form == _EXECUTION_TERMINAL or route.route_family == ROUTE_FAMILY_R5:
        stage_refs = _sr.standard_stage_receipt_refs(
            terminal_r5=True,
            c0_invoked=False,
            pa_invoked=False,
            l3_participated=False,
        )
        manifest = {
            **route_payload,
            "request_id": route.request_id,
            "run_id": route.run_id,
            "trace_id": route.trace_id,
            "terminal_r5": True,
            "terminal_r5_reason": research_note or "route_family=R5_FALLBACK",
            "x3_disposition": "DENY",
            "exit_status": "failure",
            "outcome_authorized": False,
            "exit_stage_policy": "terminal_r5_short_circuit_no_exit_receipt",
            "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
            "stage_receipt_refs": list(stage_refs),
        }
        manifest_path = _sr.write_stage_receipt(artifact_dir / _sr.FILENAME_SPINE_MANIFEST, manifest)
        artifacts.append(manifest_path)
        proof_path = write_runtime_proof_bundle(
            artifact_dir,
            manifest,
            terminal_r5=True,
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
            x3_disposition="DENY",
            terminal_r5=True,
            terminal_r5_reason=research_note or "R5_TERMINAL_FALLBACK",
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
        "research_note": research_note,
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
