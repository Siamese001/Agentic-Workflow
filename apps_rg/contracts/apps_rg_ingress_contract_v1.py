"""AppsRgIngressContractV1 — canonical apps_rg JSON ingress contract, version 1.

This is the SSOT shape apps_rg emits at U0 ingress. The U0 reflection adapter
(``agentic_core/runtime/u0/apps_rg_u0_adapter.py``) validates raw JSON against
this contract, enumerates every JSON Pointer, and proves each pointer maps to
a downstream consumer (MAPPED, DERIVED, REJECTED, or DEFERRED).

Core rule: a field may be deferred. A field may not disappear.

The contract is intentionally a SUPERSET of what is wired today. Fields not
yet consumed downstream MUST appear with status ``DEFERRED`` in the field map
``apps_rg_ingress_field_map.v1.yaml`` with an explicit reason. Adding a field
to the contract WITHOUT adding a field-map row fails the harness closed.

NOTE on filename: Python module names cannot contain dots, so the user-facing
versioned name "apps_rg_ingress_contract.v1" is implemented as the module
``apps_rg_ingress_contract_v1``. The contract version string ("v1") and the
generated schema/field-map filenames retain the dotted convention.

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md (W1.P1.1)
"""
from __future__ import annotations

import argparse
import enum
import json
import sys
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated


APPS_RG_INGRESS_CONTRACT_VERSION: str = "v1"
"""Canonical version string. The on-disk schema and field-map filenames embed
this string (``apps_rg_ingress_contract.v1.schema.json``,
``apps_rg_ingress_field_map.v1.yaml``)."""


class GenerationMode(str, enum.Enum):
    """The 8 generation modes apps_rg may request.

    Resolved per Author-Gate AG-3 (explicit user choice). The U0 adapter
    rejects any value outside this enum — see
    ``apps_rg_u0_adapter.UnknownGenerationModeError``.
    """

    STRATEGIC_TAILOR = "strategic_tailor"
    TAILOR_EXISTING = "tailor_existing"
    GENERATE_SCRATCH = "generate_scratch"
    ENHANCE_CURRENT = "enhance_current"
    HEALING_FACT_CHECK = "healing_fact_check"
    HEALING_UNSUPPORTED_CLAIM = "healing_unsupported_claim"
    REPAIR = "repair"


# ---------------------------------------------------------------------------
# Sub-shapes
# ---------------------------------------------------------------------------


_NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
_Sha256Hex = Annotated[str, StringConstraints(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")]


class _ImmutableModel(BaseModel):
    """Base for all sub-models — frozen, strict, extra=forbid (fail closed)."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",  # unknown keys at this level are rejected by Pydantic
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class TransportSection(_ImmutableModel):
    """Identity-quad + trace metadata."""

    app_id: _NonEmptyStr = Field(description="MUST be 'apps_rg'.")
    task_class: _NonEmptyStr = Field(description="Canonical task class — 'resume_generation' for apps_rg.")
    request_id: _NonEmptyStr = Field(description="Unique request id (ULID/UUID).")
    run_id: _NonEmptyStr = Field(description="Run id linking ingress → exit.")
    trace_id: _NonEmptyStr = Field(description="OTEL trace id.")
    submitted_at: _NonEmptyStr = Field(description="ISO-8601 submission timestamp.")
    tenant_id: _NonEmptyStr = Field(description="Tenant id (= app_id at this layer).")


class IdentitySection(_ImmutableModel):
    """Actor / authorization metadata."""

    actor_id: _NonEmptyStr
    actor_role: _NonEmptyStr


class ReplaySection(_ImmutableModel):
    """Idempotency + replay determinism."""

    replay_key: _NonEmptyStr = Field(description="Deterministic replay key — required, never empty.")
    idempotency_key: _NonEmptyStr


class JdPayloadSection(_ImmutableModel):
    """Job description payload — REQUIRED to carry jd_hash."""

    jd_hash: _Sha256Hex = Field(description="SHA-256 over canonical JD text. Required, never empty.")
    jd_text: _NonEmptyStr = Field(description="Inline JD text used to compute jd_hash.")
    jd_ref: str = Field(default="", description="Optional path/URL to source JD artifact.")
    jd_signals: Mapping[str, Any] = Field(default_factory=dict, description="Pre-extracted signals (seniority, role-type, etc.).")


class ResumePayloadSection(_ImmutableModel):
    """Source resume payload — at least one of text or ref required (validated above)."""

    resume_hash: _Sha256Hex
    source_resume_text: str = Field(default="", description="Inline resume text. Empty allowed if source_resume_ref provided.")
    source_resume_ref: str = Field(default="", description="Path to source resume file. Empty allowed if source_resume_text provided.")


class TargetSection(_ImmutableModel):
    """Target company / role / level."""

    company: _NonEmptyStr
    role: _NonEmptyStr
    level: _NonEmptyStr = Field(description="One of 'JUNIOR'|'MID'|'SENIOR'|'STAFF'|'EXECUTIVE'|... (apps_rg-defined enum).")


class ProfileManifestSection(_ImmutableModel):
    """Digest-bound declarative profile references — POLICY REFS.

    Every field below is a "policy ref" required by the U0 adapter. Missing
    any of these raises ``MissingPolicyRefsError``.
    """

    manifest_digest: _Sha256Hex = Field(description="SHA-256 over canonical profile manifest content.")
    profile_refs: Mapping[str, str] = Field(default_factory=dict, description="Map of profile-name → digest.")
    prompt_registry_ref: _NonEmptyStr = Field(description="Ref to prompt template registry (apps_rg owned).")
    hitl_policy_ref: _NonEmptyStr = Field(description="Ref to HITL trigger policy (apps_rg owned).")
    l0_policy_ref: _NonEmptyStr = Field(description="Ref to L0 routing policy (apps_rg domain hints).")
    agent_spec_ref: _NonEmptyStr = Field(description="Ref to apps_rg agent spec v1.")
    thresholds_ref: _NonEmptyStr = Field(description="Ref to apps_rg quality thresholds.")


class QualityThresholdsSection(_ImmutableModel):
    """Quality intent — declarative thresholds."""

    min_quality: float = Field(ge=0.0, le=1.0, description="Floor quality score (e.g. 0.75).")
    min_ats: int = Field(ge=0, le=100, description="Floor ATS compatibility (e.g. 70).")
    word_min: int = Field(ge=0, description="Floor word count.")
    word_max: int = Field(ge=0, description="Ceiling word count.")


class OutputRequirementsSection(_ImmutableModel):
    """Output formats + provenance flags."""

    formats: tuple[str, ...] = Field(min_length=1, description="Required output formats — e.g. ('json', 'docx').")
    provenance_required: bool = Field(description="If true, every bullet must carry provenance.")
    fact_checked_required: bool = Field(description="If true, fact-check gate must run.")


class ProvenanceRequirementsSection(_ImmutableModel):
    """Per-bullet provenance contract."""

    per_bullet_required: bool
    source_quote_required: bool


class RuntimeCustomizationPackage(_ImmutableModel):
    """Complete runtime operating package for apps_rg.

    Carries declarative refs, digests, policies, and gate/judge/eval metadata
    that downstream core stages consume. U0 validates and preserves this section
    verbatim under app_payload — U0 does NOT execute any of these references.

    Wave 2.5 (apps-rg-ensemble-judge-restoration-a7c4e2): blocking precondition
    for Wave 3 (L3 workflow runner) and Wave 4 (L2 ENSEMBLE_MODEL lane).
    """

    workflow_manifest_ref: str = Field(default="", description="Ref to managed workflow manifest. Empty → single_step.")
    runtime_gate_profile_ref: str = Field(default="", description="Ref to runtime gate profile (pre-L2 gates).")
    exit_profile_ref: str = Field(default="", description="Ref to Exit-stage profile (G21-G28 enforcement).")
    judge_profile_ref: str = Field(default="", description="Ref to judge jury profile (provider roster + rubric binding).")
    eval_rubric_ref: str = Field(default="", description="Ref to evaluation rubric for quality scoring.")
    threshold_profile_ref: str = Field(default="", description="Ref to threshold profile for gate pass/fail.")
    grader_roster_ref: str = Field(default="", description="Ref to grader roster (which providers grade which sections).")
    rubric_output_map_ref: str = Field(default="", description="Ref to rubric-output mapping (rubric → output format).")
    negative_controls_ref: str = Field(default="", description="Ref to negative control definitions for judge calibration.")
    learning_profile_ref: str = Field(default="", description="Ref to learning profile (L6 RuntimeExhaustBundle consumption).")
    meta_feedback_profile_ref: str = Field(default="", description="Ref to meta-feedback profile (post-runtime learning).")
    prompt_profile_ref: str = Field(default="", description="Ref to prompt profile (PA template selection).")
    route_profile_ref: str = Field(default="", description="Ref to route profile (L0 routing hints).")
    retrieval_profile_ref: str = Field(default="", description="Ref to retrieval profile (C0 grounding strategy).")
    repair_profile_ref: str = Field(default="", description="Ref to repair profile (healing/retry strategy).")
    cache_profile_ref: str = Field(default="", description="Ref to cache profile (R1A/R1B/R5 policy).")
    capability_profile_ref: str = Field(default="", description="Ref to capability profile (model requirements).")
    orchestration_profile_ref: str = Field(default="", description="Ref to orchestration profile (L3 merge/split strategy).")
    provider_profile_ref: str = Field(default="", description="Ref to provider profile (model/judge provider roster).")
    write_policy: str = Field(default="read_only", description="Write policy: 'read_only' | 'deferred_writeback'. apps_rg is always read_only.")
    required_runtime_gates: tuple[str, ...] = Field(default_factory=tuple, description="Gate IDs that MUST pass before L2 execution.")
    required_exit_gates: tuple[str, ...] = Field(default_factory=tuple, description="Gate IDs that MUST pass at Exit (G21-G28).")
    conditional_exit_gates: tuple[str, ...] = Field(default_factory=tuple, description="Gate IDs conditionally invoked at Exit (based on output_requirements).")
    package_digest: str = Field(default="", description="SHA-256 over canonical JSON of this section (integrity seal).")


# ---------------------------------------------------------------------------
# Top-level contract
# ---------------------------------------------------------------------------


class AppsRgIngressContractV1(BaseModel):
    """The canonical apps_rg JSON ingress payload, version 1.

    All sub-sections are required. Optional fields have explicit defaults
    documented in the section model. Unknown fields at the top level are
    rejected by Pydantic (``extra='forbid'``), and the U0 reflection adapter
    additionally verifies that every JSON Pointer in the input has a matching
    field-map entry — catching any field that validates but is silently
    dropped.

    Capability-requirement clause (Author-Gate AG-4.b): apps_rg declares
    semantic needs (``capability_requirements``); core L0's model_registry
    maps requirements → provider/model. apps_rg NEVER names a provider here.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    apps_rg_contract_version: _NonEmptyStr = Field(
        description=f"MUST equal '{APPS_RG_INGRESS_CONTRACT_VERSION}'. Different versions require a different module.",
    )
    transport: TransportSection
    identity: IdentitySection
    replay: ReplaySection
    jd_payload: JdPayloadSection
    resume_payload: ResumePayloadSection
    target: TargetSection
    generation_mode: GenerationMode = Field(
        description="One of the GenerationMode enum values. Unknown values fail closed.",
    )
    capability_requirements: tuple[str, ...] = Field(
        default_factory=tuple,
        description=(
            "Per Author-Gate AG-4.b: semantic capability needs (e.g. "
            "'needs_strong_narrative', 'needs_long_context'). apps_rg MAY "
            "NOT name a provider; core L0 maps requirements → provider."
        ),
    )
    profile_manifest: ProfileManifestSection
    quality_thresholds: QualityThresholdsSection
    output_requirements: OutputRequirementsSection
    provenance_requirements: ProvenanceRequirementsSection
    runtime_customization_package: RuntimeCustomizationPackage = Field(
        default_factory=RuntimeCustomizationPackage,
        description=(
            "Complete runtime operating package. Carries all refs/digests/policies "
            "downstream core stages need. Default-constructed (all empty) so existing "
            "payloads without this section remain valid."
        ),
    )
    payload_digest: _Sha256Hex = Field(description="SHA-256 over canonical JSON of all sibling fields except payload_digest itself.")


def emit_schema() -> dict[str, Any]:
    """Return the JSON Schema for AppsRgIngressContractV1 (with $id stamped).

    The schema is also persisted on disk at
    ``apps_rg/contracts/apps_rg_ingress_contract.v1.schema.json``. The
    persisted file is the canonical artifact tests load. This function is the
    regenerator — running ``python -m apps_rg.contracts.apps_rg_ingress_contract_v1
    --emit-schema`` writes the regenerated schema to stdout.
    """

    schema = AppsRgIngressContractV1.model_json_schema()
    # Stamp deterministic $id and $schema for downstream tooling.
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://windsurf.agentic-workflow/apps_rg_ingress_contract.v1.schema.json"
    schema["title"] = "AppsRgIngressContractV1"
    schema["x-contract-version"] = APPS_RG_INGRESS_CONTRACT_VERSION
    return schema


def _main() -> int:
    parser = argparse.ArgumentParser(description="apps_rg ingress contract v1 utilities")
    parser.add_argument("--emit-schema", action="store_true", help="Emit JSON schema to stdout.")
    args = parser.parse_args()

    if args.emit_schema:
        json.dump(emit_schema(), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())


__all__ = [
    "APPS_RG_INGRESS_CONTRACT_VERSION",
    "AppsRgIngressContractV1",
    "GenerationMode",
    "TransportSection",
    "IdentitySection",
    "ReplaySection",
    "JdPayloadSection",
    "ResumePayloadSection",
    "TargetSection",
    "ProfileManifestSection",
    "QualityThresholdsSection",
    "OutputRequirementsSection",
    "ProvenanceRequirementsSection",
    "RuntimeCustomizationPackage",
    "emit_schema",
]
