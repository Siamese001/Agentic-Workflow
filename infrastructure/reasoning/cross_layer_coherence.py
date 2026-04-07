"""Opportunity 2: Cross-Layer Cache Coherence & Synchronization

Implements event-driven cache invalidation, version synchronization,
and consistency monitoring across the 4-layer retrieval pattern.
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from .implementation_plan import FourLayerContractError, FourLayerContractGuard, LayerType

logger = logging.getLogger(__name__)


class InvalidationEvent(Enum):
    """Types of cache invalidation events."""

    DATA_UPDATE = "data_update"
    VERSION_CHANGE = "version_change"
    MANUAL_INVALIDATION = "manual_invalidation"
    TTL_EXPIRY = "ttl_expiry"
    CONSISTENCY_VIOLATION = "consistency_violation"


class SyncStatus(Enum):
    """Synchronization status."""

    SYNCED = "synced"
    PENDING = "pending"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    layer_type: LayerType
    version: str
    created_at: datetime
    last_accessed: datetime
    ttl_seconds: int
    dependencies: set[str] = field(default_factory=set)
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for integrity verification."""
        content = f"{self.key}:{self.version}:{json.dumps(self.value, sort_keys=True, default=str)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)

    def is_stale(self, max_age_seconds: int) -> bool:
        """Check if entry is stale."""
        return datetime.now() > self.created_at + timedelta(seconds=max_age_seconds)

    def verify_integrity(self) -> bool:
        """Verify that current payload matches checksum."""
        return self.checksum == self._calculate_checksum()


@dataclass
class InvalidationMessage:
    """Cache invalidation message."""

    event_id: str
    event_type: InvalidationEvent
    layer_type: LayerType
    affected_keys: list[str]
    version: str | None = None
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source_layer: LayerType | None = None
    cascade_to_layers: list[LayerType] = field(default_factory=list)


