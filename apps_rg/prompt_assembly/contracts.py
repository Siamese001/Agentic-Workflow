"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit core runtime contracts or perform prompt assembly.

Original: apps_rg/prompt_assembly/contracts.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Emits CompiledPromptArtifact (core contract authority)

Importing this module raises RuntimeError immediately.
Core L1 Prompt Assembly owns all contract emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly.contracts is QUARANTINED. "
    "apps_rg may NOT emit CompiledPromptArtifact or other core contracts. "
    "Core L1 Prompt Assembly owns contract emission. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to:
# archives/apps_rg/quarantine_w4_20260509/prompt_assembly/contracts.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
"""PA contract types — ORIGINAL (QUARANTINED)
"""
# from __future__ import annotations

# Original imports (QUARANTINED):
# import enum
from dataclasses import dataclass, field
from typing import Any, Optional


class PACompileStatus(str, enum.Enum):
    """Status codes for the PA compilation pipeline."""

    PA_READY = "PA_READY"
    PA_INPUT_INCOMPLETE = "PA_INPUT_INCOMPLETE"
    PA_BOM_RESOLVED = "PA_BOM_RESOLVED"
    PA_BOM_GAP = "PA_BOM_GAP"
    PA_SLOTS_COMPOSED = "PA_SLOTS_COMPOSED"
    PA_SECURITY_PASS = "PA_SECURITY_PASS"
    PA_SECURITY_GAP = "PA_SECURITY_GAP"
    PA_SLOT_CONTRACT_VALID = "PA_SLOT_CONTRACT_VALID"
    PA_SLOT_CONTRACT_INVALID = "PA_SLOT_CONTRACT_INVALID"
    PA_BUDGET_FIT = "PA_BUDGET_FIT"
    PA_BUDGET_OVERFLOW = "PA_BUDGET_OVERFLOW"
    PA_RENDERED = "PA_RENDERED"
    PA_RENDER_GAP = "PA_RENDER_GAP"
    PA_ARTIFACT_SIGNED = "PA_ARTIFACT_SIGNED"
    PA_ARTIFACT_NOT_SIGNED = "PA_ARTIFACT_NOT_SIGNED"
    PA_L2_HANDOFF_READY = "PA_L2_HANDOFF_READY"
    PA_REQUIRES_UPSTREAM_REPAIR = "PA_REQUIRES_UPSTREAM_REPAIR"
    PA_COMPILE_FAILED = "PA_COMPILE_FAILED"
    PA_GUARD_FAILED = "PA_GUARD_FAILED"


@dataclass
class AppsRgPromptRequest:
    """Input request for PA compilation."""

    flow_route: str  # strategic_tailor | tailor_existing | generate_scratch | enhance_current
    jd_data: str
    master_resume_data: str
    company_brief_data: str = ""
    user_task: str = ""
    claim_source_refs: str = ""
    unsupported_claims: str = ""
    approved_resume_examples: str = ""
    seniority_band: str = ""
    target_company: str = ""
    target_role: str = ""
    local_evidence_contract_ref: str = ""
    run_id: str = ""
    trace_id: str = ""
    request_id: str = ""
    app_name: str = "apps_rg"
    route_id: str = "apps_rg.resume_generation_v1"
    provider_lane: str = "default"
    symbolic_model_id: str = ""
    output_schema_ref: str = "generated_resume.json"
    policy_hash: str = ""
    blueprint_hash: str = ""


@dataclass
class PromptSlotReceipt:
    """Receipt for a single slot mapping operation."""

    slot_name: str  # S0, I0, C0_jd, C0_resume, C0_brief, C0_refs, U0, R0
    source: str  # origin of the data
    char_count: int = 0
    was_fenced: bool = False  # True if untrusted data was fenced
    validation_passed: bool = True


@dataclass
class PromptCompileReceipt:
    """Receipt for the full PA compilation pipeline."""

    prompt_id: str = ""
    template_id: str = ""
    template_version: str = ""
    prompt_template_hash: str = ""
    prompt_bom_hash: str = ""
    prompt_registry_hash: str = ""
    prompt_hash: str = ""
    manifest_hash: str = ""
    artifact_hash: str = ""
    canonical_slot_bytes_hash: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""
    provider_lane: str = ""
    output_schema_hash: str = ""
    slot_receipts: list[PromptSlotReceipt] = field(default_factory=list)
    compile_status: str = PACompileStatus.PA_INPUT_INCOMPLETE.value
    token_budget_receipt: dict[str, Any] = field(default_factory=dict)
    source_refs: dict[str, str] = field(default_factory=dict)
    security_validation: str = ""
    error: str = ""


@dataclass
class AppsRgCompiledPromptArtifact:
    """Compiled prompt artifact for apps_rg model calls.

    Wire-compatible with any canonical ``CompiledPromptArtifact`` base.
    Every field required by the PA contract is present.
    """

    # Identity
    artifact_id: str = ""
    request_id: str = ""
    run_id: str = ""
    trace_id: str = ""
    app_name: str = "apps_rg"
    route_id: str = "apps_rg.resume_generation_v1"

    # Prompt identity
    prompt_id: str = ""
    template_id: str = ""
    template_version: str = ""
    prompt_template_hash: str = ""
    prompt_bom_hash: str = ""
    prompt_registry_hash: str = ""
    prompt_hash: str = ""
    manifest_hash: str = ""
    canonical_slot_bytes_hash: str = ""
    artifact_hash: str = ""

    # Governance
    policy_hash: str = ""
    blueprint_hash: str = ""
    replay_key: str = ""
    provider_lane: str = ""
    symbolic_model_id: str = ""

    # Origin / security
    origin_label_map: dict[str, str] = field(default_factory=dict)
    local_evidence_contract_ref: str = ""

    # Rendered content
    rendered_slots: dict[str, str] = field(default_factory=dict)
    structured_slots_used: list[str] = field(default_factory=list)
    provider_specific_messages: list[dict[str, Any]] = field(default_factory=list)

    # Schema
    output_schema_hash: str = ""
    output_schema_ref: str = ""

    # Source references
    source_refs: dict[str, str] = field(default_factory=dict)

    # Validation receipts
    origin_security_receipt: str = ""
    slot_validation_receipt: list[PromptSlotReceipt] = field(default_factory=list)
    token_budget_receipt: dict[str, Any] = field(default_factory=dict)
    render_receipt: str = ""
    audit_refs: dict[str, str] = field(default_factory=dict)

    # Status
    compile_status: str = PACompileStatus.PA_INPUT_INCOMPLETE.value

    def is_ready(self) -> bool:
        """Return True if artifact is ready for L2 handoff."""
        return self.compile_status == PACompileStatus.PA_L2_HANDOFF_READY.value

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-safe dict."""
        from dataclasses import asdict
        return asdict(self)


@dataclass
class AppsRgEvidenceBundle:
    """Evidence bundle for PA compilation — carries source data references."""

    jd_hash: str = ""
    master_resume_hash: str = ""
    company_brief_hash: str = ""
    claim_source_refs_hash: str = ""
    unsupported_claims_hash: str = ""


__all__ = [
    "AppsRgCompiledPromptArtifact",
    "AppsRgEvidenceBundle",
    "AppsRgPromptRequest",
    "PACompileStatus",
    "PromptCompileReceipt",
    "PromptSlotReceipt",
]
