"""AppsLicIngressContractV1 — canonical apps_lic JSON ingress contract, version 1.

This is the SSOT shape apps_lic emits at U0 ingress. The U0 reflection adapter
(``agentic_core/runtime/u0/apps_lic_u0_adapter.py``) validates raw JSON against
this contract, enumerates every JSON Pointer, and proves each pointer maps to
a downstream consumer (MAPPED, DERIVED, REJECTED, or DEFERRED).

Core rule: a field may be deferred. A field may not disappear.

The contract is an exact structural transcription of the payload schema defined
in ``artifacts/apps_lic/ag8_apps_lic_payload_schema.json``. Fields not yet
consumed downstream must appear with status DEFERRED in the field map
``apps_lic_ingress_field_map.v1.yaml`` with an explicit reason. Adding a field
to this contract WITHOUT adding a field-map row fails the harness closed.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W3)
Schema ref: artifacts/apps_lic/ag8_apps_lic_payload_schema.json
"""
from __future__ import annotations

import enum
from typing import Any, List, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from typing_extensions import Annotated


APPS_LIC_INGRESS_CONTRACT_VERSION: str = "v1"
"""Canonical version string. The field-map filename embeds this string."""


# ---------------------------------------------------------------------------
# Governed value enumerations
# ---------------------------------------------------------------------------


class RequestType(str, enum.Enum):
    OUTREACH_DRAFT = "outreach_draft"
    CAMPAIGN_BATCH = "campaign_batch"
    DRY_RUN = "dry_run"


