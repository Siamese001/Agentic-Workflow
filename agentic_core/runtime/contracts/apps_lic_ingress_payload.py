"""AppsLicIngressPayload — typed ingress produced by apps_lic CLI, consumed by core U0.

Path: agentic_core/runtime/contracts/apps_lic_ingress_payload.py

This module defines:
  - AppsLicIngressPayload: frozen dataclass produced by apps_lic CLI/wizard.
  - AppsLicRequestEnvelope: transport wrapper consumed by AppIngressRunner /
    u0_validate_apps_lic.
  - AppsLicValidatedRequest: U0 output carrying app_payload + reflection_receipt +
    authority receipt. Reuses the shared ValidatedRequest shape already defined
    in apps_rg_ingress_payload.py — apps_lic U0 produces a ValidatedRequest
    (the spine-shared type) not a custom subtype, so downstream L1..Exit
    bindings can consume it without knowing which app produced it.

NOTE: The spine-shared ValidatedRequest lives in apps_rg_ingress_payload.py
because apps_rg was the golden-path pioneer. apps_lic U0 ALSO produces a
ValidatedRequest of that same type. This file defines the apps_lic *ingress*
shape only (the CLI-emitted payload and its envelope). The adapter
(agentic_core/runtime/u0/apps_lic_u0_adapter.py) is responsible for
synthesizing the shared ValidatedRequest from the apps_lic-specific contract.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W3)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(frozen=True, slots=True)
class AppsLicIngressPayload:
    """Declarative ingress payload from apps_lic CLI or wizard.

    This contract is the ONLY runtime input apps_lic may produce at U0 ingress.
    It contains campaign intent, entity references, governance policy overrides,
    personalization signals, and replay/audit linkage.

    It MUST NOT contain any runtime authority fields (route_id, execution_form,
    provider, workflow DAG node assignments, etc.).

    Populated by apps_lic CLI/wizard (ingress-only) and consumed by core U0.
    """

    # Identity
    app_id: str = "apps_lic"
    task_class: str = "outreach_message"

    # Campaign intent (F-02, F-03, F-10, F-11, F-33..F-35)
    request_type: str = "outreach_draft"
    campaign_objective: Optional[str] = None
    channel: str = "email"
    audience_segment: Optional[str] = None
    action_required: str = "draft_and_cert"
    workflow_required: str = "managed_workflow_hop"
    grounding_required: bool = True
    side_effect_class: str = "read_only"

    # Entity references — inline profiles OR reference keys (F-04..F-09)
    lead_profile: Mapping[str, Any] = field(default_factory=dict)
    lead_ref: Optional[str] = None
    sender_profile: Mapping[str, Any] = field(default_factory=dict)
    sender_ref: Optional[str] = None
    company_profile: Mapping[str, Any] = field(default_factory=dict)
    company_ref: Optional[str] = None

    # Personalization + generation hints (F-12, F-15, F-16, F-29)
    personalization_inputs: Mapping[str, Any] = field(default_factory=dict)
    generation_hints: Mapping[str, Any] = field(default_factory=dict)
    tone_constraints: Mapping[str, Any] = field(default_factory=dict)
    required_output_format: Mapping[str, Any] = field(default_factory=dict)

    # Research + routing + validation + gate + QA + integration (F-13, F-14, F-18..F-21)
    research_requirements: Mapping[str, Any] = field(default_factory=dict)
    routing_policy: Mapping[str, Any] = field(default_factory=dict)
    validation_policy: Mapping[str, Any] = field(default_factory=dict)
    gate_decision_policy: Mapping[str, Any] = field(default_factory=dict)
    qa_report_requirement: Mapping[str, Any] = field(default_factory=dict)
    integration_target: Optional[str] = None

    # Governance (F-17, F-22..F-25, F-28) — cannot be disabled
    forbidden_send_modes: tuple[str, ...] = field(
        default_factory=lambda: (
            "send_now",
            "auto_send",
            "connector_send",
            "email_outbox_send",
            "linkedin_send",
            "sms_send",
            "external_http_post",
        )
    )
    hitl_policy: Mapping[str, Any] = field(default_factory=dict)
    pii_policy: Mapping[str, Any] = field(default_factory=dict)
    governance_shield_policy: Mapping[str, Any] = field(default_factory=dict)
    antipattern_policy: Mapping[str, Any] = field(default_factory=dict)
    source_lineage_requirements: Mapping[str, Any] = field(default_factory=dict)

    # A/B + learning (F-26, F-27)
    ab_test_profile: Optional[str] = None
    learning_profile_ref: Optional[str] = None

    # Replay, audit, idempotency (F-31, F-32, F-36)
    replay_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    idempotency_key: Optional[str] = None

    # Integrity — computed at ingress time (F-37)
    payload_digest: str = ""


@dataclass(frozen=True, slots=True)
class AppsLicRequestEnvelope:
    """Transport wrapper for AppsLicIngressPayload.

    Carries the ingress payload plus identity/trace metadata so the U0
    adapter can stamp a receipt without mutating the frozen payload.
    Mirrors the shape of apps_rg RequestEnvelope.
    """

    payload: AppsLicIngressPayload
    request_id: str = ""
    run_id: str = ""
    tenant_id: str = ""
    trace_id: str = ""
    submitted_at: str = ""


__all__ = [
    "AppsLicIngressPayload",
    "AppsLicRequestEnvelope",
]
