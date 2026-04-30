"""v9 L0 D1/D2 route gates — compose L4 cache surfaces into L0 dispatch arms.

Audit plan ref: `.windsurf/plans/l0-routing-best-practice-audit-1f9180.md` §W1a
Authoritative doc: `docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v9.md`

This module is the L0-side glue that turns the two existing L4 cache surfaces
into the v9 R1A (exact cache) and R1B (semantic cache) terminal arms:

    L4 (state)                         L0 (routing)                         v9 arm
    ------------------------------     ----------------------------------   -------
    L1ExactCache.get()                 check_d1_exact_cache() ───────────► R1A
    SemanticCacheManager.recall()      check_d2_semantic_cache() ────────► R1B

Neither L4 class is touched here. This module imports lazily, never raises
on a cache miss, and returns ``None`` when the corresponding env gate is off
(fail-closed). When a hit occurs, :func:`check_route_gates` returns a fully
populated :class:`~agentic_core.L0_routing.types.routing_artifact_types.L0RouteContract`
with ``selected_route=R1A|R1B`` and ``execution_form="terminal_return"`` so
the caller can short-circuit the pipeline without ever calling ``select_path``.

W1a deposit: **no call sites yet** by design. W1b/W1c will wire
``path_router.route_with_confidence()`` (or the unified L0 dispatcher from W3)
to consult :func:`check_route_gates` before falling through to the structural
``Path.A/B/C/D`` selector. Keeping this file callerless in W1a preserves the
ability to iterate on the function signature without blast-radius cost.

Environment gates (both default to ``"0"`` — fail-closed):
    EXACT_CACHE_D1_ENABLED   — turn on D1 exact-cache gate
    SEMANTIC_CACHE_D2_ENABLED — turn on D2 semantic-cache gate (existing flag)

When a flag is off the corresponding check returns ``None`` immediately without
touching Redis / ChromaDB. This matches the existing ``SEMANTIC_CACHE_D2_ENABLED``
pattern in ``agentic_core/L4_state/utils/memory/semantic_cache_manager.py``.

Telemetry and contract-emission on hit are deferred to W1b / W3 because they
require the caller's ``trace_id`` and ``policy_hash`` — this module only
produces the :class:`L0RouteContract` shape, not the downstream side effects.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import (
    L0Route,
    L0RouteContract,
    RouteReasonCode,
)
from agentic_core.runtime.config.routing_thresholds import get_threshold

# Side-effect import: wires the L4 semantic-cache evidence resolver to the
# L0 composition root (fail-closed default; apps register real source via
# ``register_evidence_source``). Importing route_gates anywhere in the L0
# boot path is sufficient to install the wiring exactly once.
from agentic_core.L0_routing import composition_root as _composition_root  # noqa: F401

# W5.P5: fail-soft metric emission. Import lazily so any breakage in the
# observability path cannot break the routing hot path.
try:
    from agentic_core.L6_observability.routing_calibration_metrics import (  # guardian: allow-layer-violation -- W5.P5 routing metrics; observability call-back from L0 hot path, wrapped in try/except so routing never hard-depends on L6 and falls back to local no-op stubs
        record_r1_exact_hit,
        record_r1_semantic_hit,
        record_r3_coverage_below_floor,
        record_r3_grounded,
    )

    _METRICS_AVAILABLE = True
except ImportError:  # guardian: allow-log-and-swallow -- observability import is optional; routing decisions must not depend on it

    def record_r1_exact_hit(namespace: str = "default", *, increment: int = 1) -> None:  # type: ignore[misc]
        return None

    def record_r1_semantic_hit(namespace: str = "default", *, increment: int = 1) -> None:  # type: ignore[misc]
        return None

    def record_r3_coverage_below_floor(namespace: str = "default", *, increment: int = 1) -> None:  # type: ignore[misc]
        return None

    def record_r3_grounded(namespace: str = "default", *, increment: int = 1) -> None:  # type: ignore[misc]
        return None

    _METRICS_AVAILABLE = False

Logger = logging.getLogger(__name__)


# =============================================================================
# Request canonicalization
# =============================================================================


def canonical_request_hash(request: dict[str, Any]) -> str:
    """Return a stable SHA-256 hex digest of ``request`` for D1 exact matching.

    The input dict is serialized with ``sort_keys=True`` and compact separators
    so equivalent requests produce identical digests regardless of key order or
    whitespace. Non-JSON-serializable values fall through ``default=str``.

    This is **not** the semantic cache key builder — that lives in
    ``agentic_core.cache.cache_key_builders.build_semantic_cache_d2_key``.
    D1 intentionally uses a simpler key: no tenant_id, no model version,
    no corpus_version. D1's value is strict byte-for-byte match.
    """
    serialized = json.dumps(
        request,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(serialized.encode()).hexdigest()


# =============================================================================
# D1 — Exact cache gate (R1A arm)
# =============================================================================


def _d1_enabled() -> bool:
    """Return True iff ``EXACT_CACHE_D1_ENABLED`` is explicitly set to ``"1"``.

    Fail-closed: any other value (unset, ``"0"``, garbage) → disabled.
    """
    return os.environ.get("EXACT_CACHE_D1_ENABLED", "0").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def check_d1_exact_cache(request: dict[str, Any]) -> dict[str, Any] | None:
    """Return the cached response for ``request`` if a D1 exact hit exists.

    Consults :class:`agentic_core.L4_state.utils.memory.l1_exact_cache.L1ExactCache`
    via its global singleton. A hit is an O(1) SHA-256 key match in Redis
    (or local dict fallback if Redis is unavailable).

    Returns ``None`` on miss, gate disabled, or any infrastructure error.
    The R1A arm treats "cannot determine" as "not hit" — the caller then
    falls through to D2 / select_path / abstain.
    """
    if not _d1_enabled():
        return None
    try:
        # Lazy import to keep L0 module load cheap when D1 is off.
        from agentic_core.L4_state.utils.memory.l1_exact_cache import (  # noqa: PLC0415
            get_global_l1_cache,
        )
    except ImportError as exc:  # guardian: allow-return-none-swallow -- optional L4 dependency: missing import means D1 unavailable, None is the miss-safe default
        Logger.debug("route_gates: L1ExactCache import failed: %s", exc)
        return None
    try:
        cache = get_global_l1_cache()
        request_hash = canonical_request_hash(request)
        hit = cache.get(request_hash)
    except (
        AttributeError,
        RuntimeError,
        ValueError,
    ) as exc:  # guardian: allow-return-none-swallow -- cache recall: non-fatal, None is the miss-safe default
        Logger.debug("route_gates: D1 recall failed: %s", exc)
        return None
    if hit is None:
        return None
    # L1ExactCache returns a CacheHit dataclass; unpack into a dict for the caller.
    response_payload = _parse_l1_response(hit.response)
    if response_payload is None:
        return None
    return {
        "response": response_payload,
        "cache_key": hit.cache_key,
        "query_hash": hit.query_hash,
        "hit_timestamp": hit.hit_timestamp,
        "ttl_seconds": hit.ttl_seconds,
    }


def _parse_l1_response(raw: str) -> Any | None:
    """Parse the ``response`` field stored by ``L1ExactCache.set``.

    ``L1ExactCache`` stores the response as a raw string. When callers stored
    a structured payload they typically serialized JSON; when they stored
    an opaque string, it is returned unchanged. Parse-failure returns the
    original string so the caller still sees a usable value.
    """
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


# =============================================================================
# D2 — Semantic cache gate (R1B arm)
# =============================================================================


def _d2_enabled() -> bool:
    """Return True iff ``SEMANTIC_CACHE_D2_ENABLED`` is explicitly set to ``"1"``.

    This matches the existing gate inside
    ``semantic_cache_manager._init_gptcache`` and
    ``execution_orchestrator._semantic_cache_enabled`` so operators only have
    one switch to flip.
    """
    return os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def check_d2_semantic_cache(
    request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "",
    replay_mode: bool = False,
    flow_class: str | None = None,
    corpus_version: str = "",
    policy_version: str = "",
    similarity_threshold_override: float | None = None,
) -> dict[str, Any] | None:
    """Return the cached response for ``request`` if a D2 semantic hit exists.

    Consults :class:`agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager`
    via its singleton. A hit is a Redis L1 exact-hash match **or** a GPTCache
    L2 embedding-similarity match above the configured threshold.

    The ``MUST_BYPASS_FLOWS`` set on ``SemanticCacheManager`` still applies:
    ``D4_ACTION``, ``HITL``, ``UWG_WRITE``, ``AUDIT_EXIT``, ``REPLAY`` flow
    classes always miss, regardless of cache state. Callers should pass
    ``flow_class`` when known so that bypass is explicit rather than implicit.

    W3.P3: per-namespace threshold lookup. The effective threshold is
    resolved (in order): ``similarity_threshold_override`` kwarg >
    ``ROUTING_THRESHOLD__R1B_SEMANTIC_SIMILARITY`` env var >
    ``namespaces.<namespace>.r1b_semantic_similarity`` in
    ``config/routing_thresholds.yaml`` >
    ``defaults.r1b_semantic_similarity`` >
    hardcoded literal ``0.98``. The resolved threshold is **logged but not
    yet enforced** in this entry point — the underlying
    :class:`SemanticCacheManager` applies its own hardcoded similarity
    check, and retrofitting that is deferred to a follow-on wave with
    broader blast radius. Plans consuming this function for post-hit
    re-validation can read the effective threshold themselves.

    Returns ``None`` on miss, gate disabled, or any infrastructure error.
    """
    if not _d2_enabled():
        return None

    # W3.P3: resolve the per-namespace threshold up front so telemetry +
    # post-hit validation can act on it even if the underlying cache
    # manager uses its own internal literal.
    effective_threshold = (
        similarity_threshold_override
        if similarity_threshold_override is not None
        else get_threshold("r1b_semantic_similarity", namespace=namespace)
    )
    Logger.debug(
        "route_gates: D2 namespace=%s effective_threshold=%.4f",
        namespace,
        effective_threshold,
    )

    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
            CriticalInfrastructureError,
            SemanticCacheManager,
        )
    except ImportError as exc:  # guardian: allow-return-none-swallow -- optional L4 dependency: missing import means D2 unavailable, None signals miss to caller
        Logger.debug("route_gates: SemanticCacheManager import failed: %s", exc)
        return None
    # SemanticCacheManager.recall expects a string context; use canonical JSON
    # so the exact-hash sublayer inside SemanticCacheManager is deterministic
    # across call sites.
    context = json.dumps(request, sort_keys=True, separators=(",", ":"), default=str)
    try:
        cache = SemanticCacheManager.get_instance()
        hit = cache.recall(
            context,
            namespace,
            tenant_id=tenant_id,
            replay_mode=replay_mode,
            flow_class=flow_class,
            corpus_version=corpus_version,
            policy_version=policy_version,
        )
    except CriticalInfrastructureError as exc:  # ADR-079 / W4 P4.3: STRICT-mode infra failure → D2 unavailable, return None to signal miss
        Logger.critical(
            "route_gates: D2 unavailable (STRICT-mode infra failed): %s", exc
        )
        return None
    except (
        AttributeError,
        RuntimeError,
        ValueError,
    ) as exc:  # guardian: allow-return-none-swallow -- cache recall: non-fatal, None signals cache miss as the safe default
        Logger.debug("route_gates: D2 recall failed: %s", exc)
        return None

    # W3.P3: post-hit per-namespace threshold enforcement. If the hit
    # carries a similarity score and it's below the namespace-scoped
    # threshold, reject the hit — the underlying manager may have used
    # a more permissive global threshold.
    if hit is not None and isinstance(hit, dict):
        hit_similarity = hit.get("similarity") or hit.get("similarity_score")
        if isinstance(hit_similarity, (int, float)) and hit_similarity < effective_threshold:
            Logger.info(
                "route_gates: D2 hit rejected by namespace threshold "
                "namespace=%s similarity=%.4f < threshold=%.4f",
                namespace,
                hit_similarity,
                effective_threshold,
            )
            return None
    return hit


# =============================================================================
# Composed gate — D1 then D2
# =============================================================================


def check_route_gates(
    request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "",
    replay_mode: bool = False,
    flow_class: str | None = None,
    policy_hash: str = "no-policy",
    trace_id: str = "no-trace",
    confidence: float = 1.0,
    corpus_version: str = "",
    policy_version: str = "",
) -> tuple[L0RouteContract, dict[str, Any]] | None:
    """Run D1 → D2 in order; return the first hit as a populated contract.

    This is the single entry point that L0 dispatchers (W1b / W3) should call
    BEFORE ``select_path``. It preserves the v9 cascade: exact before semantic,
    both before any work.

    Returns:
        ``(contract, payload)`` on hit, where ``contract`` is a finished
        :class:`L0RouteContract` with ``selected_route`` in
        ``{L0Route.R1A, L0Route.R1B}`` and ``execution_form="terminal_return"``,
        and ``payload`` is the cached response the caller returns to its
        caller. ``None`` on miss — the caller must proceed to downstream
        gates (D3 grounded / D4 action / R5 abstain).

    The contract's ``reason_codes`` are a single-element tuple identifying
    the gate: ``("d1_exact_hit",)`` or ``("d2_semantic_hit",)``. ``confidence``
    is echoed from the caller — if the caller doesn't care, leave it at 1.0
    since cache hits are deterministic by construction.

    Args:
        request: Canonicalized request dict. Must be JSON-serializable.
        namespace: Logical cache namespace (typically agent class or workflow id).
        tenant_id: Optional tenant scope for D2 key derivation.
        replay_mode: Pass-through to ``SemanticCacheManager.recall``.
        flow_class: Pass-through to ``SemanticCacheManager.recall``. Use the
            ``MUST_BYPASS_FLOWS`` labels (``"D4_ACTION"``, ``"HITL"``,
            ``"UWG_WRITE"``, ``"AUDIT_EXIT"``, ``"REPLAY"``) to force a miss.
        policy_hash: Caller's active policy hash for replay parity.
        trace_id: Caller's trace identifier for telemetry correlation.
        confidence: Caller's confidence score; echoed into the contract.
    """
    # D1 first — always cheaper than D2.
    d1_hit = check_d1_exact_cache(request)
    if d1_hit is not None:
        Logger.info(
            "route_gates: D1 exact hit namespace=%s trace=%s",
            namespace,
            trace_id,
        )
        # W5.P5: emit calibration metric for cache-hit rate rollups.
        record_r1_exact_hit(namespace or "default")
        contract: L0RouteContract = {
            "selected_route": L0Route.R1A,
            "confidence": confidence,
            # W1b.P1: draw reason code string from the closed RouteReasonCode
            # vocabulary. The enum's ``.value`` IS the literal "d1_exact_hit"
            # so existing string-equality tests remain green.
            "reason_codes": (RouteReasonCode.D1_EXACT_HIT.value,),
            "freshness_class": "bounded",
            "cache_policy": "exact_only",
            "execution_form": "terminal_return",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }
        return contract, d1_hit
    # D2 second.
    d2_hit = check_d2_semantic_cache(
        request,
        namespace=namespace,
        tenant_id=tenant_id,
        replay_mode=replay_mode,
        flow_class=flow_class,
        corpus_version=corpus_version,
        policy_version=policy_version,
    )
    if d2_hit is not None:
        Logger.info(
            "route_gates: D2 semantic hit namespace=%s trace=%s",
            namespace,
            trace_id,
        )
        # W5.P5: emit calibration metric for cache-hit rate rollups.
        record_r1_semantic_hit(namespace or "default")
        contract = {
            "selected_route": L0Route.R1B,
            "confidence": confidence,
            # W1b.P1: draw reason code string from the closed RouteReasonCode
            # vocabulary (same literal "d2_semantic_hit").
            "reason_codes": (RouteReasonCode.D2_SEMANTIC_HIT.value,),
            "freshness_class": "bounded",
            "cache_policy": "semantic_ok",
            "execution_form": "terminal_return",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }
        return contract, d2_hit
    return None


# =============================================================================
# W3.P1 — R3 grounded-read gate (grounding-need prediction score)
# =============================================================================


def check_r3_grounding_gate(
    grounding_need_score: float,
    *,
    namespace: str = "",
    coverage_score: float | None = None,
    coverage_floor_override: float | None = None,
    threshold_override: float | None = None,
) -> tuple[bool, str]:
    """Decide whether to select R3 (grounded read) based on L1 features.

    Plan: §W3.P1. Implements the Vertex AI dynamic-retrieval pattern on top
    of the feature vector emitted by
    :mod:`agentic_core.L1_cognition.reasoning.ml_decision_support.features.grounding_need_features`.

    Decision rule (evaluated in order):

    1. If ``grounding_need_score`` is :data:`NO_SIGNAL` (caller could not
       compute it), return ``(False, "no_grounding_signal")`` — the
       dispatcher falls back to its payload-shape heuristic.
    2. If ``grounding_need_score < threshold``, return
       ``(False, "below_grounding_threshold")`` — query does not benefit
       from retrieval, pick a non-R3 arm.
    3. If ``coverage_score`` is provided AND below the coverage floor,
       return ``(True, "d3_coverage_below_floor")`` — the caller should
       either broaden retrieval (v11 §C0.6) or route to R5.
    4. Otherwise, return ``(True, "d3_grounding_required")`` — proceed
       to R3 single-step grounded read.

    Args:
        grounding_need_score: Score in ``[0, 1]`` or
            :data:`agentic_core.runtime.contracts.routing_features.NO_SIGNAL`.
        namespace: Cache / agent namespace for threshold lookup.
        coverage_score: Optional post-C0 coverage score in ``[0, 1]``.
            When present, the gate also checks the coverage floor and
            may return the ``below_floor`` reason code.
        coverage_floor_override: Bypass the YAML-configured
            ``c0_coverage_floor`` for testing or per-request overrides.
        threshold_override: Bypass the YAML-configured
            ``r3_grounding_need`` threshold.

    Returns:
        ``(should_ground, reason_code)`` — ``reason_code`` is one of
        ``"no_grounding_signal"``, ``"below_grounding_threshold"``,
        ``"d3_grounding_required"``, ``"d3_coverage_below_floor"``. Values
        match the bare-string vocabulary consumed by
        :attr:`L0RouteContract.reason_codes`.
    """
    # Import the sentinel lazily so the module load order tolerates either
    # agentic_core.runtime.contracts.routing_features being absent (W1
    # not deployed) or absent-by-design.
    from agentic_core.runtime.contracts.routing_features import NO_SIGNAL  # noqa: PLC0415

    if grounding_need_score == NO_SIGNAL:
        return False, "no_grounding_signal"
    if not 0.0 <= grounding_need_score <= 1.0:
        Logger.warning(
            "check_r3_grounding_gate: grounding_need_score=%r outside [0,1]; treating as no-signal",
            grounding_need_score,
        )
        return False, "no_grounding_signal"

    threshold = (
        threshold_override
        if threshold_override is not None
        else get_threshold("r3_grounding_need", namespace=namespace)
    )

    if grounding_need_score < threshold:
        return False, "below_grounding_threshold"

    if coverage_score is not None:
        floor = (
            coverage_floor_override
            if coverage_floor_override is not None
            else get_threshold("c0_coverage_floor", namespace=namespace)
        )
        if coverage_score < floor:
            # W5.P5: emit coverage-below-floor metric for the §C0.6
            # broaden-loop observability surface.
            record_r3_coverage_below_floor(namespace or "default")
            return True, "d3_coverage_below_floor"

    # W5.P5: successful grounded-read dispatch.
    record_r3_grounded(namespace or "default")
    return True, "d3_grounding_required"


__all__ = [
    "canonical_request_hash",
    "check_d1_exact_cache",
    "check_d2_semantic_cache",
    "check_r3_grounding_gate",
    "check_route_gates",
]
