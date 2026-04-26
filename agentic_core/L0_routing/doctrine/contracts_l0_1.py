"""03.1 L0 Route Input + Preflight contracts.

Realizes:

- ``RouteDecisionInput``      — 03.1 PHASE 1 §1
- ``RoutePreflightStatus``    — 03.1 PHASE 1 §2
- ``RouteDiscriminatorFrame`` — 03.1 PHASE 1 §3
- ``SourceAvailabilitySnapshot`` — 03.1 PHASE 1 §4
- ``RouteCandidateFrame``     — 03.1 PHASE 1 §5
- ``RouteInputAuditReceipt``  — emitted by ``preflight.run_l0_preflight``

All types are frozen dataclasses with explicit validation. No I/O. No mutation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, fields
from enum import Enum

from . import DoctrineContractError

_MAX_STR_LEN = 512
_MAX_LIST_LEN = 64
_MAX_REASON_CODES = 32


# ---------------------------------------------------------------------------
# Validation helpers (module-private)
# ---------------------------------------------------------------------------


def _need_str(value: object, field_name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise DoctrineContractError(
            f"{field_name} must be str, got {type(value).__name__}",
        )
    if len(value) > _MAX_STR_LEN:
        raise DoctrineContractError(
            f"{field_name} exceeds {_MAX_STR_LEN} chars (got {len(value)})",
        )
    if not allow_empty and len(value) == 0:
        raise DoctrineContractError(f"{field_name} must be non-empty")


def _need_str_tuple(values: object, field_name: str, *, max_len: int = _MAX_LIST_LEN) -> None:
    if not isinstance(values, tuple):
        raise DoctrineContractError(f"{field_name} must be tuple")
    if len(values) > max_len:
        raise DoctrineContractError(
            f"{field_name} exceeds max length {max_len} (got {len(values)})",
        )
    for idx, item in enumerate(values):
        if not isinstance(item, str):
            raise DoctrineContractError(
                f"{field_name}[{idx}] must be str, got {type(item).__name__}",
            )
        if len(item) == 0 or len(item) > _MAX_STR_LEN:
            raise DoctrineContractError(
                f"{field_name}[{idx}] must be non-empty str within {_MAX_STR_LEN} chars",
            )


def _need_bool(value: object, field_name: str) -> None:
    if not isinstance(value, bool):
        raise DoctrineContractError(
            f"{field_name} must be bool, got {type(value).__name__}",
        )


def _canonical_hash(payload: dict[str, object]) -> str:
    """Deterministic SHA-256 over canonical JSON. No entropy, no wall-clock."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# ---------------------------------------------------------------------------
# Allowed candidate route IDs (per 03.1 PHASE 1 §5)
# ---------------------------------------------------------------------------


class CandidateRouteId(str, Enum):
    R1A_EXACT_CACHE = "R1A_EXACT_CACHE"
    R1B_SEMANTIC_CACHE = "R1B_SEMANTIC_CACHE"
    R3_SIMPLE_GROUNDED_READ = "R3_SIMPLE_GROUNDED_READ"
    R4_SINGLE_ACTION = "R4_SINGLE_ACTION"
    R3R4_MANAGED_WORKFLOW = "R3R4_MANAGED_WORKFLOW"
    R5_FALLBACK = "R5_FALLBACK"


class PreflightStatus(str, Enum):
    """03.1 PHASE 1 §2 — RoutePreflightStatus enum."""

    ROUTE_READY = "ROUTE_READY"
    ROUTE_INPUT_INCOMPLETE = "ROUTE_INPUT_INCOMPLETE"
    ROUTE_BLOCKED_POLICY = "ROUTE_BLOCKED_POLICY"
    ROUTE_BLOCKED_SCOPE = "ROUTE_BLOCKED_SCOPE"
    ROUTE_BLOCKED_AUTHORITY = "ROUTE_BLOCKED_AUTHORITY"
    ROUTE_NEEDS_CLARIFY_FALLBACK = "ROUTE_NEEDS_CLARIFY_FALLBACK"
    ROUTE_SAFE_FALLBACK_ONLY = "ROUTE_SAFE_FALLBACK_ONLY"


# ---------------------------------------------------------------------------
# Substructures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class L1ValidationSummary:
    """Carries the L1 non-authority assertions L0 must verify (03.1 §1 validation)."""

    no_retrieval_performed: bool = True
    no_execution_performed: bool = True
    no_write_performed: bool = True
    no_final_route_authority_claimed: bool = True

    def __post_init__(self) -> None:
        for name in (
            "no_retrieval_performed",
            "no_execution_performed",
            "no_write_performed",
            "no_final_route_authority_claimed",
        ):
            _need_bool(getattr(self, name), f"L1ValidationSummary.{name}")


