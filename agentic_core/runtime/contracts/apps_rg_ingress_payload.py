"""AppsRgIngressPayload — typed ingress produced by apps_rg CLI, consumed by core U0.

Path: agentic_core/runtime/contracts/apps_rg_ingress_payload.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

if TYPE_CHECKING:
    from agentic_core.runtime.contracts.apps_rg_profile_manifest import AppsRgProfileManifest


@dataclass(frozen=True, slots=True)
class AppsRgIngressPayload:
    """Declarative ingress payload from apps_rg.

    This contract is the ONLY runtime input apps_rg may produce.
    It contains user intent, source references, constraints, and profile bindings.
    It MUST NOT contain any runtime authority fields (route_id, execution_form,
    provider, workflow DAG, etc.).

    Populated by apps_rg CLI/wizard (ingress-only) and consumed by core U0.
    """

    # Identity
    app_id: str = "apps_rg"
    task_class: str = "resume_generation"  # canonical task class for this app

    # CLI Input — Target context (provided by user via CLI or wizard)
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None

    # Source material (refs or inline text — at least one resume source required)
    source_resume_ref: Optional[str] = None  # Path to resume file
    source_resume_text: Optional[str] = None  # Inline resume text
    job_description_ref: Optional[str] = None  # Path to JD JSON
    job_description_text: Optional[str] = None  # Inline JD text
    candidate_profile_path: Optional[str] = None  # Path to candidate profile
    project_fact_refs: tuple[str, ...] = field(default_factory=tuple)

    # Research briefing (path to pre-built research JSON)
    manual_brief_path: Optional[str] = None

    # Research delegation flags
    auto_research_internal: bool = False
    auto_research_tavily: bool = False
    research_via: Optional[str] = None  # e.g., "apps_research"

    # User constraints and preferences
    user_constraints: Mapping[str, Any] = field(default_factory=dict)
    output_preferences: Mapping[str, Any] = field(default_factory=dict)

    # Profile manifest binding (digest-bound declarative profiles)
    profile_refs: "AppsRgProfileManifest" = field(default_factory=dict)  # Lazy: set by caller or post-init

    # Idempotency
    idempotency_key: Optional[str] = None

    # Integrity
    payload_digest: str = ""  # sha256 over canonical JSON of above fields

    def __post_init__(self) -> None:
        # Basic invariant: at least one of target_company or target_role required for context
        if not self.target_company and not self.target_role:
            if not self.source_resume_ref and not self.source_resume_text:
                raise ValueError(
                    "AppsRgIngressPayload: at least one of (target_company, target_role) "
                    "or (source_resume_ref, source_resume_text) is required"
                )


@dataclass(frozen=True, slots=True)
class ValidatedRequest:
    """U0 output after validating AppsRgIngressPayload.

    Proves that U0 has inspected the ingress payload and rejected any forbidden
    authority fields. The validated_request carries a receipt of that check.
    """

    request_id: str
    run_id: str
    app_id: str
    task_class: str
    payload_digest: str
    authority_validation_receipt: "AuthorityValidationReceipt"
    trace_id: str