@dataclass
class SyncStatusInfo:
    """Synchronization status information."""

    layer_type: LayerType
    status: SyncStatus
    last_sync: datetime
    pending_operations: int
    failed_operations: int
    conflicts: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class EventDrivenInvalidationBus:
    """Event bus for cross-layer cache invalidation."""

    def __init__(self):
        self.subscribers: dict[LayerType, list[Callable]] = defaultdict(list)
        self.event_history: deque[InvalidationMessage] = deque(maxlen=10000)
        self._lock = asyncio.Lock()

    def subscribe(self, layer_type: LayerType, callback: Callable[[InvalidationMessage], None]):
        """Subscribe to invalidation events."""
        self.subscribers[layer_type].append(callback)
        logger.info(f"Layer {layer_type} subscribed to invalidation events")

    async def publish(self, message: InvalidationMessage):
        """Publish invalidation event."""
        async with self._lock:
            self.event_history.append(message)
            logger.info(f"Published invalidation event: {message.event_type} for {message.layer_type}")

        # Notify subscribers
        tasks = []
        for layer_type, callbacks in self.subscribers.items():
            if layer_type in message.cascade_to_layers or layer_type == message.layer_type:
                for callback in callbacks:
                    tasks.append(self._safe_notify(callback, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_notify(self, callback: Callable, message: InvalidationMessage):
        """Safely notify subscriber."""
        try:
            await callback(message)
        except Exception as e:
            logger.error(f"Error notifying subscriber: {e}")

    def get_event_history(
        self, layer_type: LayerType | None = None, since: datetime | None = None,
    ) -> list[InvalidationMessage]:
        """Get event history."""
        events = list(self.event_history)

        if layer_type:
            events = [e for e in events if e.layer_type == layer_type or layer_type in e.cascade_to_layers]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events


class VersionManager:
    """Manages versioning and consistency across layers."""

    def __init__(self):
        self.versions: dict[str, str] = {}  # key -> version
        self.version_history: dict[str, list[str]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def get_version(self, key: str) -> str:
        """Get current version for key."""
        async with self._lock:
            return self.versions.get(key, "v1.0.0")

    async def update_version(self, key: str, new_version: str) -> bool:
        """Update version for key."""
        async with self._lock:
            old_version = self.versions.get(key)
            if old_version != new_version:
                self.versions[key] = new_version
                self.version_history[key].append(new_version)
                logger.info(f"Updated version for {key}: {old_version} -> {new_version}")
                return True
        return False

    def get_version_history(self, key: str) -> list[str]:
        """Get version history for key."""
        return list(self.version_history[key])

    async def compare_versions(self, key: str, version: str) -> str:
        """Compare versions (older, same, newer)."""
        current = await self.get_version(key)

        if current == version:
            return "same"
        elif self._is_newer_version(version, current):
            return "newer"
        else:
            return "older"

    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """Check if version1 is newer than version2."""
        try:
            v1_parts = [int(x) for x in version1.replace("v", "").split(".")]
            v2_parts = [int(x) for x in version2.replace("v", "").split(".")]

            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 > v2:
                    return True
                elif v1 < v2:
                    return False

            return len(v1_parts) > len(v2_parts)
        except (ValueError, TypeError, RuntimeError) as e:
            return version1 > version2


class DistributedLockManager:
    """Manages distributed locks for cache operations."""

    def __init__(self):
        self.locks: dict[str, asyncio.Lock] = {}
        self.lock_holders: dict[str, str] = {}
        self.lock_timeouts: dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def acquire_lock(self, key: str, holder: str, timeout_seconds: int = 30) -> bool:
        """Acquire distributed lock."""
        async with self._lock:
            # Check if lock is available
            if key in self.lock_holders:
                holder_info = self.lock_holders[key]
                timeout = self.lock_timeouts.get(key)

                # Check if lock has expired
                if timeout and datetime.now() > timeout:
                    del self.lock_holders[key]
                    del self.lock_timeouts[key]
                else:
                    return False  # Lock is held and not expired

            # Acquire lock
            if key not in self.locks:
                self.locks[key] = asyncio.Lock()

            try:
                await asyncio.wait_for(self.locks[key].acquire(), timeout=timeout_seconds)
                self.lock_holders[key] = holder
                self.lock_timeouts[key] = datetime.now() + timedelta(seconds=timeout_seconds)
                logger.info(f"Lock acquired for {key} by {holder}")
                return True
            except asyncio.TimeoutError:
                return False

    async def release_lock(self, key: str, holder: str) -> bool:
        """Release distributed lock."""
        async with self._lock:
            if self.lock_holders.get(key) == holder:
                lock_obj = self.locks.get(key)
                if lock_obj and lock_obj.locked():
                    lock_obj.release()
                del self.lock_holders[key]
                del self.lock_timeouts[key]
                logger.info(f"Lock released for {key} by {holder}")
                return True
            return False

    def is_locked(self, key: str) -> bool:
        """Check if key is locked."""
        return key in self.lock_holders

    def get_lock_info(self) -> dict[str, dict[str, Any]]:
        """Get lock information."""
        info = {}
        for key, holder in self.lock_holders.items():
            timeout = self.lock_timeouts.get(key)
            info[key] = {
                "holder": holder,
                "timeout": timeout.isoformat() if timeout else None,
                "expired": timeout is not None and datetime.now() > timeout if timeout else False,
            }
        return info


class ConsistencyMonitor:
    """Monitors and resolves cache consistency issues."""

    def __init__(self, check_interval_seconds: int = 60):
        self.check_interval = check_interval_seconds
        self.inconsistencies: dict[str, list[str]] = defaultdict(list)
        self.resolution_history: list[dict[str, Any]] = []
        self._running = False

    async def start_monitoring(self, coherence_manager):
        """Start consistency monitoring."""
        self._running = True
        while self._running:
            await self._check_consistency(coherence_manager)
            await asyncio.sleep(self.check_interval)

    async def stop_monitoring(self):
        """Stop consistency monitoring."""
        self._running = False

    def record_invalidation(self, layer_type: LayerType, key: str, reason: str):
        """Record invalidation event for tracking."""
        self.inconsistencies[key].append(f"Invalidated in {layer_type.value}: {reason}")

    async def _check_consistency(self, coherence_manager):
        """Check consistency across layers."""
        # Get all keys from all layers
        all_keys = set()
        layer_data = {}

        for layer_type in LayerType:
            cache = coherence_manager.layer_caches.get(layer_type)
            if cache:
                layer_keys = set(cache.keys())
                all_keys.update(layer_keys)
                layer_data[layer_type] = {k: cache.get(k) for k in layer_keys}

        # Check consistency
        for key in all_keys:
            inconsistencies = []
            entries = {}

            for layer_type, data in layer_data.items():
                if key in data:
                    entries[layer_type] = data[key]

            if len(entries) > 1:
                # Check for version mismatches
                versions = {layer: entry.version for layer, entry in entries.items()}
                if len(set(versions.values())) > 1:
                    inconsistencies.append(f"Version mismatch: {versions}")

                # Check for checksum mismatches
                checksums = {layer: entry.checksum for layer, entry in entries.items()}
                if len(set(checksums.values())) > 1:
                    inconsistencies.append(f"Checksum mismatch: {checksums}")

                # Check for TTL mismatches
                ttls = {layer: entry.ttl_seconds for layer, entry in entries.items()}
                if len(set(ttls.values())) > 1:
                    inconsistencies.append(f"TTL mismatch: {ttls}")

            if inconsistencies:
                self.inconsistencies[key].extend(inconsistencies)
                await self._resolve_inconsistency(key, entries, inconsistencies, coherence_manager)

    async def _resolve_inconsistency(
        self, key: str, entries: dict[LayerType, CacheEntry], inconsistencies: list[str], coherence_manager,
    ):
        """Resolve consistency inconsistency."""
        resolution = {
            "key": key,
            "timestamp": datetime.now(),
            "inconsistencies": inconsistencies,
            "entries": {layer.value: entry.__dict__ for layer, entry in entries.items()},
            "resolution": "automatic",
        }

        # Simple resolution strategy: use the most recent entry
        most_recent_entry = max(entries.values(), key=lambda e: e.created_at)
        most_recent_layer = None

        for layer, entry in entries.items():
            if entry == most_recent_entry:
                most_recent_layer = layer
                break

        # Update other layers with the most recent entry
        for layer_type, entry in entries.items():
            if layer_type != most_recent_layer:
                await coherence_manager.update_cache_entry(
                    layer_type,
                    key,
                    most_recent_entry.value,
                    most_recent_entry.version,
                    most_recent_entry.ttl_seconds,
                )

        resolution["resolution_action"] = f"Updated all layers with entry from {most_recent_layer.value}"
        self.resolution_history.append(resolution)

        logger.info(f"Resolved inconsistency for {key}: {resolution['resolution_action']}")

    def get_inconsistency_report(self) -> dict[str, Any]:
        """Get inconsistency report."""
        return {
            "total_inconsistencies": len(self.inconsistencies),
            "inconsistencies_by_key": dict(self.inconsistencies),
            "resolution_history": self.resolution_history[-100:],  # Last 100 resolutions
            "monitoring_active": self._running,
        }


class CrossLayerCoherenceManager:
    """Manages cross-layer cache coherence and synchronization."""

    def __init__(self):
        self.layer_caches: dict[LayerType, dict[str, CacheEntry]] = defaultdict(dict)
        self.invalidation_bus = EventDrivenInvalidationBus()
        self.version_manager = VersionManager()
        self.lock_manager = DistributedLockManager()
        self.consistency_monitor = ConsistencyMonitor()
        self.contract_guard = FourLayerContractGuard()

        # Subscribe layers to invalidation events
        for layer_type in LayerType:
            self.invalidation_bus.subscribe(layer_type, self._handle_invalidation)

        self.sync_status: dict[LayerType, SyncStatusInfo] = {}
        self._initialize_sync_status()

    def _initialize_sync_status(self):
        """Initialize sync status for all layers."""
        for layer_type in LayerType:
            self.sync_status[layer_type] = SyncStatusInfo(
                layer_type=layer_type,
                status=SyncStatus.SYNCED,
                last_sync=datetime.now(),
                pending_operations=0,
                failed_operations=0,
            )

    async def start_monitoring(self):
        """Start consistency monitoring."""
        asyncio.create_task(self.consistency_monitor.start_monitoring(self))

    async def stop_monitoring(self):
        """Stop consistency monitoring."""
        await self.consistency_monitor.stop_monitoring()

    async def add_cache_entry(
        self,
        layer_type: LayerType,
        key: str,
        value: Any,
        version: str,
        ttl_seconds: int = 3600,
        dependencies: set[str] | None = None,
    ) -> bool:
        """Add cache entry to layer."""
        try:
            self.contract_guard.validate_exact_lookup_key(key)
        except FourLayerContractError as e:    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context
            raise ValueError(f"Invalid cache key: {e}") from e

        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")

        lock_acquired = await self.lock_manager.acquire_lock(key, f"add_{layer_type.value}")
        if not lock_acquired:
            return False

        try:
            entry = CacheEntry(
                key=key,
                value=value,
                layer_type=layer_type,
                version=version,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                ttl_seconds=ttl_seconds,
                dependencies=dependencies or set(),
            )

            self.layer_caches[layer_type][key] = entry
            await self.version_manager.update_version(key, version)

            # Publish update event
            message = InvalidationMessage(
                event_id=f"update_{int(time.time())}_{key}",
                event_type=InvalidationEvent.DATA_UPDATE,
                layer_type=layer_type,
                affected_keys=[key],
                version=version,
                reason="Cache entry added",
                cascade_to_layers=self._get_dependent_layers(layer_type),
            )

            await self.invalidation_bus.publish(message)

            logger.info(f"Added cache entry {key} to {layer_type}")
            return True

        finally:
            await self.lock_manager.release_lock(key, f"add_{layer_type.value}")

    async def update_cache_entry(
        self, layer_type: LayerType, key: str, value: Any, version: str, ttl_seconds: int = 3600,
    ) -> bool:
        """Update cache entry."""
        try:
            self.contract_guard.validate_exact_lookup_key(key)
        except FourLayerContractError as e:    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context
            raise ValueError(f"Invalid cache key: {e}") from e

        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")

        lock_acquired = await self.lock_manager.acquire_lock(key, f"update_{layer_type.value}")
        if not lock_acquired:
            return False

        try:
            if key in self.layer_caches[layer_type]:
                entry = self.layer_caches[layer_type][key]
                entry.value = value
                entry.version = version
                entry.last_accessed = datetime.now()
                entry.ttl_seconds = ttl_seconds
                entry.checksum = entry._calculate_checksum()

                await self.version_manager.update_version(key, version)

                # Publish update event
                message = InvalidationMessage(
                    event_id=f"update_{int(time.time())}_{key}",
                    event_type=InvalidationEvent.VERSION_CHANGE,
                    layer_type=layer_type,
                    affected_keys=[key],
                    version=version,
                    reason="Cache entry updated",
                    cascade_to_layers=self._get_dependent_layers(layer_type),
                )

                await self.invalidation_bus.publish(message)

                logger.info(f"Updated cache entry {key} in {layer_type}")
                return True
            else:
                return False

        finally:
            await self.lock_manager.release_lock(key, f"update_{layer_type.value}")

    async def invalidate_cache_entry(self, layer_type: LayerType, key: str, reason: str = "") -> bool:
        """Invalidate cache entry."""
        try:
            self.contract_guard.validate_exact_lookup_key(key)
        except FourLayerContractError as e:    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context
            raise ValueError(f"Invalid cache key: {e}") from e

        lock_acquired = await self.lock_manager.acquire_lock(key, f"invalidate_{layer_type.value}")
        if not lock_acquired:
            return False

        try:
            if key in self.layer_caches[layer_type]:
                del self.layer_caches[layer_type][key]

                # Create invalidation message
                message = InvalidationMessage(
                    event_id=str(uuid.uuid4()),
                    event_type=InvalidationEvent.MANUAL_INVALIDATION,
                    layer_type=layer_type,
                    affected_keys=[key],
                    cascade_to_layers=self._get_dependent_layers(layer_type),
                )

                # Send to invalidation bus
                await self.invalidation_bus.publish(message)

                # Update consistency monitor
                self.consistency_monitor.record_invalidation(layer_type, key, reason)

                logger.info(f"Invalidated cache entry {key} in {layer_type}")
                return True
            else:
                return False

        finally:
            await self.lock_manager.release_lock(key, f"invalidate_{layer_type.value}")

    async def get_cache_entry(self, layer_type: LayerType, key: str) -> CacheEntry | None:
        """Get cache entry."""
        try:
            self.contract_guard.validate_exact_lookup_key(key)
        except FourLayerContractError:    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context    # guardian: FourLayerContractError should be handled with specific context
            return None

        entry = self.layer_caches[layer_type].get(key)

        if entry:
            # Check if expired
            if entry.is_expired():
                await self.invalidate_cache_entry(layer_type, key, "TTL expired")
                return None

            # Update last accessed
            entry.last_accessed = datetime.now()
            return entry

        return None

    async def _handle_invalidation(self, message: InvalidationMessage):
        """Handle invalidation message."""
        layer_type = message.layer_type

        # Update sync status
        self.sync_status[layer_type].pending_operations += 1

        try:
            if message.event_type == InvalidationEvent.DATA_UPDATE:
                # Handle cascade updates
                for target_layer in message.cascade_to_layers:
                    if target_layer != layer_type:
                        # Check if entry exists in target layer
                        existing_entry = self.layer_caches[target_layer].get(message.affected_keys[0])
                        if existing_entry:
                            # Invalidate dependent entry
                            await self.invalidate_cache_entry(
                                target_layer,
                                message.affected_keys[0],
                                f"Cascade invalidation from {layer_type.value}",
                            )

            elif message.event_type == InvalidationEvent.VERSION_CHANGE:
                # Handle version changes
                for target_layer in message.cascade_to_layers:
                    if target_layer != layer_type:
                        # Update version in dependent layers
                        existing_entry = self.layer_caches[target_layer].get(message.affected_keys[0])
                        if existing_entry and existing_entry.version != message.version:
                            await self.update_cache_entry(
                                target_layer,
                                message.affected_keys[0],
                                existing_entry.value,
                                message.version,
                                existing_entry.ttl_seconds,
                            )

            elif message.event_type == InvalidationEvent.MANUAL_INVALIDATION:
                for target_layer in message.cascade_to_layers:
                    if target_layer != layer_type:
                        if message.affected_keys[0] in self.layer_caches[target_layer]:
                            del self.layer_caches[target_layer][message.affected_keys[0]]
            # Update sync status
            self.sync_status[layer_type].status = SyncStatus.SYNCED
            self.sync_status[layer_type].last_sync = datetime.now()

        except Exception as e:
            self.sync_status[layer_type].failed_operations += 1
            self.sync_status[layer_type].status = SyncStatus.FAILED
            logger.error(f"Error handling invalidation: {e}")

            # Wave B-7: Emit cache coherence violations for drift detection
            try:
                from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
                bridge = get_sl_memory_bridge()

                # Persist coherence violation
                bridge.persist_cache_coherence_violation(
                    layer_type=layer_type.value,
                    violation_type="invalidation_error",
                    error_message=str(e),
                    affected_keys=message.affected_keys[:5],  # Limit to 5 keys
                    timestamp_utc=int(datetime.now().timestamp() * 1000),
                )
            except Exception:
                # Bridge unavailable - continue without it
                pass

        finally:
            self.sync_status[layer_type].pending_operations -= 1

    def _get_dependent_layers(self, layer_type: LayerType) -> list[LayerType]:
        """Get dependent layers for cascade invalidation."""
        dependencies = {
            LayerType.REDIS_EXACT_MATCH: [LayerType.SEMANTIC_CACHE],
            LayerType.SEMANTIC_CACHE: [LayerType.RAG_RETRIEVAL],
            LayerType.RAG_RETRIEVAL: [LayerType.AGENTIC_ACTION],
            LayerType.AGENTIC_ACTION: [],
        }
        return dependencies.get(layer_type, [])

    def get_coherence_status(self) -> dict[str, Any]:
        """Get overall coherence status."""
        return {
            "layer_status": {layer.value: status.__dict__ for layer, status in self.sync_status.items()},
            "cache_sizes": {layer.value: len(cache) for layer, cache in self.layer_caches.items()},
            "lock_info": self.lock_manager.get_lock_info(),
            "inconsistency_report": self.consistency_monitor.get_inconsistency_report(),
            "version_stats": {
                "total_versions": len(self.version_manager.versions),
                "version_history_size": sum(
                    len(history) for history in self.version_manager.version_history.values()
                ),
            },
        }

    async def cleanup_expired_entries(self):
        """Clean up expired entries."""
        expired_count = 0

        for layer_type, cache in self.layer_caches.items():
            expired_keys = []

            for key, entry in cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                await self.invalidate_cache_entry(layer_type, key, "TTL expired")
                expired_count += 1

        logger.info(f"Cleaned up {expired_count} expired entries")
        return expired_count
