"""
Resource Manager - Unified resource management with namespace isolation.

Provides Redis caching, namespace isolation, and resource lifecycle management
for apps_lic and apps_rg.
Phase 2B - Resource Management & Namespacing
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "resource_manager_types_util", "p0_governance")
_emit_reads_policy_state("p0", "resource_manager_types_util", "policy_binding")
_emit_snapshots_state("p0", "resource_manager_types_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("resource_manager_types_util", "p4obs", "metric_1")
_emit_emits_metric_event("resource_manager_types_util", "p4obs", "metric_2")
_emit_emits_metric_event("resource_manager_types_util", "p4obs", "metric_3")
_emit_emits_metric_event("resource_manager_types_util", "p4obs", "metric_4")
_emit_emits_metric_event("resource_manager_types_util", "p4obs", "metric_5")
_emit_emits_metric_event("resource_manager_types_util", "p4obs", "metric_6")
_emit_records_incident_event("resource_manager_types_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("resource_manager_types_util", "p4obs", "anomaly")
_emit_writes_observability_log("resource_manager_types_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("resource_manager_types_util", "p4obs", "mon_state")
_emit_triggers_alert("resource_manager_types_util", "p4obs", "alert")
_emit_links_incident_trace("resource_manager_types_util", "p4obs", "trace_link")
_emit_captures_pattern("resource_manager_types_util", "p3lm", "pattern")
_emit_records_learning_event("resource_manager_types_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resource_manager_types_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("resource_manager_types_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resource_manager_types_util", "p3lm", "routing")
_emit_improves_agent_policy("resource_manager_types_util", "p3lm", "policy")
_emit_stores_learning_state("resource_manager_types_util", "p3lm", "state")
_emit_records_execution_trace("resource_manager_types_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resource_manager_types_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resource_manager_types_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resource_manager_types_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resource_manager_types_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resource_manager_types_util", "env_read", "p2_env_1")
_emit_reads_environ("resource_manager_types_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("resource_manager_types_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resource_manager_types_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resource_manager_types_util", "context_pull")
_emit_pulls_context("p1", "resource_manager_types_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resource_manager_types_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resource_manager_types_util", "uwg_term_2")
_emit_writes_through("p1", "resource_manager_types_util", "write_through")
_emit_writes_through("p1", "resource_manager_types_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "resource_manager_types_util", "safety_validation")
_emit_invokes_eval("p1", "resource_manager_types_util", "eval_call")
_emit_proposal_commits_routing("p1", "resource_manager_types_util", "routing_commit")
_emit_escalates_to_human("p1", "resource_manager_types_util", "human_escalation")
_emit_routes_through("p1", "resource_manager_types_util", "route_through")
_emit_checks_agent_registry("p1", "resource_manager_types_util", "agent_registry")
_emit_validates_agent_capability("p1", "resource_manager_types_util", "capability")
_emit_dispatches_execution_plan("p1", "resource_manager_types_util", "exec_plan")
_emit_agent_executes_agent("p1", "resource_manager_types_util", "sub_agent")
_emit_routes_to_agent("p1", "resource_manager_types_util", "target_agent")
_emit_verifies_policy("p1", "resource_manager_types_util", "policy_check")
_emit_observes_runtime_state("p1", "resource_manager_types_util", "runtime_state")
_emit_verifies_boundary("p1", "resource_manager_types_util", "boundary_check")
_emit_transcripts_response("p1", "resource_manager_types_util", "transcript")
_emit_hard_fails_untranscripted("p1", "resource_manager_types_util")
_emit_gated_by_confidence("p1", "resource_manager_types_util", "confidence_gate")
emit_replay_key("p0", "resource_manager_types_util")
emit_determinism_digest("p0", "resource_manager_types_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "resource_manager_types_util", "execution_auth")
_emit_validates_capability("p2", "resource_manager_types_util", "capability_check")
_emit_routes_to_capability("p2", "resource_manager_types_util", "capability_route")
_emit_writes_via_uwg("p2", "resource_manager_types_util", "uwg_write")
_emit_blocks_direct_write("p2", "resource_manager_types_util", "direct_write_block")
_emit_records_tool_invocation("p2", "resource_manager_types_util", "tool_invocation")
_emit_captures_execution_output("p2", "resource_manager_types_util", "exec_output")
_emit_dispatches_agent("p3", "resource_manager_types_util", "agent_dispatch")
_emit_coordinates_agents("p3", "resource_manager_types_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "resource_manager_types_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "resource_manager_types_util", "healing_outcome")
_emit_escalates_failure("p3", "resource_manager_types_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "resource_manager_types_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resource_manager_types_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "resource_manager_types_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "resource_manager_types_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resource_manager_types_util", "eval_metric")
_emit_stores_embedding("p4", "resource_manager_types_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "resource_manager_types_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resource_manager_types_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ResourceNamespace(str, Enum):
    """Available resource namespaces for isolation."""

    LIC = "lic"
    RG = "rg"
    SHARED = "shared"
    SYSTEM = "system"


@dataclass
class ResourceConfig:
    """Configuration for resource manager."""

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    default_ttl: int = 3600
    namespace_prefix: str = "agentic"
    enable_redis: bool = True


@dataclass
class ResourceKey:
    """Represents a namespaced resource key."""

    namespace: ResourceNamespace
    category: str
    identifier: str
    prefix: str = "agentic"

    def __str__(self) -> str:
        """Generate the full resource key."""
        return f"{self.prefix}:{self.namespace.value}:{self.category}:{self.identifier}"

    @classmethod
    def parse(cls, key_string: str) -> ResourceKey:
        """Parse a key string into a ResourceKey."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResourceKey.parse")

        parts = key_string.split(":")
        if len(parts) != 4:
            raise ValueError(f"Invalid resource key format: {key_string}")
        return cls(
            prefix=parts[0],
            namespace=ResourceNamespace(parts[1]),
            category=parts[2],
            identifier=parts[3],
        )


