"""v12 L0 Routing — additive type extensions.

Realizes the v12 doctrine surface defined in
``docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v12.md``
without replacing the existing ``routing_contract.py`` / ``routing_telemetry.py``
wiring. These are DATA-ONLY helpers — they attach to or annotate existing
``RoutingContract`` / ``RoutingTelemetry`` records rather than supplanting
them.

Design principle: single-agent-first (v12 §9). We do not fork the contract;
we extend it additively with enums and a minimal ``V12RouteAnnex`` dataclass
that existing callers can opt into.

Constitutional compliance:
- Frozen dataclasses, no mutation after construction.
- Specific exception types (``V12RouteContractError``).
- HMAC-SHA256 signing via ``hmac`` / ``hashlib`` stdlib — no third-party crypto.
- UTF-8 everywhere.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import asdict, dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RouteId(str, Enum):
    """v12 route identifiers. See v12 §2.1."""

    R1A = "R1A"
    R1B = "R1B"
    R3_GROUNDED = "R3_GROUNDED"
    R4_ACTION = "R4_ACTION"
    R3R4_WORKFLOW = "R3R4_WORKFLOW"
    R5_FALLBACK = "R5_FALLBACK"
    R_PAR = "R-PAR"
    R_LOOP = "R-LOOP"
    R_HITL = "R-HITL"
    R_CASC = "R-CASC"


class FreshnessClass(str, Enum):
    """Freshness tolerance — drives cache eligibility. v12 §2.1."""

    REALTIME = "REALTIME"
    FRESH = "FRESH"
    STABLE = "STABLE"
    ARCHIVAL = "ARCHIVAL"


class CachePolicy(str, Enum):
    """Cache policy — v12 §2.1."""

    NO_CACHE = "NO_CACHE"
    EXACT_ONLY = "EXACT_ONLY"
    SEMANTIC_OK = "SEMANTIC_OK"
    CASCADE_CACHE_FIRST = "CASCADE_CACHE_FIRST"


class ExecutionForm(str, Enum):
    """Execution form — v12 §2.1. Encodes handoff vs agent-as-tool (§9.2)."""

    TERMINAL_SHORTCIRCUIT = "TERMINAL_SHORTCIRCUIT"
    SINGLE_STEP = "SINGLE_STEP"
    PARALLEL_FANOUT = "PARALLEL_FANOUT"
    ITERATIVE_LOOP = "ITERATIVE_LOOP"
    MANAGED_WORKFLOW = "MANAGED_WORKFLOW"
    HUMAN_GATED = "HUMAN_GATED"


class CostTier(str, Enum):
    """Cost-capability tier. v12 §5."""

    TIER_S = "TIER_S"
    TIER_M = "TIER_M"
    TIER_L = "TIER_L"


class OutcomeStatus(str, Enum):
    """RouteOutcomeEvent status. v12 §3.2."""

    SUCCESS = "SUCCESS"
    DEGRADED = "DEGRADED"
    FALLBACK_TAKEN = "FALLBACK_TAKEN"
    FAILED = "FAILED"
    HITL_APPROVED = "HITL_APPROVED"
    HITL_REJECTED = "HITL_REJECTED"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class V12RouteContractError(ValueError):
    """Raised when a V12RouteAnnex fails validity rules (v12 §2.2)."""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FallbackEntry:
    """One entry in a fallback_chain. v12 §2.1, §6."""

    route_id: RouteId
    cost_tier: CostTier
    provider: str | None = None


@dataclass(frozen=True)
class RouteSLO:
    """Per-route SLO/budget. v12 §10."""

    latency_budget_ms: int
    token_budget_in: int
    token_budget_out: int
    cost_cap_usd: float


@dataclass(frozen=True)
class TenantScope:
    """Ingress pre-filter result. v12 §2.1."""

    tenant_id: str
    region: str
    acl_bounds: tuple[str, ...]


@dataclass(frozen=True)
class V12RouteAnnex:
    """Additive v12 annex on top of the existing ``RoutingContract``.

    Attaches to an existing contract via ``base_contract_id``. The existing
    ``RoutingContract`` retains its 14-field audit shape; this annex adds
    v12-specific fields without schema migration of the base.

    Validity rules mirror v12 §2.2.
    """

    contract_version: str  # semver, current "1.0.0"
    base_contract_id: str  # FK to RoutingContract.routing_contract_id
    route_id: RouteId
    confidence: float
    reason_codes: tuple[str, ...]
    freshness_class: FreshnessClass
    cache_policy: CachePolicy
    execution_form: ExecutionForm
    cost_tier: CostTier
    fallback_chain: tuple[FallbackEntry, ...]
    slo: RouteSLO
    telemetry_keys: tuple[str, ...]
    tenant_scope: TenantScope
    hmac_sig: str = field(default="")

    def __post_init__(self) -> None:
        # v12 §2.2 validity rules
        if not 0.0 <= self.confidence <= 1.0:
            raise V12RouteContractError(f"confidence out of range [0,1]: {self.confidence}")
        # Cache-hit terminal routes MUST have cache semantics enabled;
        # NO_CACHE on a cache-hit route is contradictory. R5_FALLBACK is
        # terminal but not cache-driven, so NO_CACHE there is legal.
        if self.route_id == RouteId.R1A and self.cache_policy != CachePolicy.EXACT_ONLY:
            raise V12RouteContractError("R1A (exact cache) requires cache_policy == EXACT_ONLY")
        if self.route_id == RouteId.R1B and self.cache_policy not in {
            CachePolicy.SEMANTIC_OK,
            CachePolicy.CASCADE_CACHE_FIRST,
        }:
            raise V12RouteContractError(
                "R1B (semantic cache) requires cache_policy in {SEMANTIC_OK, CASCADE_CACHE_FIRST}"
            )
        if self.execution_form == ExecutionForm.TERMINAL_SHORTCIRCUIT and (
            self.route_id not in {RouteId.R1A, RouteId.R1B, RouteId.R5_FALLBACK}
        ):
            raise V12RouteContractError(
                f"TERMINAL_SHORTCIRCUIT requires route_id in {{R1A, R1B, R5_FALLBACK}}, got {self.route_id}"
            )
        if self.execution_form == ExecutionForm.HUMAN_GATED and (self.route_id != RouteId.R_HITL):
            raise V12RouteContractError("HUMAN_GATED execution_form requires route_id == R-HITL")
        # Non-terminal routes require non-empty fallback_chain (v12 §6.1).
        _terminal = {RouteId.R1A, RouteId.R1B, RouteId.R5_FALLBACK}
        if self.route_id not in _terminal and len(self.fallback_chain) == 0:
            raise V12RouteContractError(
                f"non-terminal route {self.route_id} must have non-empty fallback_chain"
            )
        # R5_FALLBACK must be the last entry when present (v12 §6.1).
        if len(self.fallback_chain) > 0:
            last = self.fallback_chain[-1]
            has_r5 = any(e.route_id == RouteId.R5_FALLBACK for e in self.fallback_chain)
            if has_r5 and last.route_id != RouteId.R5_FALLBACK:
                raise V12RouteContractError("R5_FALLBACK must be the last entry in fallback_chain")

    # ---- canonicalization for HMAC ------------------------------------------------

    def canonical_json(self) -> bytes:
        """Deterministic JSON for HMAC signing. Excludes hmac_sig itself."""
        payload = asdict(self)
        payload.pop("hmac_sig", None)
        # asdict emits enums as their values (strings) because str-enum; tuples become lists.
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign(self, secret_key: bytes) -> "V12RouteAnnex":
        """Return a copy with ``hmac_sig`` populated.

        Parameters
        ----------
        secret_key:
            HMAC key bytes. In production this is provisioned out-of-band
            (key-vault) per dispatcher instance. Never log or persist.
        """
        sig = hmac.new(secret_key, self.canonical_json(), hashlib.sha256).hexdigest()
        # frozen dataclass: rebuild with object.__setattr__-free pattern
        return V12RouteAnnex(
            contract_version=self.contract_version,
            base_contract_id=self.base_contract_id,
            route_id=self.route_id,
            confidence=self.confidence,
            reason_codes=self.reason_codes,
            freshness_class=self.freshness_class,
            cache_policy=self.cache_policy,
            execution_form=self.execution_form,
            cost_tier=self.cost_tier,
            fallback_chain=self.fallback_chain,
            slo=self.slo,
            telemetry_keys=self.telemetry_keys,
            tenant_scope=self.tenant_scope,
            hmac_sig=sig,
        )

    def verify(self, secret_key: bytes) -> bool:
        """Constant-time HMAC verification. Returns False on any mismatch."""
        if not self.hmac_sig:
            return False
        expected = hmac.new(secret_key, self.canonical_json(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.hmac_sig)


# ---------------------------------------------------------------------------
# Telemetry event shapes (v12 §3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteTelemetryEvent:
    """Emitted at dispatch time. v12 §3.1.

    Kept separate from the existing ``RoutingTelemetry`` (which is a runtime
    execution record with 15 spec fields). This event is the *decision*
    record — classifier features and alternatives — that feeds calibration
    analytics (§4.3).
    """

    event_id: str
    trace_id: str
    span_id: str
    route_id: RouteId
    confidence: float
    reason_codes: tuple[str, ...]
    classifier_features: dict[str, str | float]
    classifier_model_id: str
    classifier_version: str
    alternatives_considered: tuple[tuple[RouteId, float], ...]
    calibration_bucket: str
    slo_snapshot: RouteSLO
    tenant_scope_hash: str
    timestamp_utc: str
    dispatcher_pid: int
    dispatcher_build_sha: str


@dataclass(frozen=True)
class RouteOutcomeEvent:
    """Emitted after the route executes. v12 §3.2."""

    event_id_of_decision: str  # join key → RouteTelemetryEvent.event_id
    outcome_status: OutcomeStatus
    observed_latency_ms: int
    observed_tokens_in: int
    observed_tokens_out: int
    observed_cost_usd: float
    fallback_depth: int = 0
    quality_signal: float | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_secret_key_from_env(env_var: str = "AGENTIC_V12_ROUTE_HMAC_KEY") -> bytes:
    """Read the HMAC secret key from environment.

    Raises V12RouteContractError when the variable is absent or empty — this
    is a fail-closed posture; production dispatchers should never emit an
    unsigned contract.
    """
    value = os.environ.get(env_var, "")
    if not value:
        raise V12RouteContractError(
            f"environment variable {env_var} is unset or empty; "
            "v12 route contract HMAC signing requires a key"
        )
    return value.encode("utf-8")