@dataclass(frozen=True)
class RouteDecisionInput:
    """03.1 PHASE 1 §1 RouteDecisionInput.

    Inputs L0 needs to begin route preflight. Most fields are opaque hash/identifier
    refs because L0 itself does not parse downstream content.
    """

    request_id: str
    run_id: str
    session_id: str
    trace_root: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    l1_plan_id: str
    l1_plan_digest: str
    task_spec: str
    query_spec: str
    route_hint_from_l1: str = ""
    support_expectation: str = ""
    action_expectation: str = ""
    assumptions_and_gaps: tuple[str, ...] = field(default_factory=tuple)
    validation_summary: L1ValidationSummary = field(default_factory=L1ValidationSummary)
    caller_scope_baseline: tuple[str, ...] = field(default_factory=tuple)
    visible_source_handles: tuple[str, ...] = field(default_factory=tuple)
    source_expectations: tuple[str, ...] = field(default_factory=tuple)
    output_target: str = ""
    risk_hints: tuple[str, ...] = field(default_factory=tuple)
    freshness_hints: tuple[str, ...] = field(default_factory=tuple)
    artifact_requirements: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in (
            "request_id",
            "run_id",
            "trace_root",
            "tenant_id",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "l1_plan_id",
            "l1_plan_digest",
            "task_spec",
            "query_spec",
        ):
            _need_str(getattr(self, name), f"RouteDecisionInput.{name}")
        for name in (
            "session_id",
            "route_hint_from_l1",
            "support_expectation",
            "action_expectation",
            "output_target",
        ):
            _need_str(getattr(self, name), f"RouteDecisionInput.{name}", allow_empty=True)
        for name in (
            "assumptions_and_gaps",
            "caller_scope_baseline",
            "visible_source_handles",
            "source_expectations",
            "risk_hints",
            "freshness_hints",
            "artifact_requirements",
        ):
            _need_str_tuple(getattr(self, name), f"RouteDecisionInput.{name}")
        if not isinstance(self.validation_summary, L1ValidationSummary):
            raise DoctrineContractError(
                "RouteDecisionInput.validation_summary must be L1ValidationSummary",
            )

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RoutePreflightStatusReport:
    """03.1 PHASE 1 §2 RoutePreflightStatus."""

    preflight_id: str
    status: PreflightStatus
    eligible_for_route_selection: bool
    blocked_reason: str
    policy_status: str
    tenant_scope_status: str
    acl_scope_status: str
    route_input_completeness: str
    missing_critical_fields: tuple[str, ...]
    invalid_authority_claims: tuple[str, ...]
    stale_policy_or_blueprint_flags: tuple[str, ...]
    source_handle_status: tuple[str, ...]
    action_scope_status: str
    egress_scope_status: str
    preflight_hash: str

    def __post_init__(self) -> None:
        _need_str(self.preflight_id, "RoutePreflightStatusReport.preflight_id")
        if not isinstance(self.status, PreflightStatus):
            raise DoctrineContractError(
                "RoutePreflightStatusReport.status must be PreflightStatus",
            )
        _need_bool(
            self.eligible_for_route_selection, "RoutePreflightStatusReport.eligible_for_route_selection"
        )
        for name in (
            "blocked_reason",
            "policy_status",
            "tenant_scope_status",
            "acl_scope_status",
            "route_input_completeness",
            "action_scope_status",
            "egress_scope_status",
        ):
            _need_str(getattr(self, name), f"RoutePreflightStatusReport.{name}", allow_empty=True)
        for name in (
            "missing_critical_fields",
            "invalid_authority_claims",
            "stale_policy_or_blueprint_flags",
            "source_handle_status",
        ):
            _need_str_tuple(getattr(self, name), f"RoutePreflightStatusReport.{name}")
        _need_str(self.preflight_hash, "RoutePreflightStatusReport.preflight_hash")

        # Coherence: status==ROUTE_READY <=> eligible_for_route_selection
        if (self.status == PreflightStatus.ROUTE_READY) != self.eligible_for_route_selection:
            raise DoctrineContractError(
                "status=ROUTE_READY must agree with eligible_for_route_selection=True",
            )


