"""AppsRgIngressPayload — typed ingress produced by apps_rg CLI, consumed by core U0.

Path: agentic_core/runtime/contracts/apps_rg_ingress_payload.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping, Optional

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_READ_ONLY

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
    briefing_artifact_ref: Optional[str] = None
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

    # L5 Certification reference (optional for ingress, validated at U0)
    l5_certification_ref: Optional[str] = None

    def __post_init__(self) -> None:
        # Basic invariant: at least one of target_company or target_role required for context
        if not self.target_company and not self.target_role:
            if not self.source_resume_ref and not self.source_resume_text:
                raise ValueError(
                    "AppsRgIngressPayload: at least one of (target_company, target_role) "
                    "or (source_resume_ref, source_resume_text) is required"
                )


@dataclass(frozen=True, slots=True)
class RequestEnvelope:
    """Canonical request envelope wrapping AppsRgIngressPayload for runtime entry.

    Per plan apps-rg-runtime-wiring-completion-d4e8a1 §5 (re-opens c8b3e1).
    Adds the dataclass that c8b3e1 plan §13 line 717 referenced as
    "Duplicate RequestEnvelope removed (L5 canonical retained)" — this is
    the apps_rg ingress envelope shape that AppIngressRunner.run() consumes.

    Carries the ingress payload + identity/trace metadata so U0 ingress
    validator can stamp a receipt without mutating the frozen payload.
    """

    payload: AppsRgIngressPayload
    request_id: str = ""
    run_id: str = ""
    tenant_id: str = ""  # W1: identity quad — sourced from app_id at U0 ingress (D6)
    trace_id: str = ""
    submitted_at: str = ""  # ISO-8601 timestamp
    # 00A.6 replay binding — optional envelope-level override; U0 falls back to
    # idempotency-derived key when empty (see u0_validate_apps_rg).
    replay_key: str = ""


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
    tenant_id: str = ""  # W1: identity quad — app_id value at U0 ingress (D6)
    # W2: target level for L0 variant routing (DS-3)
    target_level: str = ""  # "SENIOR" | "STAFF" | "EXECUTIVE" | ""
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.1: standardized schema_version field (D8)
    schema_version: str = "W6.0"
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7; U0 validates only, read_only)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
    # W6 P6.3: gate verdict refs (concern #3)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_certification_ref: Optional[str] = None
    # apps-rg-u0-reflection-harness-79d032 W2.P2.1: full apps_rg domain payload
    # preserved verbatim from the validated ingress contract. Default empty so
    # this field is additive — existing call sites that construct
    # ValidatedRequest without it continue to work unchanged. The U0 reflection
    # adapter is the only producer that populates this with the validated
    # AppsRgIngressContractV1 dump.
    #
    # p3.1 (apps-rg-l1-contract-wiring): when populated by ``u0_validate_apps_rg``,
    # ``app_payload["profile_manifest"]`` SHOULD include ``l1_planning_profile_ref``
    # (repo-relative path) and ``l1_planning_profile_digest`` (64-char sha256 of that
    # file) so ``l1_plan_apps_rg`` can fail-closed on digest mismatch.
    app_payload: Mapping[str, Any] = field(default_factory=dict)
    # apps-rg-u0-reflection-live-wiring-105147 W1.P1.3: reflection receipt
    # produced by ``apps_rg_u0_adapt`` when the harness is on the live path.
    # Typed as ``Any`` to avoid a circular import (the receipt lives under
    # ``agentic_core.runtime.u0`` which imports from this module). The
    # concrete type is ``AppsRgU0ReflectionReceipt``. Default ``None`` keeps
    # the field additive — pre-harness call sites are unaffected.
    reflection_receipt: Any = None
    # W1 spine U0 identity stamps (REQ-U0-IDENTITY-STAMP-001)
    session_id: str = ""
    trace_root: str = ""
    caller_scope_baseline: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"ValidatedRequest: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