class Channel(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    CHAT = "chat"
    SMS = "sms"
    OTHER_GOVERNED = "other_governed"


class OutreachMode(str, enum.Enum):
    COLD = "cold"
    WARM = "warm"
    REENGAGEMENT = "reengagement"


class ActionRequired(str, enum.Enum):
    DRAFT_ONLY = "draft_only"
    DRAFT_AND_REVIEW = "draft_and_review"
    DRAFT_AND_CERT = "draft_and_cert"


class SideEffectClass(str, enum.Enum):
    READ_ONLY = "read_only"


class WorkflowRequired(str, enum.Enum):
    MANAGED_WORKFLOW_HOP = "managed_workflow_hop"


class LengthClass(str, enum.Enum):
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


class CtaStyle(str, enum.Enum):
    SOFT = "soft"
    DIRECT = "direct"


class ToneRegister(str, enum.Enum):
    EXECUTIVE = "executive"
    PEER = "peer"
    CONSULTATIVE = "consultative"
    DIRECT = "direct"


class PiiDetectionMode(str, enum.Enum):
    STRICT = "strict"
    STANDARD = "standard"


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

_NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
_CampaignObjective = Annotated[str, StringConstraints(min_length=5, max_length=500, strip_whitespace=True)]


# ---------------------------------------------------------------------------
# Base model — frozen, extra=forbid (fail-closed on unknown keys)
# ---------------------------------------------------------------------------


class _ImmutableModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# ---------------------------------------------------------------------------
# Sub-shapes: identity (transport)
# ---------------------------------------------------------------------------


class TransportSection(_ImmutableModel):
    """Identity-quad + trace metadata."""

    app_id: _NonEmptyStr = Field(description="MUST be 'apps_lic'.")
    task_class: _NonEmptyStr = Field(description="MUST be 'outreach_message'.")
    request_id: _NonEmptyStr
    run_id: _NonEmptyStr
    tenant_id: _NonEmptyStr
    trace_id: str = ""
    submitted_at: str = ""

    @field_validator("app_id")
    @classmethod
    def _app_id_must_be_apps_lic(cls, v: str) -> str:
        if v != "apps_lic":
            raise ValueError(f"app_id must be 'apps_lic'; got {v!r}")
        return v

    @field_validator("task_class")
    @classmethod
    def _task_class_must_be_outreach_message(cls, v: str) -> str:
        if v != "outreach_message":
            raise ValueError(f"task_class must be 'outreach_message'; got {v!r}")
        return v


# ---------------------------------------------------------------------------
# Sub-shapes: campaign intent
# ---------------------------------------------------------------------------


class CampaignSection(_ImmutableModel):
    """Campaign-level intent and context."""

    request_type: RequestType
    campaign_objective: _CampaignObjective
    channel: Channel
    audience_segment: Optional[str] = None
    action_required: ActionRequired = ActionRequired.DRAFT_AND_CERT
    workflow_required: WorkflowRequired = WorkflowRequired.MANAGED_WORKFLOW_HOP
    grounding_required: bool = True
    side_effect_class: SideEffectClass = SideEffectClass.READ_ONLY

    @field_validator("side_effect_class")
    @classmethod
    def _side_effect_must_be_read_only(cls, v: SideEffectClass) -> SideEffectClass:
        if v != SideEffectClass.READ_ONLY:
            raise ValueError("side_effect_class must be 'read_only' (NB-3 invariant)")
        return v

    @field_validator("workflow_required")
    @classmethod
    def _workflow_must_be_hop(cls, v: WorkflowRequired) -> WorkflowRequired:
        if v != WorkflowRequired.MANAGED_WORKFLOW_HOP:
            raise ValueError("workflow_required must be 'managed_workflow_hop'")
        return v


# ---------------------------------------------------------------------------
# Sub-shapes: entity references (lead / sender / company)
# ---------------------------------------------------------------------------


class LeadProfileSection(_ImmutableModel):
    """Verified inline lead profile."""

    verified_name: _NonEmptyStr
    title: Optional[str] = None
    seniority_class: str = "UNKNOWN"
    company_name: Optional[str] = None
    industry: Optional[str] = None
    consent_attested: bool = False

    @field_validator("consent_attested")
    @classmethod
    def _consent_must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("consent_attested must be True — unconsented profiles are forbidden")
        return v


class SenderProfileSection(_ImmutableModel):
    """Inline sender (rep) profile."""

    sender_id: _NonEmptyStr
    name: Optional[str] = None
    title: Optional[str] = None
    voice_profile_id: Optional[str] = None
    territory: Optional[str] = None


class CompanyProfileSection(_ImmutableModel):
    """Inline target company profile."""

    company_name: _NonEmptyStr
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    recent_news_summary: Optional[str] = None
    competitive_position: Optional[str] = None


class EntityRefsSection(_ImmutableModel):
    """Entity reference block — inline profiles or reference keys.

    At most one of (lead_profile, lead_ref) may be provided.
    At most one of (sender_profile, sender_ref) may be provided.
    At most one of (company_profile, company_ref) may be provided.
    """

    lead_profile: Optional[LeadProfileSection] = None
    lead_ref: Optional[str] = None
    sender_profile: Optional[SenderProfileSection] = None
    sender_ref: Optional[str] = None
    company_profile: Optional[CompanyProfileSection] = None
    company_ref: Optional[str] = None


# ---------------------------------------------------------------------------
# Sub-shapes: generation and personalization hints
# ---------------------------------------------------------------------------


class PersonalizationSection(_ImmutableModel):
    """Caller-supplied personalization signals.

    All keys must be explicitly declared — no open-vocabulary keys whose
    prefixes match FORBIDDEN_PERSONALIZATION_PREFIXES are permitted.
    """

    inputs: Mapping[str, Any] = Field(default_factory=dict)

    @field_validator("inputs")
    @classmethod
    def _forbid_unconsented_keys(cls, v: Mapping[str, Any]) -> Mapping[str, Any]:
        _FORBIDDEN_PREFIXES = ("inferred_", "scraped_", "unconsented_", "raw_pii_")
        bad = [k for k in v if any(k.startswith(p) for p in _FORBIDDEN_PREFIXES)]
        if bad:
            raise ValueError(
                f"personalization_inputs contains forbidden keys: {bad}. "
                "Keys with prefixes inferred_/scraped_/unconsented_/raw_pii_ are forbidden."
            )
        return v


class GenerationHintsSection(_ImmutableModel):
    """Caller generation hints."""

    preferred_length_class: Optional[LengthClass] = None
    require_differentiator: bool = False
    subject_line_constraints: Optional[str] = None
    cta_style: Optional[CtaStyle] = None


class ToneConstraintsSection(_ImmutableModel):
    """Tone and brand-voice constraints."""

    brand_voice_id: Optional[str] = None
    tone_register: Optional[ToneRegister] = None
    formality_level: Optional[int] = None

    @field_validator("formality_level")
    @classmethod
    def _formality_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("formality_level must be between 1 and 5")
        return v


class OutputFormatSection(_ImmutableModel):
    """Output format constraints."""

    include_subject_line: bool = True
    include_ps_line: bool = False
    max_paragraphs: Optional[int] = None
    bullet_list_allowed: bool = True
    output_schema_ref: Optional[str] = None

    @field_validator("max_paragraphs")
    @classmethod
    def _max_paragraphs_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 10):
            raise ValueError("max_paragraphs must be between 1 and 10")
        return v


# ---------------------------------------------------------------------------
# Sub-shapes: policy sections
# ---------------------------------------------------------------------------


class ResearchRequirementsSection(_ImmutableModel):
    """Research stage hints."""

    required_evidence_types: List[str] = Field(default_factory=list)
    freshness_class: str = "any"
    max_sources: Optional[int] = None
    prohibited_source_types: List[str] = Field(default_factory=list)