@dataclass(frozen=True)
class RouteDiscriminatorFrame:
    """03.1 PHASE 1 §3 RouteDiscriminatorFrame.

    Boolean discriminators extracted from L1 plan + tenant scope. Used by the
    selector (03.2) to reason about which routes are eligible.
    """

    asks_for_factual_claim: bool = False
    asks_for_source_grounding: bool = False
    asks_for_current_or_latest: bool = False
    asks_for_user_file_or_connector: bool = False
    asks_for_code_or_policy_location: bool = False
    asks_for_external_action: bool = False
    asks_for_durable_mutation: bool = False
    asks_for_irreversible_action: bool = False
    asks_for_multi_step_workflow: bool = False
    has_dependency_chain: bool = False
    has_branching_or_join: bool = False
    has_parallel_safe_shards: bool = False
    has_weak_support_risk: bool = False
    has_ambiguous_action_args: bool = False
    can_be_cached_exactly: bool = False
    can_be_cached_semantically: bool = False
    can_be_answered_terminally: bool = False
    can_be_single_step: bool = False
    likely_requires_l3: bool = False
    likely_requires_hitl: bool = False
    likely_requires_uwg: bool = False
    likely_requires_c0: bool = False
    likely_requires_pa: bool = False
    likely_requires_l2: bool = False
    likely_ptc_capable_downstream: bool = False

    def __post_init__(self) -> None:
        for f in fields(self):
            _need_bool(getattr(self, f.name), f"RouteDiscriminatorFrame.{f.name}")
        # PTC discriminator rule (03.1 §3): PTC capability is downstream-L2-only.
        # No invariant violation possible from data alone, but the upstream caller
        # must NOT use this flag to mean "L0 will run script". Comment-only.


@dataclass(frozen=True)
class SourceAvailabilitySnapshot:
    """03.1 PHASE 1 §4 SourceAvailabilitySnapshot."""

    source_classes_expected: tuple[str, ...] = field(default_factory=tuple)
    source_classes_available: tuple[str, ...] = field(default_factory=tuple)
    source_classes_missing: tuple[str, ...] = field(default_factory=tuple)
    connector_status: tuple[str, ...] = field(default_factory=tuple)
    file_handle_status: tuple[str, ...] = field(default_factory=tuple)
    cache_store_status: str = "unknown"
    semantic_cache_status: str = "unknown"
    vector_store_status: str = "unknown"
    bm25_status: str = "unknown"
    graph_store_status: str = "unknown"
    code_index_status: str = "unknown"
    trace_store_status: str = "unknown"
    policy_source_status: str = "unknown"
    acl_readability_summary: str = "unknown"
    freshness_index_status: str = "unknown"
    availability_hash: str = ""

    def __post_init__(self) -> None:
        for name in (
            "source_classes_expected",
            "source_classes_available",
            "source_classes_missing",
            "connector_status",
            "file_handle_status",
        ):
            _need_str_tuple(getattr(self, name), f"SourceAvailabilitySnapshot.{name}")
        for name in (
            "cache_store_status",
            "semantic_cache_status",
            "vector_store_status",
            "bm25_status",
            "graph_store_status",
            "code_index_status",
            "trace_store_status",
            "policy_source_status",
            "acl_readability_summary",
            "freshness_index_status",
        ):
            _need_str(getattr(self, name), f"SourceAvailabilitySnapshot.{name}")
        _need_str(self.availability_hash, "SourceAvailabilitySnapshot.availability_hash", allow_empty=True)

    def with_hash(self) -> "SourceAvailabilitySnapshot":
        """Return a copy with ``availability_hash`` populated deterministically."""
        payload = asdict(self)
        payload.pop("availability_hash", None)
        return SourceAvailabilitySnapshot(
            source_classes_expected=self.source_classes_expected,
            source_classes_available=self.source_classes_available,
            source_classes_missing=self.source_classes_missing,
            connector_status=self.connector_status,
            file_handle_status=self.file_handle_status,
            cache_store_status=self.cache_store_status,
            semantic_cache_status=self.semantic_cache_status,
            vector_store_status=self.vector_store_status,
            bm25_status=self.bm25_status,
            graph_store_status=self.graph_store_status,
            code_index_status=self.code_index_status,
            trace_store_status=self.trace_store_status,
            policy_source_status=self.policy_source_status,
            acl_readability_summary=self.acl_readability_summary,
            freshness_index_status=self.freshness_index_status,
            availability_hash=_canonical_hash(payload),
        )


