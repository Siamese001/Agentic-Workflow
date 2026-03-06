"""L0 Routing — Redis decision-acceleration cache seam.

Provides three non-authoritative, hash-keyed read-through helpers:

  RouteDecisionCache
      Memoises ``RouteDecisionArtifact`` outputs keyed by
      ``(intent_hash, policy_hash, routing_state_hash)``.

  RoutingRuleSurfaceCache
      Mirrors the active routing-ruleset snapshot from L4 keyed by
      ``routing_state_hash``.  Read-only — never written to by L0.

  CapabilityRegistryCache
      Mirrors tool-inventory / allowlist envelopes from L4 keyed by
      ``cap_registry_hash``.

Determinism contract
--------------------
* All keys are composed from hashes already present in existing L0
  contracts (``policy_config_hash``, ``routing_state_hash``, etc.).
* No wall-clock timestamps.  No random nonces.
* ``replay_mode=True`` causes every ``get`` to return ``None`` so the
  caller re-derives the value from L4 and records it in the transcript.
* Writing to this cache does NOT modify any L4 state.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import (
    build_cap_registry_key,
    build_route_decision_key,
    build_routing_rule_surface_key,
)
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)

logger = logging.getLogger(__name__)

_DEFAULT_RULE_SURFACE_TTL: int = 3600  # 1 hour
_DEFAULT_ROUTE_DECISION_TTL: int = 1800  # 30 minutes
_DEFAULT_CAP_REGISTRY_TTL: int = 3600  # 1 hour


class RouteDecisionCache:
    """Memoises ``RouteDecisionArtifact`` JSON for identical L0 inputs.

    The value stored is the canonical JSON representation of the artifact's
    serialisable fields.  Callers are responsible for deserialising back to
    the typed artifact.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_ROUTE_DECISION_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached route-decision dict or ``None`` on miss/bypass."""
        key = build_route_decision_key(intent_hash, policy_hash, routing_state_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
        artifact_dict: dict[str, Any],
    ) -> None:
        """Cache *artifact_dict* under the deterministic key.

        ``artifact_dict`` must be the canonical JSON-serialisable
        representation of a ``RouteDecisionArtifact`` — callers must
        produce it from the typed artifact before calling this method.
        """
        key = build_route_decision_key(intent_hash, policy_hash, routing_state_hash)
        self._cache.set_json(key, artifact_dict, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached result or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the
        ``RouteDecisionArtifact`` dict by re-deriving it from L4.  It is
        called **only** on a cache miss.  The result is stored before return.

        This is the canonical wiring point for L0 routing engines.  Engines
        should call this instead of calling ``get()`` and L4 separately.

        Parameters
        ----------
        intent_hash, policy_hash, routing_state_hash:
            Hash inputs that fully determine the routing decision.
        fetch_from_l4:
            Zero-argument callable returning ``dict[str, Any]``.
        replay_mode:
            Pass ``True`` during replay to force re-derivation from L4.
        """
        if not replay_mode:
            cached = self.get(intent_hash, policy_hash, routing_state_hash)
            if cached is not None:
                logger.debug("[L0 cache] route_decision HIT")
                return cached
        logger.debug("[L0 cache] route_decision MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(intent_hash, policy_hash, routing_state_hash, result)
        return result

    def invalidate(
        self,
        intent_hash: str,
        policy_hash: str,
        routing_state_hash: str,
    ) -> None:
        """Explicitly evict a cached decision."""
        key = build_route_decision_key(intent_hash, policy_hash, routing_state_hash)
        self._cache.delete(key)


class RoutingRuleSurfaceCache:
    """Read-only mirror of the active routing-ruleset snapshot from L4.

    This cache is NEVER a source of truth.  The ruleset is fetched from L4
    on every miss; on a hit the cached bytes are returned as a convenience.

    Parameters
    ----------
    ttl_seconds:
        TTL applied when the L4 snapshot is written into Redis.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_RULE_SURFACE_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        routing_state_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached ruleset dict or ``None`` on miss/bypass."""
        key = build_routing_rule_surface_key(routing_state_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        routing_state_hash: str,
        ruleset: dict[str, Any],
    ) -> None:
        """Write *ruleset* (a canonical JSON dict from L4) into the mirror."""
        key = build_routing_rule_surface_key(routing_state_hash)
        self._cache.set_json(key, ruleset, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        routing_state_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached ruleset or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        ruleset dict from L4.  Called only on a cache miss; result is stored.
        """
        if not replay_mode:
            cached = self.get(routing_state_hash)
            if cached is not None:
                logger.debug("[L0 cache] rule_surface HIT")
                return cached
        logger.debug("[L0 cache] rule_surface MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(routing_state_hash, result)
        return result

    def invalidate(self, routing_state_hash: str) -> None:
        """Evict the cached ruleset."""
        key = build_routing_rule_surface_key(routing_state_hash)
        self._cache.delete(key)


class CapabilityRegistryCache:
    """Mirrors the tool-inventory / capability-registry snapshot from L4.

    Value holds allowlists, tool availability booleans, and rate-limit
    envelopes.  This cache is informational — routing decisions that depend
    on capability availability must re-verify against L4 when this cache is
    cold.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied when a registry snapshot is stored.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_CAP_REGISTRY_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        cap_registry_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached capability registry or ``None`` on miss/bypass."""
        key = build_cap_registry_key(cap_registry_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        cap_registry_hash: str,
        registry: dict[str, Any],
    ) -> None:
        """Store *registry* (canonical JSON dict from L4) in the mirror."""
        key = build_cap_registry_key(cap_registry_hash)
        self._cache.set_json(key, registry, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        cap_registry_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached registry or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the current
        capability registry dict from L4.  Called only on a cache miss.
        """
        if not replay_mode:
            cached = self.get(cap_registry_hash)
            if cached is not None:
                logger.debug("[L0 cache] cap_registry HIT")
                return cached
        logger.debug("[L0 cache] cap_registry MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(cap_registry_hash, result)
        return result

    def invalidate(self, cap_registry_hash: str) -> None:
        """Evict the cached registry snapshot."""
        key = build_cap_registry_key(cap_registry_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singletons
# ---------------------------------------------------------------------------

_route_decision_cache: RouteDecisionCache | None = None
_rule_surface_cache: RoutingRuleSurfaceCache | None = None
_cap_registry_cache: CapabilityRegistryCache | None = None


def get_route_decision_cache() -> RouteDecisionCache:
    global _route_decision_cache
    if _route_decision_cache is None:
        _route_decision_cache = RouteDecisionCache()
    return _route_decision_cache


def get_routing_rule_surface_cache() -> RoutingRuleSurfaceCache:
    global _rule_surface_cache
    if _rule_surface_cache is None:
        _rule_surface_cache = RoutingRuleSurfaceCache()
    return _rule_surface_cache


def get_cap_registry_cache() -> CapabilityRegistryCache:
    global _cap_registry_cache
    if _cap_registry_cache is None:
        _cap_registry_cache = CapabilityRegistryCache()
    return _cap_registry_cache