class RoutingPolicySection(_ImmutableModel):
    """Routing hints for HOP4."""

    preferred_template_family: Optional[str] = None
    allow_fallback_template: bool = True
    outreach_mode: Optional[OutreachMode] = None


class ValidationPolicySection(_ImmutableModel):
    """ValidationEngine policy hints."""

    min_body_length: int = 20
    max_body_length: int = 4000
    require_grounded: bool = True
    evidence_coverage_min: float = 0.0

    @field_validator("min_body_length")
    @classmethod
    def _min_body_length_bounds(cls, v: int) -> int:
        if not (1 <= v <= 50):
            raise ValueError("min_body_length must be between 1 and 50")
        return v

    @field_validator("max_body_length")
    @classmethod
    def _max_body_length_bounds(cls, v: int) -> int:
        if v > 4000:
            raise ValueError("max_body_length must be <= 4000")
        return v


class GateDecisionPolicySection(_ImmutableModel):
    """GateDecisionEngine policy."""

    halt_on_validation_failure: bool = True
    warn_only_dims: List[str] = Field(default_factory=list)

    @field_validator("halt_on_validation_failure")
    @classmethod
    def _halt_must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "halt_on_validation_failure cannot be False — "
                "gate must always halt on validation failure"
            )
        return v


class QaReportSection(_ImmutableModel):
    """QA report generation config."""

    include_evidence_audit: bool = True
    include_dim_scores: bool = True
    include_omission_log: bool = True


class HitlPolicySection(_ImmutableModel):
    """HITL freeze policy at request level.

    bypass_hitl_freeze is structurally accepted here but U0 enforces that
    the HITL_FREEZE_BYPASS env var is present before propagating it.
    The governance-fields-cannot-be-disabled test targets this section.
    """

    bypass_hitl_freeze: bool = False
    confidence_override_threshold: Optional[float] = None


class PiiPolicySection(_ImmutableModel):
    """PII detection policy. Detection cannot be disabled."""

    pii_detection_mode: PiiDetectionMode = PiiDetectionMode.STRICT
    redact_on_warn: bool = True
    fail_on_pii_detect: bool = True

    @field_validator("fail_on_pii_detect")
    @classmethod
    def _pii_detection_cannot_be_disabled(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "fail_on_pii_detect cannot be False — "
                "PII detection must be active (governance field)"
            )
        return v


class GovernanceShieldSection(_ImmutableModel):
    """GovernanceShieldAgent policy. Cannot be disabled."""

    shield_required: bool = True
    policy_profile_id: Optional[str] = None

    @field_validator("shield_required")
    @classmethod
    def _shield_cannot_be_disabled(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "shield_required cannot be False — "
                "governance shield must remain active (governance field)"
            )
        return v


class AntipatternPolicySection(_ImmutableModel):
    """Antipattern detector policy. Cannot be disabled."""

    enabled: bool = True
    extended_patterns: List[str] = Field(default_factory=list)

    @field_validator("enabled")
    @classmethod
    def _antipattern_cannot_be_disabled(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "antipattern_policy.enabled cannot be False — "
                "antipattern detection must remain active"
            )
        return v


class SourceLineageSection(_ImmutableModel):
    """Source lineage requirements."""

    source_lineage_required: bool = True
    required_source_types: List[str] = Field(default_factory=list)
    prohibited_source_types: List[str] = Field(default_factory=list)

    @field_validator("source_lineage_required")
    @classmethod
    def _lineage_cannot_be_disabled(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "source_lineage_required cannot be False — "
                "source lineage is mandatory"
            )
        return v


class ForbiddenSendModesSection(_ImmutableModel):
    """Forbidden send-mode blocklist.

    The three always-forbidden modes are enforced by U0; caller may add more.
    """

    modes: List[str] = Field(
        default_factory=lambda: ["send_now", "auto_send", "connector_send"]
    )

    @field_validator("modes")
    @classmethod
    def _must_contain_hardcoded_three(cls, v: List[str]) -> List[str]:
        _REQUIRED = {"send_now", "auto_send", "connector_send"}
        missing = _REQUIRED - set(v)
        if missing:
            raise ValueError(
                f"forbidden_send_modes must include {sorted(_REQUIRED)}; "
                f"missing: {sorted(missing)}"
            )
        return v


# ---------------------------------------------------------------------------
# Sub-shapes: A/B, learning, idempotency, replay, audit
# ---------------------------------------------------------------------------


class AbTestSection(_ImmutableModel):
    """A/B test and learning profile bindings."""

    ab_test_profile: Optional[str] = None
    learning_profile_ref: Optional[str] = None