@dataclass(frozen=True)
class RouteCandidateFrame:
    """03.1 PHASE 1 §5 RouteCandidateFrame.

    Output of preflight pipeline. Carries the candidate route ids the selector
    is allowed to choose from, plus reason codes / blockers per candidate.
    """

    route_candidates: tuple[CandidateRouteId, ...]
    candidate_reason_codes: tuple[str, ...] = field(default_factory=tuple)
    candidate_blockers: tuple[str, ...] = field(default_factory=tuple)
    candidate_required_downstream_layers: tuple[str, ...] = field(default_factory=tuple)
    candidate_risks: tuple[str, ...] = field(default_factory=tuple)
    candidate_cost_estimates: tuple[str, ...] = field(default_factory=tuple)
    candidate_slo_estimates: tuple[str, ...] = field(default_factory=tuple)
    candidate_support_obligations: tuple[str, ...] = field(default_factory=tuple)
    candidate_capability_requirements: tuple[str, ...] = field(default_factory=tuple)
    candidate_sandbox_requirements: tuple[str, ...] = field(default_factory=tuple)
    candidate_handoff_requirements: tuple[str, ...] = field(default_factory=tuple)
    discriminators: RouteDiscriminatorFrame = field(default_factory=RouteDiscriminatorFrame)
    source_availability: SourceAvailabilitySnapshot = field(default_factory=SourceAvailabilitySnapshot)
    preflight_status: PreflightStatus = PreflightStatus.ROUTE_READY
    candidate_frame_hash: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.route_candidates, tuple):
            raise DoctrineContractError("route_candidates must be tuple")
        if len(self.route_candidates) == 0:
            raise DoctrineContractError(
                "route_candidates must contain at least one CandidateRouteId",
            )
        if len(self.route_candidates) > _MAX_LIST_LEN:
            raise DoctrineContractError(
                f"route_candidates exceeds {_MAX_LIST_LEN} entries",
            )
        for idx, candidate in enumerate(self.route_candidates):
            if not isinstance(candidate, CandidateRouteId):
                raise DoctrineContractError(
                    f"route_candidates[{idx}] must be CandidateRouteId, got {type(candidate).__name__}",
                )
        for name in (
            "candidate_reason_codes",
            "candidate_blockers",
            "candidate_required_downstream_layers",
            "candidate_risks",
            "candidate_cost_estimates",
            "candidate_slo_estimates",
            "candidate_support_obligations",
            "candidate_capability_requirements",
            "candidate_sandbox_requirements",
            "candidate_handoff_requirements",
        ):
            _need_str_tuple(getattr(self, name), f"RouteCandidateFrame.{name}", max_len=_MAX_REASON_CODES)
        if not isinstance(self.discriminators, RouteDiscriminatorFrame):
            raise DoctrineContractError(
                "RouteCandidateFrame.discriminators must be RouteDiscriminatorFrame",
            )
        if not isinstance(self.source_availability, SourceAvailabilitySnapshot):
            raise DoctrineContractError(
                "RouteCandidateFrame.source_availability must be SourceAvailabilitySnapshot",
            )
        if not isinstance(self.preflight_status, PreflightStatus):
            raise DoctrineContractError(
                "RouteCandidateFrame.preflight_status must be PreflightStatus",
            )
        _need_str(self.candidate_frame_hash, "RouteCandidateFrame.candidate_frame_hash", allow_empty=True)


@dataclass(frozen=True)
class RouteInputAuditReceipt:
    """Receipt emitted by ``preflight.run_l0_preflight`` for L6 calibration.

    Not in 03.1 as a dedicated section but listed under ``THIS FILE OWNS``.
    """

    receipt_id: str
    request_id: str
    run_id: str
    trace_root: str
    l1_plan_id: str
    preflight_id: str
    candidate_count: int
    blocked_count: int
    fail_closed_reason: str
    receipt_hash: str

    def __post_init__(self) -> None:
        for name in (
            "receipt_id",
            "request_id",
            "run_id",
            "trace_root",
            "l1_plan_id",
            "preflight_id",
            "receipt_hash",
        ):
            _need_str(getattr(self, name), f"RouteInputAuditReceipt.{name}")
        _need_str(self.fail_closed_reason, "RouteInputAuditReceipt.fail_closed_reason", allow_empty=True)
        if not isinstance(self.candidate_count, int) or isinstance(self.candidate_count, bool):
            raise DoctrineContractError("candidate_count must be int")
        if self.candidate_count < 0:
            raise DoctrineContractError("candidate_count must be >= 0")
        if not isinstance(self.blocked_count, int) or isinstance(self.blocked_count, bool):
            raise DoctrineContractError("blocked_count must be int")
        if self.blocked_count < 0:
            raise DoctrineContractError("blocked_count must be >= 0")


__all__ = [
    "CandidateRouteId",
    "L1ValidationSummary",
    "PreflightStatus",
    "RouteCandidateFrame",
    "RouteDecisionInput",
    "RouteDiscriminatorFrame",
    "RouteInputAuditReceipt",
    "RoutePreflightStatusReport",
    "SourceAvailabilitySnapshot",
]
