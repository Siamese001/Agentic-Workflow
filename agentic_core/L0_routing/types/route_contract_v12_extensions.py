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
- Defensive validation: reject NaN/infinity, empty required strings,
  negative budgets, self-referential fallback chains, over-long collections,
  empty-string / non-string collection members, empty HMAC keys.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
from dataclasses import asdict, dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Hard limits (reject pathological inputs at construction time)
# ---------------------------------------------------------------------------

_MAX_REASON_CODES = 32
_MAX_TELEMETRY_KEYS = 64
_MAX_ACL_BOUNDS = 64
_MAX_FALLBACK_CHAIN_DEPTH = 8
_MAX_STRING_LEN = 512
_MAX_SLO_LATENCY_MS = 3_600_000  # 1 hour — anything longer is almost certainly a bug
_MAX_SLO_TOKENS = 1_000_000
_MAX_SLO_COST_USD = 100.0


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


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _is_finite_float(value: float) -> bool:
    """True iff value is a real finite float (not NaN, not ±inf)."""
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def _require_nonempty_str(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise V12RouteContractError(f"{field_name} must be str, got {type(value).__name__}")
    if len(value) == 0:
        raise V12RouteContractError(f"{field_name} must be non-empty")
    if len(value) > _MAX_STRING_LEN:
        raise V12RouteContractError(f"{field_name} exceeds max length {_MAX_STRING_LEN} (got {len(value)})")


def _require_str_tuple(values: tuple[str, ...], field_name: str, *, max_len: int) -> None:
    if not isinstance(values, tuple):
        raise V12RouteContractError(f"{field_name} must be a tuple")
    if len(values) > max_len:
        raise V12RouteContractError(f"{field_name} exceeds max length {max_len} (got {len(values)})")
    for idx, item in enumerate(values):
        if not isinstance(item, str):
            raise V12RouteContractError(f"{field_name}[{idx}] must be str, got {type(item).__name__}")
        if len(item) == 0:
            raise V12RouteContractError(f"{field_name}[{idx}] must be non-empty")
        if len(item) > _MAX_STRING_LEN:
            raise V12RouteContractError(f"{field_name}[{idx}] exceeds max length {_MAX_STRING_LEN}")


@dataclass(frozen=True)
class FallbackEntry:
    """One entry in a fallback_chain. v12 §2.1, §6."""

    route_id: RouteId
    cost_tier: CostTier
    provider: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.route_id, RouteId):
            raise V12RouteContractError(
                f"FallbackEntry.route_id must be RouteId enum, got {type(self.route_id).__name__}"
            )
        if not isinstance(self.cost_tier, CostTier):
            raise V12RouteContractError(
                f"FallbackEntry.cost_tier must be CostTier enum, got {type(self.cost_tier).__name__}"
            )
        if self.provider is not None:
            if not isinstance(self.provider, str) or len(self.provider) == 0:
                raise V12RouteContractError("FallbackEntry.provider must be non-empty str or None")
            if len(self.provider) > _MAX_STRING_LEN:
                raise V12RouteContractError(f"FallbackEntry.provider exceeds max length {_MAX_STRING_LEN}")


