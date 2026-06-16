"""Upstream input contracts for Prompt Assembly.

Mirrors the five INPUT FAMILY blocks from the spec (lines 217–324):

    INPUT FAMILY 1: L1 PLAN PROJECTION
    INPUT FAMILY 2: L0 ROUTE PROJECTION
    INPUT FAMILY 3: C0 EVIDENCE PROJECTION
    INPUT FAMILY 4: GOVERNANCE ARTIFACTS
    INPUT FAMILY 5: USER + EXECUTION METADATA

Each family is a frozen dataclass listing every field enumerated in the
spec verbatim. Helper :func:`upstream_bundle_from_dicts` builds an
:class:`UpstreamInputBundle` from loosely-typed mappings — used by callers
that already pass dicts to :func:`run_prompt_assembly_pipeline`.

The classes are intentionally permissive (every field defaults) so partial
contracts (e.g. WEAK_WITH_CAVEATS evidence) round-trip without raising. They
are Prompt Assembly projections, not the canonical runtime contract classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class PAL1PlanProjection:
    """Spec INPUT FAMILY 1 — Prompt Assembly view of the L1 plan contract."""

    plan_id: str = ""
    task_spec: str = ""
    query_spec: str = ""
    output_target: str = ""
    grounding_required: bool = False
    declared_assumptions: tuple[str, ...] = ()
    unresolved_gaps: tuple[str, ...] = ()
    support_expectation: str = ""
    work_class: str = ""
    risk_hint: str = ""
    policy_hash: str = ""
    write_requested: bool = False
    tenant_id: str = ""  # W1: identity quad extension (D6)
    l5_certification_ref: str = ""


@dataclass(frozen=True)
class PAL0RouteProjection:
    """Spec INPUT FAMILY 2 — Prompt Assembly view of the L0 route contract."""

    route_id: str = ""
    execution_form: str = ""
    provider_lane: str = ""
    model_id: str = ""
    temperature: float | None = None
    thinking_level: str = ""
    policy_posture: str = ""
    cache_posture: str = ""
    freshness_class: str = ""
    support_target: str = ""
    cost_tier: str = ""
    slo_budget: dict[str, Any] = field(default_factory=dict)
    fallback_chain: tuple[str, ...] = ()
    telemetry_keys: tuple[str, ...] = ()
    hmac_sig: str = ""
    required_slots: tuple[str, ...] = ()
    policy_hash: str = ""
    tenant_id: str = ""  # W1: identity quad extension (D6)
    l5_certification_ref: str = ""


@dataclass(frozen=True)
class PAC0EvidenceProjection:
    """Spec INPUT FAMILY 3 — Prompt Assembly view of the C0 evidence contract."""

    status: str = ""  # PASS | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED
    support_score: float = 0.0
    verified_chunks: tuple[str, ...] = ()
    cited_spans: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    evidence_classes: dict[str, tuple[str, ...]] = field(default_factory=dict)
    contradiction_flags: tuple[str, ...] = ()
    unresolved_gaps: tuple[str, ...] = ()
    freshness_report: dict[str, Any] = field(default_factory=dict)
    acl_report: dict[str, Any] = field(default_factory=dict)
    lineage_manifest: tuple[dict[str, Any], ...] = ()
    prompt_budget_hint: dict[str, Any] = field(default_factory=dict)
    recommended_disposition: str = ""
    retrieval_budget_report: dict[str, Any] = field(default_factory=dict)
    policy_hash: str = ""


@dataclass(frozen=True)
class GovernanceArtifacts:
    """Spec INPUT FAMILY 4 — governance artifacts."""

    system_version_hash: str = ""
    policy_hash: str = ""
    compliance_hash: str = ""
    role_fences: tuple[str, ...] = ()
    safety_invariants: tuple[str, ...] = ()
    allowed_tool_posture: str = ""
    sandbox_envelope: dict[str, Any] = field(default_factory=dict)
    capability_token: str = ""
    agent_spec: dict[str, Any] = field(default_factory=dict)
    response_schema_contract: dict[str, Any] = field(default_factory=dict)
    citation_mode: str = ""
    egress_posture: str = ""
    hitl_required: bool = False
    durable_write_allowed: bool = False


@dataclass(frozen=True)
class UserExecutionMetadata:
    """Spec INPUT FAMILY 5 — user + execution metadata."""

    raw_user_task: str = ""
    neutralized_user_task: str = ""
    origin_trust: str = "user_turn"
    request_id: str = ""
    session_id: str = ""
    trace_root: str = ""
    replay_key: str = ""
    policy_hash: str = ""
    plan_id: str = ""
    route_id: str = ""
    idempotency_nonce: str = ""
    model_id: str = ""
    provider_target: str = ""
    tokenizer_target: str = ""
    run_clock: str = ""
    executable_requested: bool = True
    bom_id: str = ""
    artifact_id: str = ""


@dataclass(frozen=True)
class UpstreamInputBundle:
    """Aggregated upstream-input bundle (spec INTERNAL ARTIFACTS §1)."""

    plan: PAL1PlanProjection
    route: PAL0RouteProjection
    evidence: PAC0EvidenceProjection
    governance: GovernanceArtifacts
    execution: UserExecutionMetadata


def _filter(cls: type, src: Mapping[str, Any]) -> dict[str, Any]:
    fields = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
    return {k: v for k, v in src.items() if k in fields}


def upstream_bundle_from_dicts(
    *,
    plan_contract: Mapping[str, Any] | None,
    route_contract: Mapping[str, Any] | None,
    evidence_contract: Mapping[str, Any] | None = None,
    governance: Mapping[str, Any] | None = None,
    execution_metadata: Mapping[str, Any] | None = None,
) -> UpstreamInputBundle:
    """Build a typed :class:`UpstreamInputBundle` from dicts."""
    return UpstreamInputBundle(
        plan=PAL1PlanProjection(**_filter(PAL1PlanProjection, plan_contract or {})),
        route=PAL0RouteProjection(**_filter(PAL0RouteProjection, route_contract or {})),
        evidence=PAC0EvidenceProjection(**_filter(PAC0EvidenceProjection, evidence_contract or {})),
        governance=GovernanceArtifacts(**_filter(GovernanceArtifacts, governance or {})),
        execution=UserExecutionMetadata(**_filter(UserExecutionMetadata, execution_metadata or {})),
    )


# Backward-compatible aliases. New code should use the PA*Projection names so
# these permissive views are not confused with canonical runtime contracts.
L1PlanContract = PAL1PlanProjection
L0RouteContract = PAL0RouteProjection
C0EvidenceContract = PAC0EvidenceProjection


__all__ = [
    "C0EvidenceContract",
    "GovernanceArtifacts",
    "L0RouteContract",
    "L1PlanContract",
    "PAC0EvidenceProjection",
    "PAL0RouteProjection",
    "PAL1PlanProjection",
    "UpstreamInputBundle",
    "UserExecutionMetadata",
    "upstream_bundle_from_dicts",
]
