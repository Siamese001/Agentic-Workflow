"""v15 L0 RouteContract — additive type extensions.

Realizes the v15 doctrine surface defined in
``docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v15.md``
without disturbing the existing v12 wiring (``route_contract_v12_extensions``,
``v12_route_selector``). v15 is **additive** — same pattern v12 used to extend
v9.

Key v15 deltas over v12 (see §ROUTE CONTRACT SCHEMA — v15 in the doctrine):

- 6 canonical routes only (R1A, R1B, R3, R4, R3R4_MANAGED, R5). Parallel /
  iterative-loop / HITL / cascade are *aspects* of MANAGED_WORKFLOW, not
  separate routes.
- 3 execution forms only (TERMINAL_SHORTCIRCUIT, SINGLE_STEP, MANAGED_WORKFLOW).
- Confidence is numeric + reasoned class enum.
- Freshness uses the v15 5-value vocabulary.
- Cache policy adds READ_THROUGH and BYPASS_CACHE.
- Cost tier adds TIER_HITL.
- ``support_target``, ``authority``, ``telemetry_keys``, and ``signatures`` are
  structured top-level fields on the contract.
- Replay determinism: ``deterministic_route_digest`` MUST be a function of
  policy_hash, blueprint_hash, snapshot_id, route_id, execution_form,
  cache_policy, freshness_class, support_target, cost_tier, fallback_chain,
  reason_codes (sorted), and tenant_scope. Wall-clock and entropy MUST NOT
  influence it (v15 §INVARIANTS).

Constitutional compliance:

- Frozen dataclasses, no mutation after construction.
- Specific exception types (``V15RouteContractError``).
- HMAC-SHA256 + SHA-256 manifest hash via stdlib only.
- Defensive validation: NaN/inf reject, range checks, length caps,
  closed-vocabulary enforcement on enums, fallback-chain depth + R5-last
  guarantee, terminal vs non-terminal coherence.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import ClassVar

# ---------------------------------------------------------------------------
# Hard limits
# ---------------------------------------------------------------------------

_MAX_REASON_CODES = 32
_MAX_ACL_BOUNDS = 64
_MAX_FALLBACK_CHAIN_DEPTH = 8
_MAX_STRING_LEN = 512
_MAX_HITL_PAUSE_POINTS = 16
_MAX_SLO_LATENCY_MS = 3_600_000  # 1 hour ceiling
_MAX_SLO_TOKENS = 1_000_000
_MAX_SLO_COST_USD = 100.0
_MAX_SLO_RETRIEVAL_PASSES = 16
_MAX_SLO_GRAPH_HOPS = 16
_MAX_SLO_TOOL_CALLS = 64
_MAX_SLO_ITERATIONS = 16

_MIN_HMAC_KEY_BYTES = 16

# ---------------------------------------------------------------------------
# v15 Enums (closed vocabularies)
# ---------------------------------------------------------------------------


class RouteIdV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — six canonical routes.

    These are the ONLY route ids permitted in a v15 RouteContract. Parallel,
    iterative-loop, HITL pause, and cascade are aspects of MANAGED_WORKFLOW
    (per v15 §EDGE CASE CLARIFICATIONS #7), not separate routes.
    """

    R1A_EXACT_CACHE = "R1A_EXACT_CACHE"
    R1B_SEMANTIC_CACHE = "R1B_SEMANTIC_CACHE"
    R3_SIMPLE_GROUNDED_READ = "R3_SIMPLE_GROUNDED_READ"
    R4_SINGLE_ACTION = "R4_SINGLE_ACTION"
    R3R4_MANAGED_WORKFLOW = "R3R4_MANAGED_WORKFLOW"
    R5_FALLBACK = "R5_FALLBACK"


class ExecutionFormV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — three execution forms only."""

    TERMINAL_SHORTCIRCUIT = "TERMINAL_SHORTCIRCUIT"
    SINGLE_STEP = "SINGLE_STEP"
    MANAGED_WORKFLOW = "MANAGED_WORKFLOW"


class ConfidenceClass(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — reasoned confidence class.

    Accompanies the numeric confidence score; downstream gates may key on
    the class without re-thresholding the float.
    """

    EXACT = "EXACT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNSAFE = "UNSAFE"
    INSUFFICIENT_SUPPORT = "INSUFFICIENT_SUPPORT"


class FreshnessClassV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — five freshness tiers."""

    STATIC = "STATIC"
    SLOW_CHANGING = "SLOW_CHANGING"
    RECENT = "RECENT"
    CURRENT = "CURRENT"
    LIVE = "LIVE"


class CachePolicyV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — five cache policies."""

    EXACT_ONLY = "EXACT_ONLY"
    SEMANTIC_OK = "SEMANTIC_OK"
    READ_THROUGH = "READ_THROUGH"
    NO_CACHE = "NO_CACHE"
    BYPASS_CACHE = "BYPASS_CACHE"


