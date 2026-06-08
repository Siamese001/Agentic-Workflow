"""L1 cognition binding for the apps_lic `outreach_message` task class.

L1 is the SECOND stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L3/L2 -> Exit
pipeline. Its job is to consume the U0 ValidatedRequest, read the apps_lic
domain contract (advisory-only), and emit a typed L1PlanContract that downstream
L0/C0/PA/L2 stages consume.

AG-8 W4 invariant (apps-lic-ag8-golden-template-adoption-f3c2e1):
    L1 reads `validated_request.app_payload` ONLY — not any legacy
    AppsLicIngressPayload or envelope.payload. The five projection mappings
    surfaced on L1PlanContract are:

        - task_spec         — request_type + channel + action_required +
                              workflow_required + grounding_required + side_effect_class
        - query_spec        — lead identity anchor + sender identity anchor +
                              campaign_objective + audience_segment
        - support_expectation — grounding required + research/evidence requirements +
                                HITL posture + governance shield + PII policy
        - output_expectation — channel + tone constraints + output format +
                               gate decision policy
        - policy_refs       — references to hitl_policy, pii_policy, governance_shield,
                               antipattern_policy, source_lineage

    And two apps_lic-specific extras beyond the five base projections:

        - route_hints       — advisory hints for L0 (audience_segment, channel,
                               request_type). L0 IGNORES these for deterministic
                               routing decisions; they are advisory metadata only.
        - grounding_hints   — advisory derivation surface for grounding / workflow
                               flags; L0 consumes grounding_required from
                               L1PlanContract.grounding_required directly.

HARD LAWS:
    - grounding_required = app_payload.campaign.grounding_required (from payload)
    - workflow_required → model_generation_required=True + write_authority_present=False
    - side_effect_class must be 'read_only' (already enforced by U0; verified here)
    - L1 does NOT retrieve, execute, assemble prompts, or write L4
    - L1 does NOT call ChromaDB, embedding models, or any external I/O

Pattern: pure function. No state. No I/O.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W4)
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


APPS_LIC_L1_CERT_REF: str = "l1-apps-lic-outreach-message-ag8-w4-f3c2e1"

_PLANNING_PROFILE_RELPATH: str = "apps_lic/config/domain_contract/orchestration_profiles.yaml"

# ---------------------------------------------------------------------------
# Task plan — nine HOP stages in execution order
# ---------------------------------------------------------------------------
_OUTREACH_MESSAGE_TASK_PLAN: tuple[str, ...] = (
    "hop1_classify_intent",      # classify request into campaign archetype
    "hop2_verify_grounding",     # verify evidence anchors + consent
    "hop3_personalize_signal",   # derive sender/lead personalization signals
    "hop4_retrieve_context",     # C0: retrieve company KB + lead context
    "hop5_generate_draft",       # L2: Qwen32B draft generation
    "hop6_validate_draft",       # validate: structure + evidence + compliance
    "hop7_gate_decision",        # gate: pass / fail / escalate
    "hop8_qa_report",            # assemble QA/rubric report
    "hop9_integrate",            # assemble final run record
)

_OUTREACH_MESSAGE_REQUIRED_CAPABILITIES: tuple[str, ...] = (
    "llm.text_generation",            # Qwen32B primary model call
    "retrieval.company_kb",           # C0 company knowledge base
    "retrieval.lead_profile",         # C0 verified lead profile lookup
    "prompt_assembly.template",       # PA template-driven prompt composition
    "schema_validation.outreach",     # Exit output validation
    "governance.pii_detection",       # PII shield
    "governance.compliance_check",    # compliance/antipattern check
)

# Required app_payload top-level keys. Missing keys raise ValueError so L1
# fails closed before producing an under-specified plan.
_REQUIRED_APP_PAYLOAD_KEYS: tuple[str, ...] = (
    "transport",
    "campaign",
    "forbidden_send_modes",
    "entity_refs",
    "pii_policy",
    "governance_shield",
    "antipattern_policy",
    "source_lineage",
    "hitl_policy",
    "gate_decision_policy",
)


def _coerce_str(v: object) -> str:
    """Coerce an enum or string value to plain str."""
    if hasattr(v, "value"):
        return str(v.value)
    return str(v) if v is not None else ""


def _build_app_payload_projections(
    app_payload: Mapping[str, Any],
) -> tuple[
    Mapping[str, Any],   # task_spec
    Mapping[str, Any],   # query_spec
    Mapping[str, Any],   # support_expectation
    Mapping[str, Any],   # output_expectation
    Mapping[str, str],   # policy_refs
    Mapping[str, Any],   # route_hints (advisory)
    bool,                 # grounding_required (derived from app_payload)
    bool,                 # model_generation_required
    bool,                 # write_authority_present
]:
    """Project ValidatedRequest.app_payload into L1PlanContract projections.

    All five canonical projections + two apps_lic-specific extras are read-only
    views of app_payload. L1 NEVER mutates app_payload.

    Raises:
        ValueError: when a required app_payload key is missing.
    """
    missing = [k for k in _REQUIRED_APP_PAYLOAD_KEYS if k not in app_payload]
    if missing:
        raise ValueError(
            f"l1_plan_apps_lic: app_payload missing required keys: {missing}. "
            "AG-8 W4 invariant requires U0 reflection harness to populate the "
            "full apps_lic ingress contract — was apps_lic_u0_adapt skipped?"
        )

    transport = app_payload["transport"]
    campaign = app_payload["campaign"]
    entity_refs = app_payload["entity_refs"]
    pii = app_payload["pii_policy"]
    shield = app_payload["governance_shield"]
    antipattern = app_payload["antipattern_policy"]
    source_lineage = app_payload["source_lineage"]
    hitl = app_payload["hitl_policy"]
    gate_policy = app_payload["gate_decision_policy"]
    research_req = app_payload.get("research_requirements", {})
    tone = app_payload.get("tone_constraints", {})
    output_fmt = app_payload.get("output_format", {})
    personalization = app_payload.get("personalization", {})
    generation_hints = app_payload.get("generation_hints", {})

    # Derive canonical flags from payload
    grounding_required: bool = bool(campaign.get("grounding_required", True))
    side_effect_class: str = _coerce_str(campaign.get("side_effect_class", "read_only"))
    if side_effect_class != "read_only":
        raise ValueError(
            f"l1_plan_apps_lic: side_effect_class must be 'read_only'; "
            f"got {side_effect_class!r} — U0 should have blocked this"
        )
    workflow_required: bool = (
        _coerce_str(campaign.get("workflow_required", "")) == "managed_workflow_hop"
    )
    action_required_str: str = _coerce_str(campaign.get("action_required", "draft_and_cert"))

    # model_generation_required: always True for outreach_message (LLM draft)
    model_generation_required: bool = True
    # write_authority_present: apps_lic never mutates durable state at generation time
    write_authority_present: bool = False

    # ── 1. task_spec ─────────────────────────────────────────────────────────
    # Research authorization flags (read from research_requirements sub-section)
    allow_research: bool = bool(research_req.get("allow_research", False))
    research_disabled_by_policy: bool = bool(
        research_req.get("research_disabled_by_policy", False)
    )
    research_requested_but_disabled: bool = bool(
        research_req.get("requested_but_disabled", False)
    )
    apps_research_deprecated: bool = bool(
        research_req.get("apps_research_deprecated", False)
    )
    research_deprecation_reason: str = _coerce_str(
        research_req.get("deprecation_reason", "")
    )
    research_evidence_types: list[str] = list(
        research_req.get("research_evidence_types", research_req.get("required_evidence_types", []))
    )
    # Context freshness flags (advisory — sourced from campaign context_signals if present)
    context_signals = app_payload.get("context_signals", {})
    briefing_fresh: bool = bool(context_signals.get("briefing_fresh", False))
    lead_profile_valid: bool = bool(context_signals.get("lead_profile_valid", False))
    context_grounded: bool = bool(context_signals.get("context_grounded", False))

    task_spec: dict[str, Any] = {
        "task_class": _coerce_str(transport.get("task_class", "outreach_message")),
        "request_type": _coerce_str(campaign.get("request_type", "outreach_draft")),
        "channel": _coerce_str(campaign.get("channel", "email")),
        "action_required": action_required_str,
        "workflow_required": workflow_required,
        "grounding_required": grounding_required,
        "side_effect_class": side_effect_class,
        "campaign_objective": campaign.get("campaign_objective", ""),
        # Research authorization (L0 routing decision inputs)
        "allow_research": allow_research,
        "research_disabled_by_policy": research_disabled_by_policy,
        "research_requested_but_disabled": research_requested_but_disabled,
        "apps_research_deprecated": apps_research_deprecated,
        "research_deprecation_reason": research_deprecation_reason,
        "research_evidence_types": research_evidence_types,
        # Context freshness (L0 routing decision inputs)
        "briefing_fresh": briefing_fresh,
        "lead_profile_valid": lead_profile_valid,
        "context_grounded": context_grounded,
    }

    # ── 2. query_spec ─────────────────────────────────────────────────────────
    lead_profile = entity_refs.get("lead_profile") or {}
    sender_profile = entity_refs.get("sender_profile") or {}
    query_spec: dict[str, Any] = {
        "lead_anchor": {
            "verified_name": lead_profile.get("verified_name", ""),
            "title": lead_profile.get("title", ""),
            "seniority_class": lead_profile.get("seniority_class", ""),
            "company_name": lead_profile.get("company_name", ""),
            "industry": lead_profile.get("industry", ""),
            "consent_attested": bool(lead_profile.get("consent_attested", False)),
        },
        "lead_ref": entity_refs.get("lead_ref"),
        "sender_anchor": {
            "sender_id": sender_profile.get("sender_id", ""),
            "name": sender_profile.get("name", ""),
            "title": sender_profile.get("title", ""),
        },
        "sender_ref": entity_refs.get("sender_ref"),
        "campaign_objective": campaign.get("campaign_objective", ""),
        "audience_segment": campaign.get("audience_segment", ""),
        "personalization_inputs": dict(personalization.get("inputs", {})),
    }

    # ── 3. support_expectation ────────────────────────────────────────────────
    support_expectation: dict[str, Any] = {
        "grounding_required": grounding_required,
        "research_freshness_class": research_req.get("freshness_class", ""),
        "hitl_required": not bool(hitl.get("bypass_hitl_freeze", False)),
        "pii_detection_mode": pii.get("pii_detection_mode", "strict"),
        "fail_on_pii_detect": bool(pii.get("fail_on_pii_detect", True)),
        "governance_shield_required": bool(shield.get("shield_required", True)),
        "antipattern_detection_enabled": bool(antipattern.get("enabled", True)),
        "source_lineage_required": bool(source_lineage.get("source_lineage_required", True)),
        "halt_on_validation_failure": bool(gate_policy.get("halt_on_validation_failure", True)),
    }

    # ── 4. output_expectation ─────────────────────────────────────────────────
    output_expectation: dict[str, Any] = {
        "channel": _coerce_str(campaign.get("channel", "email")),
        "tone_brand_voice_id": tone.get("brand_voice_id", ""),
        "tone_register": _coerce_str(tone.get("tone_register", "")),
        "formality_level": tone.get("formality_level"),
        "output_format": dict(output_fmt),
        "generation_hints": dict(generation_hints),
        "gate_halt_on_validation_failure": bool(
            gate_policy.get("halt_on_validation_failure", True)
        ),
    }

    # ── 5. policy_refs ────────────────────────────────────────────────────────
    policy_refs: dict[str, str] = {
        "hitl_policy_ref": "apps_lic/config/hitl_policy.yaml",
        "pii_policy_ref": "apps_lic/config/l0_policy.yaml#pii",
        "governance_shield_ref": "apps_lic/config/l0_policy.yaml#governance_shield",
        "antipattern_policy_ref": "apps_lic/config/l0_policy.yaml#antipattern",
        "source_lineage_ref": "apps_lic/config/l0_policy.yaml#source_lineage",
        "capability_profile_ref": "apps_lic/config/domain_contract/capability_profiles.yaml",
        "route_profile_ref": "apps_lic/config/domain_contract/route_profiles.yaml",
        "intake_policy_ref": "apps_lic/config/intake_policy.yaml",
    }

    # ── advisory route_hints (L0 DOES NOT bind to these for deterministic routing)
    route_hints: dict[str, Any] = {
        "audience_segment": campaign.get("audience_segment", ""),
        "channel": _coerce_str(campaign.get("channel", "email")),
        "request_type": _coerce_str(campaign.get("request_type", "outreach_draft")),
        "ab_test_profile": app_payload.get("ab_test", {}).get("ab_test_profile"),
        "advisory": True,
    }

    return (
        task_spec,
        query_spec,
        support_expectation,
        output_expectation,
        policy_refs,
        route_hints,
        grounding_required,
        model_generation_required,
        write_authority_present,
    )


def _read_profile_digest(repo_root: Path) -> str:
    profile_path = repo_root / _PLANNING_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        return hashlib.sha256(profile_path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def l1_plan_apps_lic(validated_request: ValidatedRequest) -> L1PlanContract:
    """Emit an L1PlanContract for an apps_lic ValidatedRequest.

    Args:
        validated_request: U0 output carrying the authority-validated payload,
            app_payload, reflection_receipt, request/run/trace identity.

    Returns:
        L1PlanContract with task_plan, required_capabilities, five projection
        mappings (task_spec, query_spec, support_expectation, output_expectation,
        policy_refs), route_hints, and routing flags derived from app_payload.

    Raises:
        TypeError: if validated_request is not a ValidatedRequest.
        ValueError: if task_class != 'outreach_message' or app_id != 'apps_lic',
            or if app_payload is missing required keys.
    """
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            "l1_plan_apps_lic expected ValidatedRequest, got "
            f"{type(validated_request).__name__}"
        )
    if validated_request.task_class != "outreach_message":
        raise ValueError(
            f"l1_plan_apps_lic only handles task_class='outreach_message'; "
            f"got {validated_request.task_class!r}"
        )
    if validated_request.app_id != "apps_lic":
        raise ValueError(
            f"l1_plan_apps_lic expected app_id='apps_lic'; "
            f"got {validated_request.app_id!r}"
        )
    if not validated_request.app_payload:
        raise ValueError(
            "l1_plan_apps_lic: app_payload is empty — U0 must populate it. "
            "AG-8 W4 hard law: L1 reads app_payload, never envelope.payload."
        )

    profile_digest = _read_profile_digest(_resolve_repo_root())

    (
        task_spec,
        query_spec,
        support_expectation,
        output_expectation,
        policy_refs,
        route_hints,
        grounding_required,
        model_generation_required,
        write_authority_present,
    ) = _build_app_payload_projections(validated_request.app_payload)

    lead_anchor = query_spec.get("lead_anchor") or {}
    target_level = str(lead_anchor.get("seniority_class", "") or "")

    return L1PlanContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        tenant_id=validated_request.tenant_id,
        target_level=target_level,
        task_plan=_OUTREACH_MESSAGE_TASK_PLAN,
        required_capabilities=_OUTREACH_MESSAGE_REQUIRED_CAPABILITIES,
        grounding_required=grounding_required,
        model_generation_required=model_generation_required,
        write_authority_present=write_authority_present,
        profile_manifest_digest=profile_digest,
        task_spec=task_spec,
        query_spec=query_spec,
        support_expectation=support_expectation,
        output_expectation=output_expectation,
        policy_refs=policy_refs,
        replay_key=validated_request.replay_key,
        planning_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-8.W4.f3c2e1",
        l5_certification_ref=APPS_LIC_L1_CERT_REF,
    )


__all__ = [
    "APPS_LIC_L1_CERT_REF",
    "l1_plan_apps_lic",
]
