"""
CacheStrategyManager - TTL and similarity threshold guardrails.

[PHASE 1] Core Infrastructure Implementation

Provides:
- Domain-specific TTL management
- Similarity threshold enforcement
- Cache eviction policies
- Cache poisoning protection
- Healing cycle depth tracking
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.L1_cognition.types.cache_types import (
    MAX_SIMILARITY_THRESHOLD,
    MAX_TTL_SECONDS,
    MIN_SIMILARITY_THRESHOLD,
    MIN_TTL_SECONDS,
    DomainConfig,
    EvictionPolicy,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

Logger = logging.getLogger(__name__)


# Module-level singleton instance
_csm_singleton: Any = None


@dataclass
class CacheStrategyManager:
    """
    Manages TTL and similarity threshold guardrails for Meta-Learning.

    [PHASE 1] Core Infrastructure Implementation

    Features:
    - Domain-specific TTL management
    - Similarity threshold enforcement
    - Cache eviction policies
    - Cache poisoning protection
    - Healing cycle depth tracking
    """

    # Domain configurations (from existing base agents)
    domain_configs: dict[str, DomainConfig] = field(default_factory=dict)

    # State
    _access_times: dict[str, float] = field(default_factory=dict, init=False)
    _access_counts: dict[str, int] = field(default_factory=dict, init=False)
    _healing_depths: dict[str, int] = field(default_factory=dict, init=False)

    # Statistics
    stats: dict[str, Any] = field(
        default_factory=lambda: {
            "evictions": 0,
            "threshold_rejections": 0,
            "depth_limit_hits": 0,
            "poisoning_attempts_blocked": 0,
            "by_domain": {},
        },
    )

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        global _csm_singleton
        if _csm_singleton is None:
            _csm_singleton = super().__new__(cls)
        return _csm_singleton

    def __post_init__(self) -> None:
        """Initialize default domain configurations."""
        if not self.domain_configs:
            self._initialize_default_configs()

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CacheStrategyManager.reset_instance", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CacheStrategyManager.reset_instance", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "CacheStrategyManager.reset_instance"
        )

        global _csm_singleton
        _csm_singleton = None

    def _initialize_default_configs(self) -> None:
        """Initialize default domain configurations."""
        self.domain_configs = {
            # guardian: allow-magic-config
            AGENTIC_CORE_DIR: DomainConfig(
                domain=AGENTIC_CORE_DIR,
                ttl_seconds=3600,  # 1 hour
                similarity_threshold=THRESHOLD,
                max_cache_size=10000,
                eviction_policy=EvictionPolicy.LRU,
                max_healing_depth=5,
            ),
            # guardian: allow-magic-config
            APPS_LIC_DIR: DomainConfig(
                domain=APPS_LIC_DIR,
                ttl_seconds=7200,  # 2 hours (LIC has longer campaign cycles)
                similarity_threshold=THRESHOLD,  # Higher threshold from LICAgentBase
                max_cache_size=5000,
                eviction_policy=EvictionPolicy.LRU,
                max_healing_depth=5,
            ),
            # guardian: allow-magic-config
            APPS_RG_DIR: DomainConfig(
                domain=APPS_RG_DIR,
                ttl_seconds=3600,  # 1 hour
                similarity_threshold=THRESHOLD,  # From RGAgentBase
                max_cache_size=5000,
                eviction_policy=EvictionPolicy.LRU,
                max_healing_depth=5,
            ),
        }

    def get_domain_config(self, domain: str) -> DomainConfig:
        """Get configuration for a domain."""
        # guardian: allow-config-with-logic
        if domain not in self.domain_configs:
            # Create default config for unknown domain
            self.domain_configs[domain] = DomainConfig(domain=domain)
        return self.domain_configs[domain]

    def set_domain_config(self, config: DomainConfig) -> None:
        """Set configuration for a domain."""
        self.domain_configs[config.domain] = config

    # ==================== TTL MANAGEMENT ====================

    def get_ttl(self, domain: str) -> int:
        """Get TTL for a domain."""
        return self.get_domain_config(domain).ttl_seconds

    def set_ttl(self, domain: str, ttl_seconds: int) -> None:
        """Set TTL for a domain."""
        config = self.get_domain_config(domain)
        config.ttl_seconds = max(MIN_TTL_SECONDS, min(MAX_TTL_SECONDS, ttl_seconds))

    def is_expired(self, created_at: float, domain: str) -> bool:
        """Check if an entry has expired based on domain TTL."""
        ttl = self.get_ttl(domain)
        return get_clock().now_epoch() - created_at > ttl

    # ==================== SIMILARITY THRESHOLD ====================

    def get_similarity_threshold(self, domain: str) -> float:
        """Get similarity threshold for a domain."""
        return self.get_domain_config(domain).similarity_threshold

    def set_similarity_threshold(self, domain: str, threshold: float) -> None:
        """Set similarity threshold for a domain."""
        config = self.get_domain_config(domain)
        config.similarity_threshold = max(
            MIN_SIMILARITY_THRESHOLD,
            min(MAX_SIMILARITY_THRESHOLD, threshold),
        )

    def meets_similarity_threshold(
        self,
        similarity: float,
        domain: str,
    ) -> bool:
        """Check if similarity meets domain threshold."""
        threshold = self.get_similarity_threshold(domain)
        if similarity < threshold:
            self.stats["threshold_rejections"] += 1
            self._update_domain_stats(domain, "threshold_rejections")
            return False
        return True

    # ==================== CACHE EVICTION ====================

    def record_access(self, key: str) -> None:
        """Record cache access for eviction tracking."""
        self._access_times[key] = get_clock().now_epoch()
        self._access_counts[key] = self._access_counts.get(key, 0) + 1

    def get_eviction_candidates(
        self,
        domain: str,
        current_size: int,
    ) -> list[str]:
        """
        Get keys to evict based on domain policy.

        Args:
            domain: Domain name
            current_size: Current cache size

        Returns:
            List of keys to evict
        """
        config = self.get_domain_config(domain)
        if current_size <= config.max_cache_size:
            return []

        # Calculate how many to evict (10% of max size)
        evict_count = max(1, int(config.max_cache_size * 0.1))
        candidates: list[str] = []

        # Filter keys by domain
        domain_keys = [k for k in self._access_times.keys() if k.startswith(f"meta_learning:{domain}:")]

        if config.eviction_policy == EvictionPolicy.LRU:
            # Least Recently Used
            sorted_keys = sorted(domain_keys, key=lambda k: self._access_times.get(k, 0))
            candidates = sorted_keys[:evict_count]

        elif config.eviction_policy == EvictionPolicy.LFU:
            # Least Frequently Used
            sorted_keys = sorted(domain_keys, key=lambda k: self._access_counts.get(k, 0))
            candidates = sorted_keys[:evict_count]

        elif config.eviction_policy == EvictionPolicy.FIFO:
            # First In First Out (same as LRU for our tracking)
            sorted_keys = sorted(domain_keys, key=lambda k: self._access_times.get(k, 0))
            candidates = sorted_keys[:evict_count]

        self.stats["evictions"] += len(candidates)
        self._update_domain_stats(domain, "evictions", len(candidates))

        return candidates

    def clear_eviction_tracking(self, key: str) -> None:
        """Clear eviction tracking for a key."""
        self._access_times.pop(key, None)
        self._access_counts.pop(key, None)

    # ==================== HEALING DEPTH TRACKING ====================

    def check_healing_depth(self, agent_name: str, violation_id: str) -> bool:
        """
        Check if healing depth limit has been reached.

        Args:
            agent_name: Name of the agent
            violation_id: Unique violation identifier

        Returns:
            True if healing can proceed, False if limit reached
        """
        key = f"{agent_name}:{violation_id}"
        current_depth = self._healing_depths.get(key, 0)

        # Get domain from agent name (heuristic)
        domain = AGENTIC_CORE_DIR
        if "Lic" in agent_name or "LIC" in agent_name:
            domain = APPS_LIC_DIR
        elif "Rg" in agent_name or "RG" in agent_name:
            domain = APPS_RG_DIR

        max_depth = self.get_domain_config(domain).max_healing_depth

        if current_depth >= max_depth:
            self.stats["depth_limit_hits"] += 1
            self._update_domain_stats(domain, "depth_limit_hits")
            Logger.warning(f"[CacheStrategyManager] Healing depth limit reached: {key}")
            return False

        return True

    def increment_healing_depth(self, agent_name: str, violation_id: str) -> int:
        """Increment healing depth counter."""
        key = f"{agent_name}:{violation_id}"
        self._healing_depths[key] = self._healing_depths.get(key, 0) + 1
        return self._healing_depths[key]

    def reset_healing_depth(self, agent_name: str, violation_id: str) -> None:
        """Reset healing depth counter."""
        key = f"{agent_name}:{violation_id}"
        self._healing_depths.pop(key, None)

    def get_healing_depth(self, agent_name: str, violation_id: str) -> int:
        """Get current healing depth."""
        key = f"{agent_name}:{violation_id}"
        return self._healing_depths.get(key, 0)

    # ==================== CACHE POISONING PROTECTION ====================

    def validate_cache_input(self, key: str, value: Any) -> bool:
        """
        Validate cache input to prevent poisoning.

        Args:
            key: Cache key
            value: Value to cache

        Returns:
            True if valid, False if potentially malicious
        """
        # Check key format
        if not key or not isinstance(key, str):
            self.stats["poisoning_attempts_blocked"] += 1
            return False

        if len(key) > 500:  # Key too long
            self.stats["poisoning_attempts_blocked"] += 1
            return False

        # Check for injection attempts in key
        dangerous_patterns = ["../", "..\\", "\x00", "\n", "\r"]
        for pattern in dangerous_patterns:
            if pattern in key:
                self.stats["poisoning_attempts_blocked"] += 1
                Logger.warning(f"[CacheStrategyManager] Blocked suspicious key: {key[:50]}")
                return False

        # Check value size
        if value is not None:
            try:
                import json

                serialized = json.dumps(value, default=str)
                if len(serialized) > 1000000:  # 1MB limit
                    self.stats["poisoning_attempts_blocked"] += 1
                    return False
            except (TypeError, ValueError):
                self.stats["poisoning_attempts_blocked"] += 1
                return False

        return True

    # ==================== STATISTICS ====================

    def _update_domain_stats(self, domain: str, stat_key: str, count: int = 1) -> None:
        """Update domain-specific statistics."""
        if domain not in self.stats["by_domain"]:
            self.stats["by_domain"][domain] = {
                "evictions": 0,
                "threshold_rejections": 0,
                "depth_limit_hits": 0,
            }
        if stat_key in self.stats["by_domain"][domain]:
            self.stats["by_domain"][domain][stat_key] += count

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        return {
            **self.stats,
            "active_healing_cycles": len(self._healing_depths),
            "tracked_keys": len(self._access_times),
        }

    def get_domain_stats(self, domain: str) -> dict[str, Any]:
        """Get statistics for a specific domain."""
        config = self.get_domain_config(domain)
        domain_stats = self.stats["by_domain"].get(domain, {})
        return {
            "config": {
                "ttl_seconds": config.ttl_seconds,
                "similarity_threshold": config.similarity_threshold,
                "max_cache_size": config.max_cache_size,
                "eviction_policy": config.eviction_policy.value,
                "max_healing_depth": config.max_healing_depth,
            },
            "stats": domain_stats,
        }


# Singleton accessor
_cache_strategy_manager: CacheStrategyManager | None = None


def get_cache_strategy_manager() -> CacheStrategyManager:
    """Get or create the CacheStrategyManager singleton."""
    global _cache_strategy_manager
    if _cache_strategy_manager is None:
        _cache_strategy_manager = CacheStrategyManager()
    return _cache_strategy_manager


def reset_cache_strategy_manager() -> None:
    """[TESTING ONLY] Reset the singleton."""
    global _cache_strategy_manager
    _cache_strategy_manager = None
    CacheStrategyManager.reset_instance()