class SupportTargetV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — answer-support expectation."""

    NONE = "NONE"
    EXACT_QUOTE = "EXACT_QUOTE"
    SOURCE_BACKED_SUMMARY = "SOURCE_BACKED_SUMMARY"
    POLICY_CLAUSE = "POLICY_CLAUSE"
    CODE_LOCATION = "CODE_LOCATION"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    RANKED_CAUSE = "RANKED_CAUSE"
    ACTION_ARGUMENT_GROUNDING = "ACTION_ARGUMENT_GROUNDING"


class CostTierV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — cost tier adds TIER_HITL over v12."""

    TIER_S = "TIER_S"
    TIER_M = "TIER_M"
    TIER_L = "TIER_L"
    TIER_HITL = "TIER_HITL"


class ReasonCodeV15(str, Enum):
    """v15 §ROUTE CONTRACT SCHEMA — closed reason-code vocabulary.

    Members map exactly to the bullet list under ``reason_codes`` in the v15
    doctrine. New members require an ADR plus an entry on the v15 amendment
    plan.
    """

    SCOPE_FAIL = "SCOPE_FAIL"
    POLICY_BLOCK = "POLICY_BLOCK"
    EXACT_CACHE_HIT = "EXACT_CACHE_HIT"
    SEMANTIC_CACHE_HIT = "SEMANTIC_CACHE_HIT"
    CACHE_EXPIRED = "CACHE_EXPIRED"
    GROUNDING_REQUIRED = "GROUNDING_REQUIRED"
    SUPPORT_WEAK = "SUPPORT_WEAK"
    ACTION_LOW_RISK = "ACTION_LOW_RISK"
    ACTION_HIGH_RISK = "ACTION_HIGH_RISK"
    HITL_REQUIRED = "HITL_REQUIRED"
    MULTI_STEP_REQUIRED = "MULTI_STEP_REQUIRED"
    DEPENDENCY_BRANCHING_REQUIRED = "DEPENDENCY_BRANCHING_REQUIRED"
    GRAPH_REQUIRED = "GRAPH_REQUIRED"
    FRESHNESS_REQUIRED = "FRESHNESS_REQUIRED"
    ACL_BLOCKED = "ACL_BLOCKED"
    TOOL_UNAVAILABLE = "TOOL_UNAVAILABLE"
    PROVIDER_OUTAGE = "PROVIDER_OUTAGE"
    SLO_RISK = "SLO_RISK"
    FALLBACK_SELECTED = "FALLBACK_SELECTED"


class WriteAuthority(str, Enum):
    """v15 §authority — write authority class.

    L0 NEVER writes durable state. The contract MUST declare
    ``NONE_UNTIL_UWG`` until the Universal Write Gateway clears the mutation.
    """

    NONE_UNTIL_UWG = "NONE_UNTIL_UWG"
    UWG_CLEARED = "UWG_CLEARED"


class SafeResponseType(str, Enum):
    """v15 §R5 FALLBACK CONTRACT FIELDS — ``safe_response_type``.

    Categorizes the safe terminal response Exit Eval should render. Required
    on every R5 contract; ignored on non-R5 routes.

    * ``CLARIFY``: ask the user for missing information (intent under-specified
      but resolvable with one safe clarification).
    * ``ABSTAIN``: decline to answer because evidence is insufficient or no
      grounded path is available.
    * ``REFUSE``: decline because the request is unsafe, blocked by policy,
      or out of scope.
    * ``SAFE_PARTIAL``: emit a caveated/partial answer when full grounding
      cannot be obtained but a bounded partial is genuinely safer than a
      full abstain.
    """

    CLARIFY = "CLARIFY"
    ABSTAIN = "ABSTAIN"
    REFUSE = "REFUSE"
    SAFE_PARTIAL = "SAFE_PARTIAL"


class CapabilityClass(str, Enum):
    """v15 §authority — capability class declared on the route."""

    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"
    ACTION = "ACTION"
    REFLECT_ONLY = "REFLECT_ONLY"