class ReplayAuditSection(_ImmutableModel):
    """Replay, idempotency, and audit linkage."""

    idempotency_key: Optional[str] = None
    replay_refs: List[str] = Field(default_factory=list)
    audit_refs: List[str] = Field(default_factory=list)

    @field_validator("idempotency_key")
    @classmethod
    def _idempotency_key_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 128:
            raise ValueError("idempotency_key must be <= 128 chars")
        return v

    @field_validator("replay_refs")
    @classmethod
    def _replay_refs_max(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError("replay_refs must contain <= 5 entries")
        return v

    @field_validator("audit_refs")
    @classmethod
    def _audit_refs_max(cls, v: List[str]) -> List[str]:
        if len(v) > 20:
            raise ValueError("audit_refs must contain <= 20 entries")
        return v


# ---------------------------------------------------------------------------
# Root contract
# ---------------------------------------------------------------------------


class AppsLicIngressContractV1(_ImmutableModel):
    """apps_lic v1 ingress contract — the ONLY shape apps_lic emits at U0.

    Structured into named sections that mirror the payload schema F-xx fields
    and HOP DAG stages. Every section is optional at the Pydantic level;
    U0 enforces field-level requirements per the E1-E7 exit conditions.
    """

    apps_lic_contract_version: str = APPS_LIC_INGRESS_CONTRACT_VERSION

    # Required sections
    transport: TransportSection
    campaign: CampaignSection
    forbidden_send_modes: ForbiddenSendModesSection = Field(
        default_factory=ForbiddenSendModesSection
    )

    # Entity references
    entity_refs: EntityRefsSection = Field(default_factory=EntityRefsSection)

    # Personalization + generation hints
    personalization: PersonalizationSection = Field(
        default_factory=PersonalizationSection
    )
    generation_hints: GenerationHintsSection = Field(
        default_factory=GenerationHintsSection
    )
    tone_constraints: ToneConstraintsSection = Field(
        default_factory=ToneConstraintsSection
    )
    output_format: OutputFormatSection = Field(default_factory=OutputFormatSection)

    # Policy sections
    research_requirements: ResearchRequirementsSection = Field(
        default_factory=ResearchRequirementsSection
    )
    routing_policy: RoutingPolicySection = Field(
        default_factory=RoutingPolicySection
    )
    validation_policy: ValidationPolicySection = Field(
        default_factory=ValidationPolicySection
    )
    gate_decision_policy: GateDecisionPolicySection = Field(
        default_factory=GateDecisionPolicySection
    )
    qa_report: QaReportSection = Field(default_factory=QaReportSection)
    integration_target: Optional[str] = None

    # Governance sections (cannot be disabled)
    hitl_policy: HitlPolicySection = Field(default_factory=HitlPolicySection)
    pii_policy: PiiPolicySection = Field(default_factory=PiiPolicySection)
    governance_shield: GovernanceShieldSection = Field(
        default_factory=GovernanceShieldSection
    )
    antipattern_policy: AntipatternPolicySection = Field(
        default_factory=AntipatternPolicySection
    )
    source_lineage: SourceLineageSection = Field(
        default_factory=SourceLineageSection
    )

    # A/B + learning
    ab_test: AbTestSection = Field(default_factory=AbTestSection)

    # Replay, audit, idempotency
    replay_audit: ReplayAuditSection = Field(default_factory=ReplayAuditSection)

    # Integrity — computed by caller's __post_init__ equivalent
    payload_digest: str = ""

    @field_validator("apps_lic_contract_version")
    @classmethod
    def _version_must_match(cls, v: str) -> str:
        if v != APPS_LIC_INGRESS_CONTRACT_VERSION:
            raise ValueError(
                f"apps_lic_contract_version must be {APPS_LIC_INGRESS_CONTRACT_VERSION!r}; got {v!r}"
            )
        return v


__all__ = [
    "APPS_LIC_INGRESS_CONTRACT_VERSION",
    "ActionRequired",
    "AntipatternPolicySection",
    "AppsLicIngressContractV1",
    "CampaignSection",
    "Channel",
    "CompanyProfileSection",
    "EntityRefsSection",
    "ForbiddenSendModesSection",
    "GateDecisionPolicySection",
    "GenerationHintsSection",
    "GovernanceShieldSection",
    "HitlPolicySection",
    "LeadProfileSection",
    "OutreachMode",
    "PersonalizationSection",
    "PiiPolicySection",
    "RequestType",
    "RoutingPolicySection",
    "SenderProfileSection",
    "SideEffectClass",
    "SourceLineageSection",
    "ToneConstraintsSection",
    "TransportSection",
    "ValidationPolicySection",
    "WorkflowRequired",
]