@dataclass(frozen=True)
class RouteSLO:
    """Per-route SLO/budget. v12 §10.

    All budgets MUST be non-negative and finite. Upper bounds catch
    configuration mistakes (e.g., a runaway latency budget that would mask
    a stuck process).
    """

    latency_budget_ms: int
    token_budget_in: int
    token_budget_out: int
    cost_cap_usd: float

    def __post_init__(self) -> None:
        if not isinstance(self.latency_budget_ms, int) or isinstance(self.latency_budget_ms, bool):
            raise V12RouteContractError("latency_budget_ms must be int")
        if self.latency_budget_ms < 0:
            raise V12RouteContractError("latency_budget_ms must be >= 0")
        if self.latency_budget_ms > _MAX_SLO_LATENCY_MS:
            raise V12RouteContractError(f"latency_budget_ms exceeds ceiling {_MAX_SLO_LATENCY_MS}")
        for name, value in (
            ("token_budget_in", self.token_budget_in),
            ("token_budget_out", self.token_budget_out),
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise V12RouteContractError(f"{name} must be int")
            if value < 0:
                raise V12RouteContractError(f"{name} must be >= 0")
            if value > _MAX_SLO_TOKENS:
                raise V12RouteContractError(f"{name} exceeds ceiling {_MAX_SLO_TOKENS}")
        if not _is_finite_float(self.cost_cap_usd):
            raise V12RouteContractError("cost_cap_usd must be finite (no NaN/inf)")
        if self.cost_cap_usd < 0.0:
            raise V12RouteContractError("cost_cap_usd must be >= 0")
        if self.cost_cap_usd > _MAX_SLO_COST_USD:
            raise V12RouteContractError(f"cost_cap_usd exceeds ceiling {_MAX_SLO_COST_USD}")


@dataclass(frozen=True)
class TenantScope:
    """Ingress pre-filter result. v12 §2.1.

    ``tenant_id`` and ``region`` must be non-empty. ``acl_bounds`` may be
    empty only on an explicit deny-all scope (caller responsibility to flag).
    """

    tenant_id: str
    region: str
    acl_bounds: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_nonempty_str(self.tenant_id, "tenant_id")
        _require_nonempty_str(self.region, "region")
        _require_str_tuple(self.acl_bounds, "acl_bounds", max_len=_MAX_ACL_BOUNDS)


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
        # v12 §2.2 validity rules — type + range + structural
        _require_nonempty_str(self.contract_version, "contract_version")
        _require_nonempty_str(self.base_contract_id, "base_contract_id")
        if not isinstance(self.route_id, RouteId):
            raise V12RouteContractError(f"route_id must be RouteId enum, got {type(self.route_id).__name__}")
        if not isinstance(self.freshness_class, FreshnessClass):
            raise V12RouteContractError("freshness_class must be FreshnessClass enum")
        if not isinstance(self.cache_policy, CachePolicy):
            raise V12RouteContractError("cache_policy must be CachePolicy enum")
        if not isinstance(self.execution_form, ExecutionForm):
            raise V12RouteContractError("execution_form must be ExecutionForm enum")
        if not isinstance(self.cost_tier, CostTier):
            raise V12RouteContractError("cost_tier must be CostTier enum")
        if not isinstance(self.tenant_scope, TenantScope):
            raise V12RouteContractError("tenant_scope must be TenantScope")
        if not isinstance(self.slo, RouteSLO):
            raise V12RouteContractError("slo must be RouteSLO")
        # Confidence: reject NaN / inf / out-of-range in one check.
        if not _is_finite_float(self.confidence):
            raise V12RouteContractError(f"confidence must be a finite float, got {self.confidence!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise V12RouteContractError(f"confidence out of range [0,1]: {self.confidence}")
        _require_str_tuple(self.reason_codes, "reason_codes", max_len=_MAX_REASON_CODES)
        _require_str_tuple(self.telemetry_keys, "telemetry_keys", max_len=_MAX_TELEMETRY_KEYS)
        # Fallback chain structural rules
        if not isinstance(self.fallback_chain, tuple):
            raise V12RouteContractError("fallback_chain must be a tuple")
        if len(self.fallback_chain) > _MAX_FALLBACK_CHAIN_DEPTH:
            raise V12RouteContractError(
                f"fallback_chain exceeds max depth {_MAX_FALLBACK_CHAIN_DEPTH} "
                f"(got {len(self.fallback_chain)})"
            )
        for idx, entry in enumerate(self.fallback_chain):
            if not isinstance(entry, FallbackEntry):
                raise V12RouteContractError(
                    f"fallback_chain[{idx}] must be FallbackEntry, got {type(entry).__name__}"
                )
        # Reject self-referential chains (primary appearing in its own chain),
        # except R5_FALLBACK → R5_FALLBACK which cannot happen (terminal route
        # has empty chain), and except intentional re-try at a different tier
        # (we allow same route_id at a different cost_tier).
        for idx, entry in enumerate(self.fallback_chain):
            if entry.route_id == self.route_id and entry.cost_tier == self.cost_tier:
                raise V12RouteContractError(
                    f"fallback_chain[{idx}] is self-referential: "
                    f"same (route_id={self.route_id}, cost_tier={self.cost_tier}) as primary"
                )
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
            Must be non-empty bytes; empty keys are a well-known HMAC
            footgun and are rejected.
        """
        if not isinstance(secret_key, (bytes, bytearray)):
            raise V12RouteContractError(f"secret_key must be bytes, got {type(secret_key).__name__}")
        if len(secret_key) == 0:
            raise V12RouteContractError("secret_key must be non-empty; empty HMAC keys are insecure")
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


_MIN_HMAC_KEY_BYTES = 16


def load_secret_key_from_env(env_var: str = "AGENTIC_V12_ROUTE_HMAC_KEY") -> bytes:
    """Read the HMAC secret key from environment.

    Raises V12RouteContractError when the variable is absent, empty, or
    below the minimum entropy floor (16 bytes). This is a fail-closed
    posture; production dispatchers should never emit an unsigned
    contract and should never use a trivially-guessable key.

    Whitespace is stripped from both ends before length/entropy checks
    (a trailing newline from ``$(cat keyfile)`` is a common mistake).
    """
    raw = os.environ.get(env_var, "")
    value = raw.strip() if isinstance(raw, str) else ""
    if not value:
        raise V12RouteContractError(
            f"environment variable {env_var} is unset or empty; "
            "v12 route contract HMAC signing requires a key"
        )
    encoded = value.encode("utf-8")
    if len(encoded) < _MIN_HMAC_KEY_BYTES:
        raise V12RouteContractError(
            f"environment variable {env_var} is too short "
            f"({len(encoded)} bytes); minimum is {_MIN_HMAC_KEY_BYTES}"
        )
    return encoded
