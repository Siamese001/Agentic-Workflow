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
)

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
    except (AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-return-none-swallow -- cache recall: non-fatal, None is the miss-safe default
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
) -> dict[str, Any] | None:
    """Return the cached response for ``request`` if a D2 semantic hit exists.

    Consults :class:`agentic_core.L4_state.utils.memory.semantic_cache_manager.SemanticCacheManager`
    via its singleton. A hit is a Redis L1 exact-hash match **or** a GPTCache
    L2 embedding-similarity match above the configured threshold.

    The ``MUST_BYPASS_FLOWS`` set on ``SemanticCacheManager`` still applies:
    ``D4_ACTION``, ``HITL``, ``UWG_WRITE``, ``AUDIT_EXIT``, ``REPLAY`` flow
    classes always miss, regardless of cache state. Callers should pass
    ``flow_class`` when known so that bypass is explicit rather than implicit.

    Returns ``None`` on miss, gate disabled, or any infrastructure error.
    """
    if not _d2_enabled():
        return None
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
            SemanticCacheManager,
        )
    except ImportError as exc:  # guardian: allow-return-none-swallow -- optional L4 dependency: missing import means D2 unavailable, None is the miss-safe default
        Logger.debug("route_gates: SemanticCacheManager import failed: %s", exc)
        return None
    # SemanticCacheManager.recall expects a string context; use canonical JSON
    # so the exact-hash sublayer inside SemanticCacheManager is deterministic
    # across call sites.
    context = json.dumps(request, sort_keys=True, separators=(",", ":"), default=str)
    try:
        cache = SemanticCacheManager.get_instance()
        return cache.recall(
            context,
            namespace,
            tenant_id=tenant_id,
            replay_mode=replay_mode,
            flow_class=flow_class,
            corpus_version=corpus_version,
            policy_version=policy_version,
        )
    except (AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-return-none-swallow -- cache recall: non-fatal, None is the miss-safe default
        Logger.debug("route_gates: D2 recall failed: %s", exc)
        return None


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
        contract: L0RouteContract = {
            "selected_route": L0Route.R1A,
            "confidence": confidence,
            "reason_codes": ("d1_exact_hit",),
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
        contract = {
            "selected_route": L0Route.R1B,
            "confidence": confidence,
            "reason_codes": ("d2_semantic_hit",),
            "freshness_class": "bounded",
            "cache_policy": "semantic_ok",
            "execution_form": "terminal_return",
            "policy_hash": policy_hash,
            "trace_id": trace_id,
        }
        return contract, d2_hit
    return None


__all__ = [
    "canonical_request_hash",
    "check_d1_exact_cache",
    "check_d2_semantic_cache",
    "check_route_gates",
]