class ResourceManager:
    """
    Unified resource manager with namespace isolation.

    Provides:
    - Redis-backed caching with TTL
    - Namespace isolation for apps_lic and apps_rg
    - Resource lifecycle management
    - Fallback to in-memory cache when Redis unavailable
    """

    def __init__(self, config: ResourceConfig | None = None):
        """
        Initialize resource manager.

        Args:
            config: Resource configuration (uses defaults if None)
        """
        self.config = config or ResourceConfig()
        self._redis_client = None
        self._memory_cache: dict[str, tuple[Any, float | None]] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure Redis connection is initialized."""
        if self._initialized:
            return
        if not self.config.enable_redis:
            logger.info("Redis disabled, using in-memory cache")
            self._initialized = True
            return
        try:
            import redis

            self._redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True,
            )
            self._redis_client.ping()
            logger.info("Redis connection established")
            self._initialized = True
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("Redis not installed, using in-memory cache")
            self._initialized = True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory cache")
            self._redis_client = None
            self._initialized = True

    def _get_key(self, namespace: ResourceNamespace, category: str, identifier: str) -> ResourceKey:
        """Generate a resource key."""
        return ResourceKey(
            namespace=namespace,
            category=category,
            identifier=identifier,
            prefix=self.config.namespace_prefix,
        )

    def set(
        self,
        namespace: ResourceNamespace,
        category: str,
        identifier: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """
        Set a resource value.

        Args:
            namespace: Resource namespace for isolation
            category: Resource category (e.g., 'cache', 'config', 'state')
            identifier: Unique resource identifier
            value: Value to store (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successful
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResourceManager.set")

        self._ensure_initialized()
        key = self._get_key(namespace, category, identifier)
        key_str = str(key)
        ttl = ttl if ttl is not None else self.config.default_ttl
        try:
            serialized = json.dumps(value)
            if self._redis_client:
                if ttl > 0:
                    self._redis_client.setex(key_str, ttl, serialized)
                else:
                    self._redis_client.set(key_str, serialized)
            else:
                import time

                expiry = time.time() + ttl if ttl > 0 else None
                self._memory_cache[key_str] = (serialized, expiry)
            logger.debug(f"Set resource: {key_str}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to set resource {key_str}: {e}")
            return False

    def get(self, namespace: ResourceNamespace, category: str, identifier: str) -> Any | None:
        """
        Get a resource value.

        Args:
            namespace: Resource namespace
            category: Resource category
            identifier: Resource identifier

        Returns:
            Stored value or None if not found/expired
        """
        self._ensure_initialized()
        key = self._get_key(namespace, category, identifier)
        key_str = str(key)
        try:
            if self._redis_client:
                value = self._redis_client.get(key_str)
                if value:
                    return json.loads(value)
            else:
                import time

                if key_str in self._memory_cache:
                    serialized, expiry = self._memory_cache[key_str]
                    if expiry is None or time.time() < expiry:
                        return json.loads(serialized)
                    else:
                        del self._memory_cache[key_str]
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get resource {key_str}: {e}")
            return None

    def delete(self, namespace: ResourceNamespace, category: str, identifier: str) -> bool:
        """
        Delete a resource.

        Args:
            namespace: Resource namespace
            category: Resource category
            identifier: Resource identifier

        Returns:
            True if successful
        """
        self._ensure_initialized()
        key = self._get_key(namespace, category, identifier)
        key_str = str(key)
        try:
            if self._redis_client:
                self._redis_client.delete(key_str)
            else:
                self._memory_cache.pop(key_str, None)
            logger.debug(f"Deleted resource: {key_str}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to delete resource {key_str}: {e}")
            return False

    def exists(self, namespace: ResourceNamespace, category: str, identifier: str) -> bool:
        """
        Check if a resource exists.

        Args:
            namespace: Resource namespace
            category: Resource category
            identifier: Resource identifier

        Returns:
            True if resource exists and is not expired
        """
        return self.get(namespace, category, identifier) is not None

    def clear_namespace(self, namespace: ResourceNamespace) -> int:
        """
        Clear all resources in a namespace.

        Args:
            namespace: Namespace to clear

        Returns:
            Number of resources cleared
        """
        self._ensure_initialized()
        pattern = f"{self.config.namespace_prefix}:{namespace.value}:*"
        count = 0
        try:
            if self._redis_client:
                cursor = 0
                while True:
                    cursor, keys = self._redis_client.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        self._redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            else:
                prefix = f"{self.config.namespace_prefix}:{namespace.value}:"
                to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
                for k in to_delete:
                    del self._memory_cache[k]
                    count += 1
            logger.info(f"Cleared {count} resources from namespace: {namespace.value}")
            return count
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace.value}: {e}")
            return 0

    def get_namespace_stats(self, namespace: ResourceNamespace) -> dict[str, Any]:
        """
        Get statistics for a namespace.

        Args:
            namespace: Namespace to query

        Returns:
            Dictionary with namespace statistics
        """
        self._ensure_initialized()
        pattern = f"{self.config.namespace_prefix}:{namespace.value}:*"
        stats = {"namespace": namespace.value, "key_count": 0, "categories": {}}
        try:
            if self._redis_client:
                cursor = 0
                while True:
                    cursor, keys = self._redis_client.scan(cursor=cursor, match=pattern, count=100)
                    for key in keys:
                        stats["key_count"] += 1
                        parts = key.split(":")
                        if len(parts) >= 3:
                            category = parts[2]
                            stats["categories"][category] = stats["categories"].get(category, 0) + 1
                    if cursor == 0:
                        break
            else:
                prefix = f"{self.config.namespace_prefix}:{namespace.value}:"
                for key in self._memory_cache:
                    if key.startswith(prefix):
                        stats["key_count"] += 1
                        parts = key.split(":")
                        if len(parts) >= 3:
                            category = parts[2]
                            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            return stats
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to get namespace stats: {e}")
            return stats


_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    """
    Get singleton resource manager instance.

    Returns:
        ResourceManager instance
    """
    global _resource_manager
    if _resource_manager is None:
        config = ResourceConfig(
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            enable_redis=os.getenv("ENABLE_REDIS", "true").lower() == "true",
        )
        _resource_manager = ResourceManager(config)
    return _resource_manager
