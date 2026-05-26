"""L1 Plan Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L1 planning output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_READ_ONLY


@dataclass(frozen=True, slots=True)
class L1PlanContract:
    """L1 planning output contract.

    Contains planning decisions, routing requirements, and execution prerequisites.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Planning decisions
    task_plan: tuple[str, ...] = field(default_factory=tuple)
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)

    # Execution prerequisites (determine routing)
    # apps_rg: grounding_required=True always for active generation modes (C0.1–C0.7).
    # Company-brief delegation uses apps_research_call_required (no U0 briefing).
    grounding_required: bool = False
    apps_research_call_required: bool = False
    model_generation_required: bool = False  # L2 model execution needed
    write_authority_present: bool = False  # State modification required

    # Identity extension
    tenant_id: str = ""  # W1: threaded from U0 ValidatedRequest.tenant_id (D6)

    # Profile binding
    profile_manifest_digest: str = ""

    # W2: target level for L0 variant routing (DS-3 executive vs default)
    target_level: str = ""  # "SENIOR" | "STAFF" | "EXECUTIVE" | ""

    # AG-2 (apps-rg-app-payload-consumption-wiring-b3a449): app_payload-derived
    # projections. L1 reads ValidatedRequest.app_payload, builds these mappings,
    # and downstream stages (L0, PA, Exit) consume them WITHOUT reading the
    # legacy AppsRgIngressPayload. All five default to empty mapping so the
    # additions are non-breaking for non-apps_rg L1 producers.
    #   - task_spec: generation_mode + capability_requirements
    #   - query_spec: identity hashes (jd_hash, resume_hash) + target tuple
    #   - support_expectation: thresholds + provenance/fact-check booleans
    #   - output_expectation: formats + provenance_required + fact_checked_required
    #   - policy_refs: manifest_digest + 5 ref strings (prompt/hitl/l0/spec/thresholds)
    task_spec: Mapping[str, Any] = field(default_factory=dict)
    query_spec: Mapping[str, Any] = field(default_factory=dict)
    support_expectation: Mapping[str, Any] = field(default_factory=dict)
    output_expectation: Mapping[str, Any] = field(default_factory=dict)
    policy_refs: Mapping[str, str] = field(default_factory=dict)

    # Work-shape hints (L0 uses these to evaluate execution_form after cache miss)
    # All default False so non-managed-workflow apps are unaffected.
    multiple_work_units_hint: bool = False  # >1 independent generation units
    merge_required_hint: bool = False  # units must be merged into final output
    per_unit_quality_selection_hint: bool = False  # each unit needs judge/gate selection
    candidate_generation_expected_hint: bool = False  # multiple candidates per unit

    # Receipt
    planning_timestamp: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from plan_version (D8)
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7, D7=RuntimePosture struct)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
    # W6 P6.3: gate verdict refs (concern #3, reuse CommitRequest shape)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_certification_ref: str = ""

    # W3: non-authority assertion (NAA) — L1 asserts it does not hold execution authority
    # When present, all four required keys must be True.
    non_authority_assertion: Mapping[str, bool] = field(default_factory=dict)

    # W3: planning prior refs — references to prior planning context/decisions
    planning_prior_refs: tuple[str, ...] = field(default_factory=tuple)

    # W3: advisory route hints (not route authority)
    route_hints: Mapping[str, str] = field(default_factory=dict)

    # p3.2: generic work-shape / profile binding for L0 (values from app route_profiles.yaml)
    work_shape: str = ""
    task_shape: str = ""
    route_profile_ref: str = ""

    # W3: prompt BOM refs — references to prompt bill-of-materials entries
    prompt_bom_refs: tuple[str, ...] = field(default_factory=tuple)

    # W3: judge evaluation expectation refs
    judge_eval_expectation_refs: tuple[str, ...] = field(default_factory=tuple)

    # W3 spine (REQ-L1-PLAN-VALIDATION-001, REQ-L1-AMBIGUITY-REGISTER-001)
    validation_receipt_id: str = ""
    ambiguity_register: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"L1PlanContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )

        # Validate non_authority_assertion
        if self.non_authority_assertion:
            _validate_non_authority_assertion(self.non_authority_assertion)

        # Validate route_hints reject route-authority keys
        if self.route_hints:
            _validate_route_hints(self.route_hints)

        # Validate prompt_bom_refs format
        if self.prompt_bom_refs:
            _validate_ref_tuple(self.prompt_bom_refs, "prompt_bom_refs")

        # Validate judge_eval_expectation_refs format
        if self.judge_eval_expectation_refs:
            _validate_ref_tuple(self.judge_eval_expectation_refs, "judge_eval_expectation_refs")


