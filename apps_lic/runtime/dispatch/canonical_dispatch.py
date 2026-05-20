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

from apps_lic.runtime.dispatch.spine_run_result import SpineRunResult

ROUTE_FAMILY_R4 = ROUTE_FAMILY_R4_MANAGED_DRAFT
ROUTE_FAMILY_R3R4 = ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT
ROUTE_FAMILY_R5 = ROUTE_FAMILY_R5_FALLBACK

_EXECUTION_MANAGED = "managed_workflow"
_EXECUTION_TERMINAL = "terminal_fallback"


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
            "research_evidence_types": ["company_brief", "lead_context"],
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


def _run_r3r4_research(
    *,
    route: RouteContract,
    validated_request: Any,
) -> tuple[bool, str, Any | None]:
    """Dispatch apps_research via ``dispatch_managed_briefing`` when R3R4 is selected."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        BriefingReady,
        DispatchFailurePacket,
        dispatch_managed_briefing,
    )

    req = _build_request_for_briefing(route, validated_request)
    outcome = dispatch_managed_briefing(req, bridge=_research_bridge())
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
    validated_request, _reflection = apps_lic_u0_adapt(raw_ingress)
    validated_request = _inject_context_signals(validated_request, raw_ingress)
    l1 = l1_plan_apps_lic(validated_request)
    route = l0_route_apps_lic(l1)

    run_id = route.run_id
    artifact_dir = artifact_root or (
        Path("artifacts") / "apps_lic" / "spine_convergence" / "runs" / run_id
    )
    artifacts: list[str] = []

    _write_json(
        artifact_dir / "ingress_raw.json",
        {"ingress": raw_ingress, "reflection_keys": list(_reflection.keys()) if isinstance(_reflection, dict) else []},
    )
    artifacts.append(str(artifact_dir / "ingress_raw.json"))

    research_note = ""
    if route.route_family == ROUTE_FAMILY_R3R4 and not skip_r3r4_research:
        ok, research_note, manifest = _run_r3r4_research(
            route=route,
            validated_request=validated_request,
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

    route_payload = {
        "route_id": route.route_id,
        "route_family": route.route_family,
        "execution_form": route.execution_form,
        "l3_required": route.l3_required,
        "reason_codes": list(route.reason_codes),
    }
    _write_json(artifact_dir / "route_contract.json", route_payload)
    artifacts.append(str(artifact_dir / "route_contract.json"))

    if route.execution_form == _EXECUTION_TERMINAL or route.route_family == ROUTE_FAMILY_R5:
        manifest = {
            **route_payload,
            "terminal_r5": True,
            "terminal_r5_reason": research_note or "route_family=R5_FALLBACK",
            "x3_disposition": "DENY",
            "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        }
        _write_json(artifact_dir / "spine_run_manifest.json", manifest)
        artifacts.append(str(artifact_dir / "spine_run_manifest.json"))
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
        _write_json(
            artifact_dir / "fec_summary.json",
            {
                "compilation_hash": fec.compilation_hash,
                "item_count": len(fec.evidence_items),
            },
        )
        artifacts.append(str(artifact_dir / "fec_summary.json"))

    if l1.model_generation_required and fec is not None:
        prompt = pa_compose_apps_lic(
            route=route,
            l1_plan=l1,
            fec=fec,
            validated_request=validated_request,
        )
        pa_invoked = True

    if route.execution_form != _EXECUTION_MANAGED:
        raise ValueError(
            f"canonical_dispatch: non-terminal route must be managed_workflow; "
            f"got {route.execution_form!r}"
        )

    l3_receipt, step, _bus = l3_orchestrate_apps_lic(route, fec, prompt)
    l2_artifact = l2_execute_apps_lic(route, fec, step, prompt)
    x3 = exit_finalize_apps_lic(l2_artifact)

    l2_status = getattr(l2_artifact, "execution_status", "") or ""
    x3_disp = getattr(x3, "disposition", None) or getattr(x3, "final_disposition", "UNKNOWN")
    x3_str = str(x3_disp)

    manifest = {
        **route_payload,
        "terminal_r5": False,
        "x3_disposition": x3_str,
        "l3_participated": True,
        "c0_invoked": c0_invoked,
        "pa_invoked": pa_invoked,
        "l2_execution_status": l2_status,
        "l3_receipt_id": getattr(l3_receipt, "receipt_id", ""),
        "producer_component": "apps_lic.runtime.dispatch.canonical_dispatch",
        "research_note": research_note,
    }
    _write_json(artifact_dir / "spine_run_manifest.json", manifest)
    artifacts.append(str(artifact_dir / "spine_run_manifest.json"))

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
        exit_status=x3_str,
        artifacts=tuple(artifacts),
    )
