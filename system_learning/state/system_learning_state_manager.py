"""System Learning State Management Integration

Integrates system learning with L4 state management infrastructure for
enterprise-grade state patterns, lineage tracking, and snapshot management.

Provides unified state management across all system learning operations
with deterministic state recording, version tracking, and enterprise observability.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    # P1 Execution
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    # P4 Observability
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

# Module-level telemetry initialization
_emit_applies_guardrail("p0", "system_learning_state_manager", "p0_governance")
_emit_reads_policy_state("p0", "system_learning_state_manager", "policy_binding")
_emit_snapshots_state("p0", "system_learning_state_manager", "state_snapshot")

_emit_emits_metric_event("system_learning_state_manager", "p4obs", "metric_1")
_emit_emits_metric_event("system_learning_state_manager", "p4obs", "metric_2")
_emit_emits_metric_event("system_learning_state_manager", "p4obs", "metric_3")
_emit_emits_metric_event("system_learning_state_manager", "p4obs", "metric_4")
_emit_emits_metric_event("system_learning_state_manager", "p4obs", "metric_5")
_emit_emits_metric_event("system_learning_state_manager", "p4obs", "metric_6")
_emit_records_incident_event("system_learning_state_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("system_learning_state_manager", "p4obs", "anomaly")
_emit_writes_observability_log("system_learning_state_manager", "p4obs", "obs_log")
_emit_emits_metric_event("system_learning_state_manager", "p4obs", "mon_state")
_emit_triggers_alert("system_learning_state_manager", "p4obs", "alert")
_emit_links_incident_trace("system_learning_state_manager", "p4obs", "trace_link")
_emit_captures_pattern("system_learning_state_manager", "p3lm", "pattern")
_emit_records_learning_event("system_learning_state_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("system_learning_state_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("system_learning_state_manager", "p3lm", "meta_feed")
_emit_feeds_meta_learning("system_learning_state_manager", "p3lm", "routing")
_emit_improves_agent_policy("system_learning_state_manager", "p3lm", "policy")
_emit_stores_learning_state("system_learning_state_manager", "p3lm", "state")

logger = logging.getLogger(__name__)


class SystemLearningStateType(Enum):
    """Types of system learning state for management."""

    # Learning State
    LEARNING_SESSION = "learning_session"
    MODEL_STATE = "model_state"
    TRAINING_STATE = "training_state"
    INFERENCE_STATE = "inference_state"

    # Configuration State
    CONFIG_STATE = "config_state"
    POLICY_STATE = "policy_state"
    VERSION_STATE = "version_state"

    # Data State
    CACHE_STATE = "cache_state"
    EMBEDDING_STATE = "embedding_state"
    RETRIEVAL_STATE = "retrieval_state"

    # Performance State
    PERFORMANCE_STATE = "performance_state"
    DRIFT_STATE = "drift_state"
    TELEMETRY_STATE = "telemetry_state"


class StateLineageType(Enum):
    """Types of state lineage relationships."""

    PARENT_CHILD = "parent_child"
    VERSION_SUCCESSOR = "version_successor"
    DERIVATION = "derivation"
    AGGREGATION = "aggregation"
    TRANSFORMATION = "transformation"
    SNAPSHOT = "snapshot"


@dataclass
class StateLineageEntry:
    """Entry in state lineage tracking."""

    lineage_type: StateLineageType
    parent_state_id: str
    child_state_id: str
    relationship_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class SystemLearningStateSnapshot:
    """Deterministic state snapshot for system learning operations."""

    # Basic snapshot metadata
    state_id: str
    state_type: SystemLearningStateType
    component_name: str
    snapshot_hash: str
    parent_snapshot_hash: str | None = None

    # Timestamps
    created_at: float = field(default_factory=time.time)
    version: int = 1

    # State content
    state_data: dict[str, Any] = field(default_factory=dict)
    config_hashes: dict[str, str] = field(default_factory=dict)
    policy_hashes: dict[str, str] = field(default_factory=dict)

    # Lineage tracking
    lineage: list[StateLineageEntry] = field(default_factory=list)

    # Performance metrics
    size_bytes: int | None = None
    access_count: int = 0
    last_accessed: float | None = None

    # Validation
    is_validated: bool = False
    validation_errors: list[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute deterministic hash of the snapshot."""
        # Create canonical representation
        canonical_data = {
            "state_id": self.state_id,
            "state_type": self.state_type.value,
            "component_name": self.component_name,
            "version": self.version,
            "state_data": self.state_data,
            "config_hashes": self.config_hashes,
            "policy_hashes": self.policy_hashes,
            "parent_snapshot_hash": self.parent_snapshot_hash,
        }

        # Compute SHA-256 hash
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class SystemLearningStateManager:
    """Enterprise state manager for system learning operations.

    Integrates with L4 state management infrastructure to provide:
    - Deterministic state recording and lineage tracking
    - Version management and state evolution tracking
    - Enterprise observability and compliance
    - Performance monitoring and optimization
    - State validation and integrity checking
    """

    def __init__(
        self,
        component_name: str,
        cache: DeterministicRedisCache | None = None,
        enable_state_caching: bool = True,
        state_cache_ttl: int = 7200,  # 2 hours
        max_snapshots_per_type: int = 1000,
        enable_lineage_tracking: bool = True,
    ) -> None:
        """Initialize system learning state manager."""
        self.component_name = component_name
        self._cache = cache or get_hot_cache()
        self.enable_state_caching = enable_state_caching
        self.state_cache_ttl = state_cache_ttl
        self.max_snapshots_per_type = max_snapshots_per_type
        self.enable_lineage_tracking = enable_lineage_tracking

        # State storage
        self._snapshots: dict[str, SystemLearningStateSnapshot] = {}
        self._lineage: list[StateLineageEntry] = []

        # Metrics
        self._metrics = {
            "snapshots_created": 0,
            "snapshots_accessed": 0,
            "lineage_entries": 0,
            "state_validations": 0,
            "validation_failures": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "snapshots_by_type": {},
        }

        logger.info(f"SystemLearningStateManager initialized for {component_name}")

    async def create_state_snapshot(
        self,
        state_type: SystemLearningStateType,
        state_data: dict[str, Any],
        config_hashes: dict[str, str] | None = None,
        policy_hashes: dict[str, str] | None = None,
        parent_state_id: str | None = None,
        version: int | None = None,
        **metadata: Any,
    ) -> SystemLearningStateSnapshot:
        """Create a new state snapshot with deterministic hashing."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "SystemLearningStateManager.create_state_snapshot"
        )

        # Generate state ID
        state_id = str(uuid.uuid4())

        # Get parent snapshot hash if provided
        parent_snapshot_hash = None
        if parent_state_id and parent_state_id in self._snapshots:
            parent_snapshot_hash = self._snapshots[parent_state_id].snapshot_hash

        # Create snapshot
        snapshot = SystemLearningStateSnapshot(
            state_id=state_id,
            state_type=state_type,
            component_name=self.component_name,
            snapshot_hash="",  # Will be computed
            parent_snapshot_hash=parent_snapshot_hash,
            version=version or 1,
            state_data=state_data,
            config_hashes=config_hashes or {},
            policy_hashes=policy_hashes or {},
            **metadata,
        )

        # Compute deterministic hash
        snapshot.snapshot_hash = snapshot.compute_hash()

        # Validate snapshot
        await self._validate_snapshot(snapshot)

        # Store snapshot
        self._snapshots[state_id] = snapshot

        # Add lineage entry if parent provided
        if parent_state_id and parent_state_id in self._snapshots and self.enable_lineage_tracking:
            lineage_entry = StateLineageEntry(
                lineage_type=StateLineageType.PARENT_CHILD,
                parent_state_id=parent_state_id,
                child_state_id=state_id,
                relationship_metadata=metadata,
            )
            self._lineage.append(lineage_entry)
            snapshot.lineage.append(lineage_entry)

        # Cache snapshot if enabled
        if self.enable_state_caching:
            await self._cache_snapshot(snapshot)

        # Update metrics
        self._metrics["snapshots_created"] += 1
        state_type_key = state_type.value
        self._metrics["snapshots_by_type"][state_type_key] = (
            self._metrics["snapshots_by_type"].get(state_type_key, 0) + 1
        )

        # Emit state events
        _emit_writes_learning_snapshot("p3lm", self.component_name, f"state_snapshot:{state_type.value}")
        _emit_stores_learning_state("p3lm", self.component_name, f"state:{state_type.value}")
        _emit_links_execution_to_snapshot("p4", self.component_name, snapshot.snapshot_hash)

        # Cleanup old snapshots if needed
        await self._cleanup_old_snapshots(state_type)

        logger.info(f"Created state snapshot: {state_type.value} for {self.component_name}")
        return snapshot

    async def get_state_snapshot(
        self,
        state_id: str,
        update_access_stats: bool = True,
    ) -> SystemLearningStateSnapshot | None:
        """Get a state snapshot by ID."""
        # Try cache first
        if self.enable_state_caching:
            cached_snapshot = await self._get_cached_snapshot(state_id)
            if cached_snapshot:
                self._metrics["cache_hits"] += 1
                if update_access_stats:
                    cached_snapshot.access_count += 1
                    cached_snapshot.last_accessed = time.time()
                self._metrics["snapshots_accessed"] += 1
                return cached_snapshot
            else:
                self._metrics["cache_misses"] += 1

        # Get from memory
        if state_id in self._snapshots:
            snapshot = self._snapshots[state_id]
            if update_access_stats:
                snapshot.access_count += 1
                snapshot.last_accessed = time.time()
            self._metrics["snapshots_accessed"] += 1
            return snapshot

        return None

    async def get_snapshots_by_type(
        self,
        state_type: SystemLearningStateType,
        limit: int | None = None,
        sort_by: str = "created_at",
        descending: bool = True,
    ) -> list[SystemLearningStateSnapshot]:
        """Get snapshots by type with optional sorting and limiting."""
        snapshots = [snapshot for snapshot in self._snapshots.values() if snapshot.state_type == state_type]

        # Sort snapshots
        if sort_by == "created_at":
            snapshots.sort(key=lambda s: s.created_at, reverse=descending)
        elif sort_by == "access_count":
            snapshots.sort(key=lambda s: s.access_count, reverse=descending)
        elif sort_by == "version":
            snapshots.sort(key=lambda s: s.version, reverse=descending)

        # Apply limit
        if limit:
            snapshots = snapshots[:limit]

        return snapshots

    async def get_state_lineage(
        self,
        state_id: str,
        max_depth: int = 10,
    ) -> list[StateLineageEntry]:
        """Get lineage information for a state."""
        if not self.enable_lineage_tracking:
            return []

        # Find lineage entries
        lineage_entries = [
            entry
            for entry in self._lineage
            if entry.parent_state_id == state_id or entry.child_state_id == state_id
        ]

        # Limit depth
        if len(lineage_entries) > max_depth:
            lineage_entries = lineage_entries[:max_depth]

        return lineage_entries

    async def update_state_snapshot(
        self,
        state_id: str,
        state_data: dict[str, Any] | None = None,
        config_hashes: dict[str, str] | None = None,
        policy_hashes: dict[str, str] | None = None,
        create_new_version: bool = True,
        **metadata: Any,
    ) -> SystemLearningStateSnapshot | None:
        """Update a state snapshot, optionally creating a new version."""
        existing_snapshot = await self.get_state_snapshot(state_id, update_access_stats=False)
        if not existing_snapshot:
            return None

        if create_new_version:
            # Create new version with lineage
            return await self.create_state_snapshot(
                state_type=existing_snapshot.state_type,
                state_data=state_data or existing_snapshot.state_data,
                config_hashes=config_hashes or existing_snapshot.config_hashes,
                policy_hashes=policy_hashes or existing_snapshot.policy_hashes,
                parent_state_id=state_id,
                version=existing_snapshot.version + 1,
                **metadata,
            )
        else:
            # Update in place (less common)
            if state_data:
                existing_snapshot.state_data.update(state_data)
            if config_hashes:
                existing_snapshot.config_hashes.update(config_hashes)
            if policy_hashes:
                existing_snapshot.policy_hashes.update(policy_hashes)

            # Recompute hash
            existing_snapshot.snapshot_hash = existing_snapshot.compute_hash()

            # Re-validate
            await self._validate_snapshot(existing_snapshot)

            # Update cache
            if self.enable_state_caching:
                await self._cache_snapshot(existing_snapshot)

            return existing_snapshot

    async def delete_state_snapshot(
        self,
        state_id: str,
        cascade_delete: bool = False,
    ) -> bool:
        """Delete a state snapshot."""
        if state_id not in self._snapshots:
            return False

        snapshot = self._snapshots[state_id]

        # Check for children if not cascading
        if not cascade_delete and self.enable_lineage_tracking:
            children = [entry for entry in self._lineage if entry.parent_state_id == state_id]
            if children:
                logger.warning(f"Cannot delete snapshot {state_id}: has child states")
                return False

        # Remove from storage
        del self._snapshots[state_id]

        # Remove lineage entries
        if self.enable_lineage_tracking:
            self._lineage = [
                entry
                for entry in self._lineage
                if entry.parent_state_id != state_id and entry.child_state_id != state_id
            ]

        # Remove from cache
        if self.enable_state_caching:
            cache_key = f"state_snapshot:{state_id}"
            self._cache.delete(cache_key)

        # Emit deletion event
        _emit_records_learning_event(
            "p3lm", self.component_name, f"state_deleted:{snapshot.state_type.value}"
        )

        logger.info(f"Deleted state snapshot: {state_id}")
        return True

    async def _validate_snapshot(
        self,
        snapshot: SystemLearningStateSnapshot,
    ) -> None:
        """Validate a state snapshot."""
        self._metrics["state_validations"] += 1

        validation_errors = []

        # Basic validation
        if not snapshot.state_id:
            validation_errors.append("Missing state_id")

        if not snapshot.snapshot_hash:
            validation_errors.append("Missing snapshot_hash")

        # Hash validation
        computed_hash = snapshot.compute_hash()
        if snapshot.snapshot_hash != computed_hash:
            validation_errors.append(f"Hash mismatch: expected {computed_hash}, got {snapshot.snapshot_hash}")

        # Parent validation
        if snapshot.parent_snapshot_hash and snapshot.parent_snapshot_hash not in [
            s.snapshot_hash for s in self._snapshots.values()
        ]:
            validation_errors.append(f"Parent snapshot not found: {snapshot.parent_snapshot_hash}")

        # Size validation
        if snapshot.size_bytes and snapshot.size_bytes > 100 * 1024 * 1024:  # 100MB limit
            validation_errors.append(f"Snapshot too large: {snapshot.size_bytes} bytes")

        # Store validation results
        snapshot.is_validated = len(validation_errors) == 0
        snapshot.validation_errors = validation_errors

        if not snapshot.is_validated:
            self._metrics["validation_failures"] += 1
            logger.warning(f"Snapshot validation failed: {validation_errors}")
            _emit_captures_runtime_anomaly("p4obs", self.component_name, "snapshot_validation_failed")

    async def _cache_snapshot(
        self,
        snapshot: SystemLearningStateSnapshot,
    ) -> None:
        """Cache a state snapshot."""
        try:
            cache_key = f"state_snapshot:{snapshot.state_id}"

            # Prepare cache data
            cache_data = {
                "state_id": snapshot.state_id,
                "state_type": snapshot.state_type.value,
                "component_name": snapshot.component_name,
                "snapshot_hash": snapshot.snapshot_hash,
                "parent_snapshot_hash": snapshot.parent_snapshot_hash,
                "created_at": snapshot.created_at,
                "version": snapshot.version,
                "state_data": snapshot.state_data,
                "config_hashes": snapshot.config_hashes,
                "policy_hashes": snapshot.policy_hashes,
                "access_count": snapshot.access_count,
                "last_accessed": snapshot.last_accessed,
                "is_validated": snapshot.is_validated,
                "validation_errors": snapshot.validation_errors,
                "lineage_count": len(snapshot.lineage),
            }

            self._cache.set_json(cache_key, cache_data, ttl_seconds=self.state_cache_ttl)

        except Exception as e:
            logger.debug(f"Failed to cache snapshot: {e}")

    async def _get_cached_snapshot(
        self,
        state_id: str,
    ) -> SystemLearningStateSnapshot | None:
        """Get a cached state snapshot."""
        try:
            cache_key = f"state_snapshot:{state_id}"
            cached_data = self._cache.get_json(cache_key)

            if not cached_data:
                return None

            # Reconstruct snapshot
            snapshot = SystemLearningStateSnapshot(
                state_id=cached_data["state_id"],
                state_type=SystemLearningStateType(cached_data["state_type"]),
                component_name=cached_data["component_name"],
                snapshot_hash=cached_data["snapshot_hash"],
                parent_snapshot_hash=cached_data.get("parent_snapshot_hash"),
                created_at=cached_data["created_at"],
                version=cached_data["version"],
                state_data=cached_data["state_data"],
                config_hashes=cached_data["config_hashes"],
                policy_hashes=cached_data["policy_hashes"],
                access_count=cached_data.get("access_count", 0),
                last_accessed=cached_data.get("last_accessed"),
                is_validated=cached_data.get("is_validated", False),
                validation_errors=cached_data.get("validation_errors", []),
            )

            return snapshot

        except Exception as e:
            logger.debug(f"Failed to get cached snapshot: {e}")
            return None

    async def _cleanup_old_snapshots(
        self,
        state_type: SystemLearningStateType,
    ) -> None:
        """Clean up old snapshots to prevent memory bloat."""
        snapshots_of_type = [
            snapshot for snapshot in self._snapshots.values() if snapshot.state_type == state_type
        ]

        if len(snapshots_of_type) <= self.max_snapshots_per_type:
            return

        # Sort by creation time (oldest first)
        snapshots_of_type.sort(key=lambda s: s.created_at)

        # Remove oldest snapshots
        to_remove = snapshots_of_type[: -self.max_snapshots_per_type]
        for snapshot in to_remove:
            await self.delete_state_snapshot(snapshot.state_id, cascade_delete=False)

        logger.info(f"Cleaned up {len(to_remove)} old snapshots for {state_type.value}")

    def get_metrics(self) -> dict[str, Any]:
        """Get state manager metrics."""
        return {
            **self._metrics,
            "total_snapshots": len(self._snapshots),
            "total_lineage_entries": len(self._lineage),
            "cache_hit_rate": (
                self._metrics["cache_hits"] / (self._metrics["cache_hits"] + self._metrics["cache_misses"])
                if (self._metrics["cache_hits"] + self._metrics["cache_misses"]) > 0
                else 0.0
            ),
            "validation_success_rate": (
                (self._metrics["state_validations"] - self._metrics["validation_failures"])
                / self._metrics["state_validations"]
                if self._metrics["state_validations"] > 0
                else 0.0
            ),
        }

    def reset_metrics(self) -> None:
        """Reset state manager metrics."""
        for key in self._metrics:
            if isinstance(self._metrics[key], dict):
                self._metrics[key].clear()
            else:
                self._metrics[key] = 0
        _emit_emits_metric_event("system_learning_state_manager", "p4obs", "state_metrics_reset")


# Component state managers registry
_state_managers: dict[str, SystemLearningStateManager] = {}


def get_state_manager(component_name: str) -> SystemLearningStateManager:
    """Get or create a state manager for a component."""
    if component_name not in _state_managers:
        _state_managers[component_name] = SystemLearningStateManager(component_name)
    return _state_managers[component_name]


__all__ = [
    "SystemLearningStateType",
    "StateLineageType",
    "StateLineageEntry",
    "SystemLearningStateSnapshot",
    "SystemLearningStateManager",
    "get_state_manager",
]