# --- Validation Helpers ---

# Required non-authority assertion keys
_NAA_REQUIRED_KEYS = frozenset({"no_evidence_retrieval", "no_pa_assembly", "no_model_call", "no_c0_import"})

# Forbidden route-authority keys in route_hints
_ROUTE_AUTHORITY_KEYS = frozenset({"route_id", "route_family", "execution_form", "selected_route_reason", "route_digest"})


def _validate_non_authority_assertion(naa: Mapping[str, bool]) -> None:
    """Validate non_authority_assertion has all required keys and all values are True."""
    present_keys = set(naa.keys())
    missing_keys = _NAA_REQUIRED_KEYS - present_keys
    if missing_keys:
        raise ValueError(
            f"L1PlanContract.non_authority_assertion: missing required keys {sorted(missing_keys)}. "
            f"All of {_NAA_REQUIRED_KEYS} must be present when NAA is asserted."
        )
    extra_keys = present_keys - _NAA_REQUIRED_KEYS
    if extra_keys:
        raise ValueError(
            f"L1PlanContract.non_authority_assertion: unknown keys {sorted(extra_keys)}. "
            f"Only {_NAA_REQUIRED_KEYS} are allowed."
        )
    for key, value in naa.items():
        if value is not True:
            raise ValueError(
                f"L1PlanContract.non_authority_assertion: key '{key}' must be True, got {value!r}. "
                "All NAA assertions must affirmatively be True."
            )


def _validate_route_hints(hints: Mapping[str, str]) -> None:
    """Validate route_hints contains no route-authority keys."""
    for key in hints.keys():
        if key in _ROUTE_AUTHORITY_KEYS:
            raise ValueError(
                f"L1PlanContract.route_hints: forbidden route-authority key '{key}'. "
                f"Route hints must not contain {_ROUTE_AUTHORITY_KEYS}."
            )


def _validate_ref_tuple(refs: tuple[str, ...], field_name: str) -> None:
    """Validate ref tuple contains only clean reference strings."""
    # Forbidden patterns indicating raw prompt content
    _FORBIDDEN_PROMPT_PATTERNS = [
        "generate", "create", "write", "produce",
        "resume", "cv", "cover letter",
    ]

    for i, ref in enumerate(refs):
        if not isinstance(ref, str):
            raise ValueError(
                f"L1PlanContract.{field_name}[{i}]: must be str, got {type(ref).__name__}"
            )
        if "\n" in ref or "\r" in ref:
            raise ValueError(
                f"L1PlanContract.{field_name}[{i}]: ref must not contain newlines"
            )
        if "<prompt>" in ref or "</prompt>" in ref or ("<" in ref and ">" in ref):
            raise ValueError(
                f"L1PlanContract.{field_name}[{i}]: ref must not contain XML tags or prompt content"
            )
        if len(ref) > 256:
            raise ValueError(
                f"L1PlanContract.{field_name}[{i}]: ref length {len(ref)} exceeds max 256"
            )
        # Reject raw prompt content (natural language instructions)
        ref_lower = ref.lower()
        for pattern in _FORBIDDEN_PROMPT_PATTERNS:
            if pattern in ref_lower and " " in ref_lower:
                raise ValueError(
                    f"L1PlanContract.{field_name}[{i}]: ref appears to contain prompt content: '{ref[:30]}...'"
                )