class SideEffectClass(str, Enum):
    """v15 §authority — side-effect class declared on the route."""

    PURE = "PURE"
    LOCAL_REVERSIBLE = "LOCAL_REVERSIBLE"
    REMOTE_REVERSIBLE = "REMOTE_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class SandboxClass(str, Enum):
    """v15 §authority — sandbox class declared on the route."""

    NO_SANDBOX = "NO_SANDBOX"
    PROCESS_SANDBOX = "PROCESS_SANDBOX"
    NETWORK_SANDBOX = "NETWORK_SANDBOX"
    FULL_SANDBOX = "FULL_SANDBOX"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class V15RouteContractError(ValueError):
    """Raised when a V15RouteContract violates v15 §INVARIANTS."""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _is_finite_float(value: object) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def _require_nonempty_str(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise V15RouteContractError(
            f"{field_name} must be str, got {type(value).__name__}",
        )
    if len(value) == 0:
        raise V15RouteContractError(f"{field_name} must be non-empty")
    if len(value) > _MAX_STRING_LEN:
        raise V15RouteContractError(
            f"{field_name} exceeds max length {_MAX_STRING_LEN} (got {len(value)})",
        )


def _require_str_tuple(
    values: tuple[str, ...],
    field_name: str,
    *,
    max_len: int,
) -> None:
    if not isinstance(values, tuple):
        raise V15RouteContractError(f"{field_name} must be a tuple")
    if len(values) > max_len:
        raise V15RouteContractError(
            f"{field_name} exceeds max length {max_len} (got {len(values)})",
        )
    for idx, item in enumerate(values):
        if not isinstance(item, str):
            raise V15RouteContractError(f"{field_name}[{idx}] must be str, got {type(item).__name__}")
        if len(item) == 0:
            raise V15RouteContractError(f"{field_name}[{idx}] must be non-empty")
        if len(item) > _MAX_STRING_LEN:
            raise V15RouteContractError(f"{field_name}[{idx}] exceeds max length {_MAX_STRING_LEN}")


def _check_int_field(name: str, value: object, ceiling: int) -> None:
    """Validate one bounded non-negative int field against a ceiling.

    Used by RouteSLOV15 to keep its validation loop body small and
    semantically clean.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise V15RouteContractError(f"{name} must be int")
    if value < 0:
        raise V15RouteContractError(f"{name} must be >= 0")
    if value > ceiling:
        raise V15RouteContractError(f"{name} exceeds ceiling {ceiling} (got {value})")


# ---------------------------------------------------------------------------
# Substructures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FallbackEntryV15:
    """One entry in a v15 fallback_chain. v15 §FIXED DECISION ORDER."""

    route_id: RouteIdV15
    cost_tier: CostTierV15
    provider: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.route_id, RouteIdV15):
            raise V15RouteContractError(
                f"FallbackEntryV15.route_id must be RouteIdV15, got {type(self.route_id).__name__}",
            )
        if not isinstance(self.cost_tier, CostTierV15):
            raise V15RouteContractError(
                f"FallbackEntryV15.cost_tier must be CostTierV15, got {type(self.cost_tier).__name__}",
            )
        if self.provider is not None:
            _require_nonempty_str(self.provider, "FallbackEntryV15.provider")


@dataclass(frozen=True)
class RouteSLOV15:
    """v15 §slo block. All budgets non-negative and finite."""

    max_latency_ms: int
    max_cost: float
    max_tokens: int
    max_retrieval_passes: int
    max_graph_hops: int
    max_tool_calls: int
    max_iterations: int
    reserve_for_exit_eval: int

    def __post_init__(self) -> None:
        _slo_int_checks = (
            ("max_latency_ms", self.max_latency_ms, _MAX_SLO_LATENCY_MS),
            ("max_tokens", self.max_tokens, _MAX_SLO_TOKENS),
            ("max_retrieval_passes", self.max_retrieval_passes, _MAX_SLO_RETRIEVAL_PASSES),
            ("max_graph_hops", self.max_graph_hops, _MAX_SLO_GRAPH_HOPS),
            ("max_tool_calls", self.max_tool_calls, _MAX_SLO_TOOL_CALLS),
            ("max_iterations", self.max_iterations, _MAX_SLO_ITERATIONS),
            ("reserve_for_exit_eval", self.reserve_for_exit_eval, _MAX_SLO_TOKENS),
        )
        for name, value, ceiling in _slo_int_checks:
            _check_int_field(name, value, ceiling)
        if not _is_finite_float(self.max_cost):
            raise V15RouteContractError("max_cost must be finite (no NaN/inf)")
        if self.max_cost < 0.0:
            raise V15RouteContractError("max_cost must be >= 0")
        if self.max_cost > _MAX_SLO_COST_USD:
            raise V15RouteContractError(
                f"max_cost exceeds ceiling {_MAX_SLO_COST_USD} (got {self.max_cost})",
            )


@dataclass(frozen=True)
class AuthorityScope:
    """v15 §authority block.

    Captures the full authority surface the route operates under. The
    invariant ``write_authority == NONE_UNTIL_UWG`` MUST hold for every
    contract emitted by L0 — only UWG flips it to ``UWG_CLEARED`` after
    re-clearance. L0 itself never emits a contract with UWG_CLEARED.
    """

    tenant_scope: str
    acl_scope: tuple[str, ...]
    region_scope: str
    capability_class: CapabilityClass
    side_effect_class: SideEffectClass
    sandbox_class: SandboxClass
    write_authority: WriteAuthority = WriteAuthority.NONE_UNTIL_UWG

    def __post_init__(self) -> None:
        _require_nonempty_str(self.tenant_scope, "AuthorityScope.tenant_scope")
        _require_nonempty_str(self.region_scope, "AuthorityScope.region_scope")
        _require_str_tuple(
            self.acl_scope,
            "AuthorityScope.acl_scope",
            max_len=_MAX_ACL_BOUNDS,
        )
        if not isinstance(self.capability_class, CapabilityClass):
            raise V15RouteContractError(
                "AuthorityScope.capability_class must be CapabilityClass",
            )
        if not isinstance(self.side_effect_class, SideEffectClass):
            raise V15RouteContractError(
                "AuthorityScope.side_effect_class must be SideEffectClass",
            )
        if not isinstance(self.sandbox_class, SandboxClass):
            raise V15RouteContractError(
                "AuthorityScope.sandbox_class must be SandboxClass",
            )
        if not isinstance(self.write_authority, WriteAuthority):
            raise V15RouteContractError(
                "AuthorityScope.write_authority must be WriteAuthority",
            )


@dataclass(frozen=True)
class TelemetryKeysV15:
    """v15 §telemetry_keys block. All fields non-empty strings."""

    trace_root: str
    route_span_id: str
    route_digest: str
    policy_hash: str
    blueprint_hash: str
    snapshot_id: str
    replay_key: str
    route_telemetry_event_id: str

    _FIELDS: ClassVar[tuple[str, ...]] = (
        "trace_root",
        "route_span_id",
        "route_digest",
        "policy_hash",
        "blueprint_hash",
        "snapshot_id",
        "replay_key",
        "route_telemetry_event_id",
    )

    def __post_init__(self) -> None:
        for name in TelemetryKeysV15._FIELDS:
            _require_nonempty_str(getattr(self, name), f"TelemetryKeysV15.{name}")


@dataclass(frozen=True)
class SignaturesV15:
    """v15 §signatures block.

    ``hmac_sig`` defaults to empty (caller signs after construction via
    :meth:`V15RouteContract.sign`). ``manifest_hash`` and
    ``deterministic_route_digest`` MUST be set by the producer.
    """

    manifest_hash: str
    deterministic_route_digest: str
    hmac_sig: str = ""

    def __post_init__(self) -> None:
        _require_nonempty_str(self.manifest_hash, "SignaturesV15.manifest_hash")
        _require_nonempty_str(
            self.deterministic_route_digest,
            "SignaturesV15.deterministic_route_digest",
        )
        if not isinstance(self.hmac_sig, str):
            raise V15RouteContractError("SignaturesV15.hmac_sig must be str")
        if len(self.hmac_sig) > _MAX_STRING_LEN:
            raise V15RouteContractError(
                f"SignaturesV15.hmac_sig exceeds max length {_MAX_STRING_LEN}",
            )


# ---------------------------------------------------------------------------
# v15 RouteContract (top-level)
# ---------------------------------------------------------------------------


_TERMINAL_ROUTES_V15: frozenset[RouteIdV15] = frozenset(
    {
        RouteIdV15.R1A_EXACT_CACHE,
        RouteIdV15.R1B_SEMANTIC_CACHE,
        RouteIdV15.R5_FALLBACK,
    },
)
"""v15 §INVARIANTS — R1A/R1B/R5 are terminal [RET] routes."""

_SINGLE_STEP_ROUTES_V15: frozenset[RouteIdV15] = frozenset(
    {
        RouteIdV15.R3_SIMPLE_GROUNDED_READ,
        RouteIdV15.R4_SINGLE_ACTION,
    },
)
"""v15 §INVARIANTS — R3 and R4 each dispatch exactly one bounded L2 step."""

_MANAGED_WORKFLOW_ROUTES_V15: frozenset[RouteIdV15] = frozenset(
    {RouteIdV15.R3R4_MANAGED_WORKFLOW},
)
"""v15 §INVARIANTS — R3R4_MANAGED_WORKFLOW is the only L3 entry route."""


def _execution_form_for(route_id: RouteIdV15) -> ExecutionFormV15:
    """Canonical execution form per v15 §ROUTE SELECTION MATRIX."""
    if route_id in _TERMINAL_ROUTES_V15:
        return ExecutionFormV15.TERMINAL_SHORTCIRCUIT
    if route_id in _SINGLE_STEP_ROUTES_V15:
        return ExecutionFormV15.SINGLE_STEP
    return ExecutionFormV15.MANAGED_WORKFLOW


def _allowed_cache_policies_for(route_id: RouteIdV15) -> frozenset[CachePolicyV15]:
    """Per-route cache policy whitelist (v15 §ROUTE SELECTION MATRIX)."""
    if route_id == RouteIdV15.R1A_EXACT_CACHE:
        return frozenset({CachePolicyV15.EXACT_ONLY})
    if route_id == RouteIdV15.R1B_SEMANTIC_CACHE:
        return frozenset({CachePolicyV15.SEMANTIC_OK})
    if route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ:
        return frozenset(
            {
                CachePolicyV15.READ_THROUGH,
                CachePolicyV15.NO_CACHE,
                CachePolicyV15.BYPASS_CACHE,
            },
        )
    if route_id in {RouteIdV15.R4_SINGLE_ACTION, RouteIdV15.R5_FALLBACK}:
        return frozenset({CachePolicyV15.NO_CACHE, CachePolicyV15.BYPASS_CACHE})
    # Managed workflow may use any cache policy on a per-step basis; the
    # contract-level value reflects the workflow-wide default.
    return frozenset(CachePolicyV15)


def _classify_confidence(score: float) -> ConfidenceClass:
    """Map a numeric score to the v15 reasoned ConfidenceClass.

    Bounds:

    * score == 1.0  -> EXACT (deterministic cache hit)
    * 0.85 <= s < 1 -> HIGH
    * 0.65 <= s     -> MEDIUM
    * 0.40 <= s     -> LOW
    * 0.0  <= s     -> INSUFFICIENT_SUPPORT

    UNSAFE is not derived from score; it is set explicitly by the caller
    when ingress flagged the request as unsafe.
    """
    if not _is_finite_float(score) or not 0.0 <= score <= 1.0:
        return ConfidenceClass.INSUFFICIENT_SUPPORT
    if score >= 1.0:
        return ConfidenceClass.EXACT
    if score >= 0.85:
        return ConfidenceClass.HIGH
    if score >= 0.65:
        return ConfidenceClass.MEDIUM
    if score >= 0.40:
        return ConfidenceClass.LOW
    return ConfidenceClass.INSUFFICIENT_SUPPORT


@dataclass(frozen=True)
class V15RouteContract:
    """v15 §ROUTE CONTRACT SCHEMA — the deterministic contract emitted by L0.

    Each L1 plan that clears ingress yields exactly one ``V15RouteContract``.
    Downstream layers (C0, Prompt Assembly, L2, L3, Exit Eval, UWG) consume
    this contract and MUST NOT re-decide the route.

    Replay invariant (v15 §INVARIANTS):

        Same packet + same policy_hash + same snapshot_id MUST replay to the
        same ``signatures.deterministic_route_digest``.

    Wall-clock, raw entropy, and live provider drift MUST NOT influence the
    digest. Use :func:`compute_deterministic_route_digest` to compute the
    digest deterministically.
    """

    contract_version: str
    route_id: RouteIdV15
    execution_form: ExecutionFormV15
    confidence_score: float
    confidence_class: ConfidenceClass
    reason_codes: tuple[str, ...]
    freshness_class: FreshnessClassV15
    cache_policy: CachePolicyV15
    support_target: SupportTargetV15
    cost_tier: CostTierV15
    fallback_chain: tuple[FallbackEntryV15, ...]
    slo: RouteSLOV15
    authority: AuthorityScope
    telemetry_keys: TelemetryKeysV15
    signatures: SignaturesV15
    base_contract_id: str = ""
    hitl_pause_points: tuple[str, ...] = field(default_factory=tuple)
    workflow_blueprint_id: str | None = None
    safe_response_type: SafeResponseType | None = None

    def __post_init__(self) -> None:
        # ---- type guards ----
        _require_nonempty_str(self.contract_version, "contract_version")
        if not isinstance(self.route_id, RouteIdV15):
            raise V15RouteContractError(
                f"route_id must be RouteIdV15, got {type(self.route_id).__name__}",
            )
        if not isinstance(self.execution_form, ExecutionFormV15):
            raise V15RouteContractError(
                "execution_form must be ExecutionFormV15",
            )
        if not isinstance(self.confidence_class, ConfidenceClass):
            raise V15RouteContractError(
                "confidence_class must be ConfidenceClass",
            )
        if not isinstance(self.freshness_class, FreshnessClassV15):
            raise V15RouteContractError(
                "freshness_class must be FreshnessClassV15",
            )
        if not isinstance(self.cache_policy, CachePolicyV15):
            raise V15RouteContractError("cache_policy must be CachePolicyV15")
        if not isinstance(self.support_target, SupportTargetV15):
            raise V15RouteContractError("support_target must be SupportTargetV15")
        if not isinstance(self.cost_tier, CostTierV15):
            raise V15RouteContractError("cost_tier must be CostTierV15")
        if not isinstance(self.slo, RouteSLOV15):
            raise V15RouteContractError("slo must be RouteSLOV15")
        if not isinstance(self.authority, AuthorityScope):
            raise V15RouteContractError("authority must be AuthorityScope")
        if not isinstance(self.telemetry_keys, TelemetryKeysV15):
            raise V15RouteContractError("telemetry_keys must be TelemetryKeysV15")
        if not isinstance(self.signatures, SignaturesV15):
            raise V15RouteContractError("signatures must be SignaturesV15")

        # ---- numeric ranges ----
        if not _is_finite_float(self.confidence_score):
            raise V15RouteContractError(
                f"confidence_score must be finite, got {self.confidence_score!r}",
            )
        if not 0.0 <= self.confidence_score <= 1.0:
            raise V15RouteContractError(
                f"confidence_score out of range [0,1]: {self.confidence_score}",
            )

        # ---- closed-vocabulary tuples ----
        _require_str_tuple(
            self.reason_codes,
            "reason_codes",
            max_len=_MAX_REASON_CODES,
        )
        # All reason_codes must be valid ReasonCodeV15 members.
        known_reasons = {r.value for r in ReasonCodeV15}
        for idx, code in enumerate(self.reason_codes):
            if code not in known_reasons:
                raise V15RouteContractError(
                    f"reason_codes[{idx}]={code!r} is not in ReasonCodeV15 vocabulary",
                )

        _require_str_tuple(
            self.hitl_pause_points,
            "hitl_pause_points",
            max_len=_MAX_HITL_PAUSE_POINTS,
        )

        # ---- fallback_chain structural rules ----
        if not isinstance(self.fallback_chain, tuple):
            raise V15RouteContractError("fallback_chain must be a tuple")
        if len(self.fallback_chain) > _MAX_FALLBACK_CHAIN_DEPTH:
            raise V15RouteContractError(
                f"fallback_chain exceeds max depth {_MAX_FALLBACK_CHAIN_DEPTH} "
                f"(got {len(self.fallback_chain)})",
            )
        for idx, entry in enumerate(self.fallback_chain):
            if not isinstance(entry, FallbackEntryV15):
                raise V15RouteContractError(
                    f"fallback_chain[{idx}] must be FallbackEntryV15, got {type(entry).__name__}",
                )
        # No self-reference (same route_id+cost_tier as primary).
        for idx, entry in enumerate(self.fallback_chain):
            if entry.route_id == self.route_id and entry.cost_tier == self.cost_tier:
                raise V15RouteContractError(
                    f"fallback_chain[{idx}] is self-referential: same "
                    f"(route_id={self.route_id.value}, cost_tier={self.cost_tier.value}) as primary",
                )

        # ---- execution_form ↔ route_id coherence (v15 §INVARIANTS) ----
        canonical_form = _execution_form_for(self.route_id)
        if self.execution_form != canonical_form:
            raise V15RouteContractError(
                f"execution_form={self.execution_form.value} incompatible with "
                f"route_id={self.route_id.value} (canonical={canonical_form.value})",
            )

        # ---- cache_policy whitelist ----
        allowed = _allowed_cache_policies_for(self.route_id)
        if self.cache_policy not in allowed:
            raise V15RouteContractError(
                f"cache_policy={self.cache_policy.value} not allowed for "
                f"route_id={self.route_id.value} (allowed={sorted(p.value for p in allowed)})",
            )

        # ---- terminal vs non-terminal fallback rules ----
        if self.route_id in _TERMINAL_ROUTES_V15:
            # Terminal routes typically have an empty chain. R5 itself is
            # the terminal safety net so its chain must be empty.
            if self.route_id == RouteIdV15.R5_FALLBACK and len(self.fallback_chain) > 0:
                raise V15RouteContractError(
                    "R5_FALLBACK must have an empty fallback_chain (it is the terminal safety net)",
                )
        else:
            if len(self.fallback_chain) == 0:
                raise V15RouteContractError(
                    f"non-terminal route {self.route_id.value} requires non-empty fallback_chain",
                )
            # Last entry must be R5_FALLBACK (v15 §INVARIANTS — no silent fallback).
            last = self.fallback_chain[-1]
            if last.route_id != RouteIdV15.R5_FALLBACK:
                raise V15RouteContractError(
                    f"fallback_chain last entry must be R5_FALLBACK, got {last.route_id.value}",
                )
            # R5 must appear at most once and only at the tail.
            r5_count = sum(1 for e in self.fallback_chain if e.route_id == RouteIdV15.R5_FALLBACK)
            if r5_count != 1:
                raise V15RouteContractError(
                    f"fallback_chain must contain R5_FALLBACK exactly once at tail, found {r5_count}",
                )

        # ---- write_authority invariant ----
        if self.authority.write_authority != WriteAuthority.NONE_UNTIL_UWG:
            raise V15RouteContractError(
                f"L0 must emit write_authority=NONE_UNTIL_UWG; got "
                f"{self.authority.write_authority.value}. Only UWG flips this after re-clearance.",
            )

        # ---- managed-workflow specific guards ----
        if self.route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW:
            if self.workflow_blueprint_id is None:
                raise V15RouteContractError(
                    "R3R4_MANAGED_WORKFLOW requires workflow_blueprint_id",
                )
            _require_nonempty_str(
                self.workflow_blueprint_id,
                "workflow_blueprint_id",
            )

        # ---- TIER_HITL must coincide with HITL routes (v15 §EDGE CASE #5) ----
        if self.cost_tier == CostTierV15.TIER_HITL:
            # HITL pause is realized inside MANAGED_WORKFLOW or via R5
            # fallback chain; never on R1A/R1B (cache hits cannot need HITL).
            if self.route_id in {
                RouteIdV15.R1A_EXACT_CACHE,
                RouteIdV15.R1B_SEMANTIC_CACHE,
            }:
                raise V15RouteContractError(
                    f"TIER_HITL incompatible with terminal cache route {self.route_id.value}",
                )

        # ---- R5 fallback specific reason-code requirement ----
        if self.route_id == RouteIdV15.R5_FALLBACK and len(self.reason_codes) == 0:
            raise V15RouteContractError(
                "R5_FALLBACK requires at least one reason_code (no silent fallback)",
            )

        # ---- R5 fallback safe_response_type requirement (v15 §R5 CONTRACT) ----
        if self.route_id == RouteIdV15.R5_FALLBACK:
            if self.safe_response_type is None:
                raise V15RouteContractError(
                    "R5_FALLBACK requires safe_response_type "
                    "(CLARIFY|ABSTAIN|REFUSE|SAFE_PARTIAL) per v15 §R5 CONTRACT",
                )
            if not isinstance(self.safe_response_type, SafeResponseType):
                raise V15RouteContractError(
                    "safe_response_type must be SafeResponseType enum",
                )
        else:
            # Non-R5 routes MUST NOT carry a safe_response_type — it is
            # the terminal-fallback rendering hint and is meaningless on
            # cache/grounded/action/managed paths.
            if self.safe_response_type is not None:
                raise V15RouteContractError(
                    f"safe_response_type is meaningful only on R5_FALLBACK; "
                    f"got {self.safe_response_type.value} on {self.route_id.value}",
                )

        # ---- confidence_class must agree with confidence_score (modulo UNSAFE) ----
        derived = _classify_confidence(self.confidence_score)
        if self.confidence_class != ConfidenceClass.UNSAFE and self.confidence_class != derived:
            raise V15RouteContractError(
                f"confidence_class={self.confidence_class.value} disagrees with derived "
                f"class={derived.value} for confidence_score={self.confidence_score}",
            )

    # ---- canonicalization ------------------------------------------------

    def canonical_payload(self) -> dict[str, object]:
        """Return a JSON-friendly dict (enums → values) excluding hmac_sig.

        Used both for HMAC signing and for deterministic digest computation.
        """
        payload = asdict(self)
        # Strip the embedded hmac_sig so signing remains idempotent.
        if isinstance(payload.get("signatures"), dict) and "hmac_sig" in payload["signatures"]:
            payload["signatures"] = {k: v for k, v in payload["signatures"].items() if k != "hmac_sig"}
        return payload

    def canonical_json(self) -> bytes:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def sign(self, secret_key: bytes) -> "V15RouteContract":
        """Return a copy with ``signatures.hmac_sig`` populated."""
        if not isinstance(secret_key, (bytes, bytearray)):
            raise V15RouteContractError(
                f"secret_key must be bytes, got {type(secret_key).__name__}",
            )
        if len(secret_key) == 0:
            raise V15RouteContractError(
                "secret_key must be non-empty; empty HMAC keys are insecure",
            )
        sig = hmac.new(
            secret_key,
            self.canonical_json(),
            hashlib.sha256,
        ).hexdigest()
        signed_signatures = SignaturesV15(
            manifest_hash=self.signatures.manifest_hash,
            deterministic_route_digest=self.signatures.deterministic_route_digest,
            hmac_sig=sig,
        )
        return V15RouteContract(
            contract_version=self.contract_version,
            route_id=self.route_id,
            execution_form=self.execution_form,
            confidence_score=self.confidence_score,
            confidence_class=self.confidence_class,
            reason_codes=self.reason_codes,
            freshness_class=self.freshness_class,
            cache_policy=self.cache_policy,
            support_target=self.support_target,
            cost_tier=self.cost_tier,
            fallback_chain=self.fallback_chain,
            slo=self.slo,
            authority=self.authority,
            telemetry_keys=self.telemetry_keys,
            signatures=signed_signatures,
            base_contract_id=self.base_contract_id,
            hitl_pause_points=self.hitl_pause_points,
            workflow_blueprint_id=self.workflow_blueprint_id,
            safe_response_type=self.safe_response_type,
        )

    def verify(self, secret_key: bytes) -> bool:
        """Constant-time HMAC verification."""
        if not self.signatures.hmac_sig:
            return False
        expected = hmac.new(
            secret_key,
            self.canonical_json(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, self.signatures.hmac_sig)


# ---------------------------------------------------------------------------
# Deterministic digest + manifest hash
# ---------------------------------------------------------------------------


def compute_deterministic_route_digest(
    *,
    route_id: RouteIdV15,
    execution_form: ExecutionFormV15,
    cache_policy: CachePolicyV15,
    freshness_class: FreshnessClassV15,
    support_target: SupportTargetV15,
    cost_tier: CostTierV15,
    reason_codes: tuple[str, ...],
    fallback_chain: tuple[FallbackEntryV15, ...],
    authority: AuthorityScope,
    policy_hash: str,
    blueprint_hash: str,
    snapshot_id: str,
) -> str:
    """Compute the v15 deterministic route digest.

    v15 §INVARIANTS — *Same RouteContract + same policy_hash + same snapshot
    must replay to the same routing digest. No wall clock, raw entropy,
    hidden state, live provider drift, or mixed-state reads may influence a
    replay-certified route.*

    The digest is a SHA-256 over a stable, sorted JSON of:

    * route_id, execution_form, cache_policy, freshness_class
    * support_target, cost_tier
    * reason_codes (sorted lexicographically — order-independent)
    * fallback_chain (preserved order — fallback order matters)
    * authority (tenant_scope, region_scope, sorted acl_scope, classes)
    * policy_hash, blueprint_hash, snapshot_id

    Returns a 64-char lowercase hex digest.
    """
    # Validate inputs to avoid silently producing an empty/garbage digest.
    if not isinstance(route_id, RouteIdV15):
        raise V15RouteContractError("route_id must be RouteIdV15")
    if not isinstance(execution_form, ExecutionFormV15):
        raise V15RouteContractError("execution_form must be ExecutionFormV15")
    if not isinstance(cache_policy, CachePolicyV15):
        raise V15RouteContractError("cache_policy must be CachePolicyV15")
    if not isinstance(freshness_class, FreshnessClassV15):
        raise V15RouteContractError("freshness_class must be FreshnessClassV15")
    if not isinstance(support_target, SupportTargetV15):
        raise V15RouteContractError("support_target must be SupportTargetV15")
    if not isinstance(cost_tier, CostTierV15):
        raise V15RouteContractError("cost_tier must be CostTierV15")
    if not isinstance(authority, AuthorityScope):
        raise V15RouteContractError("authority must be AuthorityScope")
    _require_nonempty_str(policy_hash, "policy_hash")
    _require_nonempty_str(blueprint_hash, "blueprint_hash")
    _require_nonempty_str(snapshot_id, "snapshot_id")

    # Normalize fallback_chain: tuple of (route_id, cost_tier, provider).
    chain_repr = [(e.route_id.value, e.cost_tier.value, e.provider or "") for e in fallback_chain]

    payload = {
        "route_id": route_id.value,
        "execution_form": execution_form.value,
        "cache_policy": cache_policy.value,
        "freshness_class": freshness_class.value,
        "support_target": support_target.value,
        "cost_tier": cost_tier.value,
        "reason_codes": sorted(reason_codes),
        "fallback_chain": chain_repr,
        "authority": {
            "tenant_scope": authority.tenant_scope,
            "region_scope": authority.region_scope,
            "acl_scope": sorted(authority.acl_scope),
            "capability_class": authority.capability_class.value,
            "side_effect_class": authority.side_effect_class.value,
            "sandbox_class": authority.sandbox_class.value,
            "write_authority": authority.write_authority.value,
        },
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "snapshot_id": snapshot_id,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_manifest_hash(
    *,
    contract_version: str,
    route_digest: str,
    policy_hash: str,
    blueprint_hash: str,
    snapshot_id: str,
) -> str:
    """SHA-256 manifest hash binding contract_version + digest + provenance."""
    _require_nonempty_str(contract_version, "contract_version")
    _require_nonempty_str(route_digest, "route_digest")
    _require_nonempty_str(policy_hash, "policy_hash")
    _require_nonempty_str(blueprint_hash, "blueprint_hash")
    _require_nonempty_str(snapshot_id, "snapshot_id")
    payload = {
        "contract_version": contract_version,
        "route_digest": route_digest,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "snapshot_id": snapshot_id,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_secret_key_from_env(
    env_var: str = "AGENTIC_V15_ROUTE_HMAC_KEY",
) -> bytes:
    """Read the HMAC secret key from environment.

    Raises :class:`V15RouteContractError` when the variable is absent, empty,
    or below the minimum entropy floor (16 bytes). Whitespace is stripped
    from both ends before length checks.
    """
    raw = os.environ.get(env_var, "")
    value = raw.strip() if isinstance(raw, str) else ""
    if not value:
        raise V15RouteContractError(
            f"environment variable {env_var} is unset or empty; "
            "v15 route contract HMAC signing requires a key",
        )
    encoded = value.encode("utf-8")
    if len(encoded) < _MIN_HMAC_KEY_BYTES:
        raise V15RouteContractError(
            f"environment variable {env_var} is too short "
            f"({len(encoded)} bytes); minimum is {_MIN_HMAC_KEY_BYTES}",
        )
    return encoded


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------


__all__ = [
    "AuthorityScope",
    "CachePolicyV15",
    "CapabilityClass",
    "ConfidenceClass",
    "CostTierV15",
    "ExecutionFormV15",
    "FallbackEntryV15",
    "FreshnessClassV15",
    "ReasonCodeV15",
    "RouteIdV15",
    "RouteSLOV15",
    "SafeResponseType",
    "SandboxClass",
    "SideEffectClass",
    "SignaturesV15",
    "SupportTargetV15",
    "TelemetryKeysV15",
    "V15RouteContract",
    "V15RouteContractError",
    "WriteAuthority",
    "_MANAGED_WORKFLOW_ROUTES_V15",
    "_SINGLE_STEP_ROUTES_V15",
    "_TERMINAL_ROUTES_V15",
    "_classify_confidence",
    "compute_deterministic_route_digest",
    "compute_manifest_hash",
    "load_secret_key_from_env",
]
