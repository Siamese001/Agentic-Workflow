"""Opportunity 4: Distributed State Management & Recovery

Implements multi-region state replication, automatic failover, state snapshots,
and disaster recovery for the 4-layer retrieval pattern.
"""

import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .implementation_plan import LayerType

logger = logging.getLogger(__name__)


class _ChecksumTrackingDict(dict):
    """Dictionary that keeps parent snapshot checksum in sync on mutations."""

    def __init__(self, initial: dict[str, Any], owner: "StateSnapshot"):
        super().__init__(initial)
        self._owner = owner

    def _refresh(self):
        self._owner.checksum = self._owner._calculate_checksum()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._refresh()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._refresh()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._refresh()

    def clear(self):
        super().clear()
        self._refresh()


class Region(Enum):
    """Geographic regions for distributed deployment."""

    US_EAST = "us_east"
    US_WEST = "us_west"
    EUROPE = "europe"
    ASIA = "asia"


class StateType(Enum):
    """Types of state to manage."""

    CACHE_STATE = "cache_state"
    CONFIGURATION_STATE = "configuration_state"
    USER_SESSION_STATE = "user_session_state"
    SYSTEM_HEALTH_STATE = "system_health_state"
    PERFORMANCE_STATE = "performance_state"


class RecoveryStatus(Enum):
    """Recovery status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    RECOVERING = "recovering"
    FAILED = "failed"


@dataclass
class StateSnapshot:
    """State snapshot for recovery."""

    snapshot_id: str
    state_type: StateType
    layer_type: LayerType
    region: Region
    timestamp: datetime
    data: dict[str, Any]
    checksum: str = ""
    version: str = "v1.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.data, _ChecksumTrackingDict):
            self.data = _ChecksumTrackingDict(self.data, self)
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for integrity verification."""
        import hashlib

        content = f"{self.snapshot_id}:{self.state_type}:{self.layer_type}:{self.version}:{json.dumps(dict(self.data), sort_keys=True, default=str)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify snapshot integrity."""
        return self.checksum == self._calculate_checksum()


@dataclass
class ReplicationStatus:
    """Replication status across regions."""

    state_type: StateType
    primary_region: Region
    replica_regions: list[Region]
    last_replication: datetime
    replication_lag_seconds: float
    success_rate: float
    total_replications: int
    failed_replications: int


@dataclass
class HealthCheckResult:
    """Health check result."""

    component_id: str
    region: Region
    layer_type: LayerType
    status: RecoveryStatus
    timestamp: datetime
    response_time_ms: float
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class StateStorage(ABC):
    """Abstract base class for state storage."""

    @abstractmethod
    async def store_state(self, snapshot: StateSnapshot) -> bool:
        """Store state snapshot."""
        pass

    @abstractmethod
    async def retrieve_state(self, snapshot_id: str) -> StateSnapshot | None:
        """Retrieve state snapshot."""
        pass

    @abstractmethod
    async def list_snapshots(
        self,
        state_type: StateType | None = None,
        layer_type: LayerType | None = None,
        since: datetime | None = None,
    ) -> list[StateSnapshot]:
        """List state snapshots."""
        pass

    @abstractmethod
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete state snapshot."""
        pass


class InMemoryStateStorage(StateStorage):
    """In-memory state storage implementation."""

    def __init__(self):
        self.snapshots: dict[str, StateSnapshot] = {}
        self._lock = asyncio.Lock()

    async def store_state(self, snapshot: StateSnapshot) -> bool:
        """Store state snapshot."""
        async with self._lock:
            self.snapshots[snapshot.snapshot_id] = snapshot
            logger.info(f"Stored snapshot {snapshot.snapshot_id} in memory")
            return True

    async def retrieve_state(self, snapshot_id: str) -> StateSnapshot | None:
        """Retrieve state snapshot."""
        async with self._lock:
            return self.snapshots.get(snapshot_id)

    async def list_snapshots(
        self,
        state_type: StateType | None = None,
        layer_type: LayerType | None = None,
        since: datetime | None = None,
    ) -> list[StateSnapshot]:
        """List state snapshots."""
        async with self._lock:
            snapshots = list(self.snapshots.values())

            if state_type:
                snapshots = [s for s in snapshots if s.state_type == state_type]

            if layer_type:
                snapshots = [s for s in snapshots if s.layer_type == layer_type]

            if since:
                snapshots = [s for s in snapshots if s.timestamp >= since]

            return sorted(snapshots, key=lambda s: s.timestamp, reverse=True)

    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete state snapshot."""
        async with self._lock:
            if snapshot_id in self.snapshots:
                del self.snapshots[snapshot_id]
                logger.info(f"Deleted snapshot {snapshot_id} from memory")
                return True
            return False


class MultiRegionReplicator:
    """Manages multi-region state replication."""

    def __init__(self, primary_region: Region, replica_regions: list[Region]):
        self.primary_region = primary_region
        self.replica_regions = replica_regions
        self.storage_backends: dict[Region, StateStorage] = {}
        self.replication_status: dict[StateType, ReplicationStatus] = {}
        self.replication_queue: deque = deque(maxlen=1000)
        self._replication_task = None
        self._lock = asyncio.Lock()

    def add_storage_backend(self, region: Region, storage: StateStorage):
        """Add storage backend for region."""
        self.storage_backends[region] = storage
        logger.info(f"Added storage backend for {region}")

    async def start_replication(self):
        """Start replication process."""
        self._replication_task = asyncio.create_task(self._replication_worker())
        logger.info("Started multi-region replication")

    async def stop_replication(self):
        """Stop replication process."""
        if self._replication_task:
            self._replication_task.cancel()
        logger.info("Stopped multi-region replication")

    async def store_state(self, snapshot: StateSnapshot) -> bool:
        """Store state in primary region and queue for replication."""
        # Store in primary region
        primary_storage = self.storage_backends.get(self.primary_region)
        if not primary_storage:
            logger.error(f"No storage backend for primary region {self.primary_region}")
            return False

        success = await primary_storage.store_state(snapshot)
        if success:
            # Queue for replication
            self.replication_queue.append(snapshot)
            logger.info(f"Queued snapshot {snapshot.snapshot_id} for replication")

        return success

    async def retrieve_state(
        self, snapshot_id: str, preferred_region: Region | None = None,
    ) -> StateSnapshot | None:
        """Retrieve state snapshot from preferred region or primary."""
        regions_to_try = [preferred_region] if preferred_region else []
        regions_to_try.extend([self.primary_region] + self.replica_regions)

        for region in regions_to_try:
            if region in self.storage_backends:
                storage = self.storage_backends[region]
                snapshot = await storage.retrieve_state(snapshot_id)
                if snapshot and snapshot.verify_integrity():
                    logger.info(f"Retrieved snapshot {snapshot_id} from {region}")
                    return snapshot

        return None

    async def _replication_worker(self):
        """Worker process for replicating snapshots."""
        while True:
            try:
                if self.replication_queue:
                    snapshot = self.replication_queue.popleft()
                    await self._replicate_snapshot(snapshot)
                else:
                    await asyncio.sleep(1)  # Wait for new snapshots
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in replication worker: {e}")
                await asyncio.sleep(5)

    async def _replicate_snapshot(self, snapshot: StateSnapshot):
        """Replicate snapshot to all replica regions."""
        start_time = time.time()
        success_count = 0

        for region in self.replica_regions:
            if region in self.storage_backends:
                storage = self.storage_backends[region]

                try:
                    # Create region-specific snapshot
                    replica_snapshot = StateSnapshot(
                        snapshot_id=f"{snapshot.snapshot_id}_{region}",
                        state_type=snapshot.state_type,
                        layer_type=snapshot.layer_type,
                        region=region,
                        timestamp=snapshot.timestamp,
                        data=snapshot.data.copy(),
                        checksum="",
                        version=snapshot.version,
                        metadata=snapshot.metadata.copy(),
                    )

                    success = await storage.store_state(replica_snapshot)
                    if success:
                        success_count += 1
                        logger.debug(f"Replicated snapshot to {region}")
                    else:
                        logger.warning(f"Failed to replicate snapshot to {region}")

                except Exception as e:
                    logger.error(f"Error replicating to {region}: {e}")

        # Update replication status
        replication_time = (time.time() - start_time) * 1000
        total_regions = len(self.replica_regions)

        if snapshot.state_type not in self.replication_status:
            self.replication_status[snapshot.state_type] = ReplicationStatus(
                state_type=snapshot.state_type,
                primary_region=self.primary_region,
                replica_regions=self.replica_regions.copy(),
                last_replication=datetime.now(),
                replication_lag_seconds=replication_time / 1000,
                success_rate=success_count / total_regions,
                total_replications=1,
                failed_replications=total_regions - success_count,
            )
        else:
            status = self.replication_status[snapshot.state_type]
            status.last_replication = datetime.now()
            status.replication_lag_seconds = replication_time / 1000
            status.total_replications += 1
            status.failed_replications += total_regions - success_count
            status.success_rate = (
                status.total_replications - status.failed_replications
            ) / status.total_replications

        logger.info(
            f"Replicated snapshot to {success_count}/{total_regions} regions in {replication_time:.2f}ms",
        )

    def get_replication_status(self) -> dict[str, Any]:
        """Get replication status."""
        return {
            "primary_region": self.primary_region.value,
            "replica_regions": [r.value for r in self.replica_regions],
            "queue_size": len(self.replication_queue),
            "replication_status": {
                state_type.value: status.__dict__ for state_type, status in self.replication_status.items()
            },
            "storage_backends": list(self.storage_backends.keys()),
        }


class HealthChecker:
    """Health checking for distributed components."""

    def __init__(self, check_interval_seconds: int = 30):
        self.check_interval = check_interval_seconds
        self.health_status: dict[str, HealthCheckResult] = {}
        self.component_registry: dict[str, dict[str, Any]] = {}
        self._check_task = None
        self._lock = asyncio.Lock()

    def register_component(
        self,
        component_id: str,
        region: Region,
        layer_type: LayerType,
        endpoint: str,
        health_check_path: str = "/health",
    ):
        """Register component for health checking."""
        self.component_registry[component_id] = {
            "region": region,
            "layer_type": layer_type,
            "endpoint": endpoint,
            "health_check_path": health_check_path,
            "registered_at": datetime.now(),
        }
        logger.info(f"Registered component {component_id} for health checking")

    async def start_health_checks(self):
        """Start health checking."""
        self._check_task = asyncio.create_task(self._health_check_worker())
        logger.info("Started distributed health checking")

    async def stop_health_checks(self):
        """Stop health checking."""
        if self._check_task:
            self._check_task.cancel()
        logger.info("Stopped distributed health checking")

    async def _health_check_worker(self):
        """Worker process for health checking."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check worker: {e}")
                await asyncio.sleep(5)

    async def _perform_health_checks(self):
        """Perform health checks on all registered components."""
        tasks = []

        for component_id, config in self.component_registry.items():
            task = asyncio.create_task(self._check_component_health(component_id, config))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_component_health(self, component_id: str, config: dict[str, Any]) -> HealthCheckResult:
        """Check health of individual component."""
        start_time = time.time()

        try:
            # Simulate health check - in real implementation, this would make HTTP request
            await asyncio.sleep(random.uniform(0.01, 0.1))  # Simulate network latency

            response_time = (time.time() - start_time) * 1000

            # Simulate health status based on component_id
            is_healthy = "healthy" in component_id or random.random() > 0.1

            status = RecoveryStatus.HEALTHY if is_healthy else RecoveryStatus.DEGRADED

            result = HealthCheckResult(
                component_id=component_id,
                region=config["region"],
                layer_type=config["layer_type"],
                status=status,
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"endpoint": config["endpoint"]},
            )

            async with self._lock:
                self.health_status[component_id] = result

            return result

        except Exception as e:
            result = HealthCheckResult(
                component_id=component_id,
                region=config["region"],
                layer_type=config["layer_type"],
                status=RecoveryStatus.FAILED,
                timestamp=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
            )

            async with self._lock:
                self.health_status[component_id] = result

            return result

    def get_health_summary(self) -> dict[str, Any]:
        """Get health summary."""
        status_counts = defaultdict(int)
        region_status = defaultdict(lambda: defaultdict(int))
        layer_status = defaultdict(lambda: defaultdict(int))

        for result in self.health_status.values():
            status_counts[result.status.value] += 1
            region_status[result.region.value][result.status.value] += 1
            layer_status[result.layer_type.value][result.status.value] += 1

        return {
            "total_components": len(self.health_status),
            "status_counts": dict(status_counts),
            "region_status": {k: dict(v) for k, v in region_status.items()},
            "layer_status": {k: dict(v) for k, v in layer_status.items()},
            "last_check": max(
                (r.timestamp for r in self.health_status.values()), default=datetime.now(),
            ).isoformat(),
        }

    async def get_health_summary_async(self) -> dict[str, Any]:
        """Async wrapper for health summary."""
        return self.get_health_summary()


class DisasterRecoveryManager:
    """Manages disaster recovery procedures."""

    def __init__(self, replicator: MultiRegionReplicator, health_checker: HealthChecker):
        self.replicator = replicator
        self.health_checker = health_checker
        self.recovery_procedures: dict[str, dict[str, Any]] = {}
        self.recovery_history: list[dict[str, Any]] = []
        self._recovery_task = None

    async def start_recovery_monitoring(self):
        """Start recovery monitoring."""
        self._recovery_task = asyncio.create_task(self._recovery_monitor())
        logger.info("Started disaster recovery monitoring")

    async def stop_recovery_monitoring(self):
        """Stop recovery monitoring."""
        if self._recovery_task:
            self._recovery_task.cancel()
        logger.info("Stopped disaster recovery monitoring")

    async def _recovery_monitor(self):
        """Monitor for recovery needs."""
        while True:
            try:
                await self._check_recovery_needs()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in recovery monitor: {e}")
                await asyncio.sleep(10)

    async def _check_recovery_needs(self):
        """Check if recovery procedures need to be triggered."""
        # Check for region failures
        for region in Region:
            region_components = [c for c in self.health_checker.health_status.values() if c.region == region]

            if region_components:
                failed_count = sum(1 for c in region_components if c.status == RecoveryStatus.FAILED)
                failure_rate = failed_count / len(region_components)

                if failure_rate > 0.5:  # More than 50% components failed
                    await self._trigger_region_recovery(region, failure_rate)

        # Check for layer failures
        for layer in LayerType:
            layer_components = [
                c for c in self.health_checker.health_status.values() if c.layer_type == layer
            ]

            if layer_components:
                failed_count = sum(1 for c in layer_components if c.status == RecoveryStatus.FAILED)
                failure_rate = failed_count / len(layer_components)

                if failure_rate > 0.3:  # More than 30% components failed
                    await self._trigger_layer_recovery(layer, failure_rate)

    async def _trigger_region_recovery(self, region: Region, failure_rate: float):
        """Trigger recovery for a region."""
        logger.warning(f"Triggering recovery for region {region} (failure rate: {failure_rate:.2%})")

        recovery_id = f"region_recovery_{int(time.time())}"

        try:
            # Promote replica region to primary
            if region == self.replicator.primary_region:
                await self._promote_replica_to_primary()

            # Redirect traffic to healthy regions
            await self._redirect_traffic(region)

            # Record recovery
            recovery_record = {
                "recovery_id": recovery_id,
                "type": "region_recovery",
                "target": region.value,
                "failure_rate": failure_rate,
                "timestamp": datetime.now(),
                "status": "completed",
                "actions": ["promoted_replica", "redirected_traffic"],
            }

            self.recovery_history.append(recovery_record)
            logger.info(f"Completed region recovery for {region}")

        except Exception as e:
            recovery_record = {
                "recovery_id": recovery_id,
                "type": "region_recovery",
                "target": region.value,
                "failure_rate": failure_rate,
                "timestamp": datetime.now(),
                "status": "failed",
                "error": str(e),
            }

            self.recovery_history.append(recovery_record)
            logger.error(f"Failed region recovery for {region}: {e}")

    async def _trigger_layer_recovery(self, layer: LayerType, failure_rate: float):
        """Trigger recovery for a layer."""
        logger.warning(f"Triggering recovery for layer {layer} (failure rate: {failure_rate:.2%})")

        recovery_id = f"layer_recovery_{int(time.time())}"

        try:
            # Restore layer state from latest snapshot
            await self._restore_layer_state(layer)

            # Restart failed components
            await self._restart_layer_components(layer)

            # Record recovery
            recovery_record = {
                "recovery_id": recovery_id,
                "type": "layer_recovery",
                "target": layer.value,
                "failure_rate": failure_rate,
                "timestamp": datetime.now(),
                "status": "completed",
                "actions": ["restored_state", "restarted_components"],
            }

            self.recovery_history.append(recovery_record)
            logger.info(f"Completed layer recovery for {layer}")

        except Exception as e:
            recovery_record = {
                "recovery_id": recovery_id,
                "type": "layer_recovery",
                "target": layer.value,
                "failure_rate": failure_rate,
                "timestamp": datetime.now(),
                "status": "failed",
                "error": str(e),
            }

            self.recovery_history.append(recovery_record)
            logger.error(f"Failed layer recovery for {layer}: {e}")

    async def _promote_replica_to_primary(self):
        """Promote a replica region to primary."""
        # Select healthiest replica region
        replica_regions = self.replicator.replica_regions
        healthiest_region = None
        best_health_score = 0.0

        for region in replica_regions:
            region_components = [c for c in self.health_checker.health_status.values() if c.region == region]
            if region_components:
                healthy_count = sum(1 for c in region_components if c.status == RecoveryStatus.HEALTHY)
                health_score = healthy_count / len(region_components)

                if health_score > best_health_score:
                    best_health_score = health_score
                    healthiest_region = region

        if healthiest_region:
            old_primary = self.replicator.primary_region
            self.replicator.primary_region = healthiest_region
            self.replicator.replica_regions.remove(healthiest_region)
            self.replicator.replica_regions.append(old_primary)

            logger.info(f"Promoted {healthiest_region} to primary region (was {old_primary})")
        else:
            raise Exception("No healthy replica region available for promotion")

    async def _redirect_traffic(self, failed_region: Region):
        """Redirect traffic away from failed region."""
        # In a real implementation, this would update load balancer configurations
        logger.info(f"Redirecting traffic away from failed region {failed_region}")

    async def _restore_layer_state(self, layer: LayerType):
        """Restore layer state from latest snapshot."""
        # Get latest snapshot for layer
        storage = self.replicator.storage_backends.get(self.replicator.primary_region)
        if not storage:
            raise Exception("No storage backend available for state restoration")

        snapshots = await storage.list_snapshots(layer_type=layer)
        if not snapshots:
            raise Exception(f"No snapshots available for layer {layer}")

        latest_snapshot = snapshots[0]
        logger.info(f"Restoring layer {layer} from snapshot {latest_snapshot.snapshot_id}")

        # In a real implementation, this would restore the actual layer state
        # For now, we just log the action
        await asyncio.sleep(1)  # Simulate restoration time

    async def _restart_layer_components(self, layer: LayerType):
        """Restart failed components for a layer."""
        failed_components = [
            c
            for c in self.health_checker.health_status.values()
            if c.layer_type == layer and c.status == RecoveryStatus.FAILED
        ]

        for component in failed_components:
            logger.info(f"Restarting component {component.component_id}")
            # In a real implementation, this would restart the actual component
            await asyncio.sleep(0.5)  # Simulate restart time

    async def create_backup(self, state_type: StateType, layer_type: LayerType, data: dict[str, Any]) -> str:
        """Create backup snapshot."""
        snapshot_id = f"backup_{state_type.value}_{layer_type.value}_{int(time.time())}"

        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            state_type=state_type,
            layer_type=layer_type,
            region=self.replicator.primary_region,
            timestamp=datetime.now(),
            data=data,
            checksum="",
            metadata={"backup_type": "manual", "created_by": "disaster_recovery_manager"},
        )

        success = await self.replicator.store_state(snapshot)
        if success:
            logger.info(f"Created backup snapshot {snapshot_id}")
            return snapshot_id
        else:
            raise Exception(f"Failed to create backup snapshot {snapshot_id}")

    async def restore_from_backup(self, snapshot_id: str) -> bool:
        """Restore from backup snapshot."""
        snapshot = await self.replicator.retrieve_state(snapshot_id)
        if not snapshot:
            raise Exception(f"Backup snapshot {snapshot_id} not found")

        if not snapshot.verify_integrity():
            raise Exception(f"Backup snapshot {snapshot_id} integrity check failed")

        logger.info(f"Restoring from backup snapshot {snapshot_id}")

        # In a real implementation, this would restore the actual state
        # For now, we just simulate the restoration
        await asyncio.sleep(2)  # Simulate restoration time

        return True

    def get_recovery_status(self) -> dict[str, Any]:
        """Get recovery status."""
        status_counts = defaultdict(int)
        region_status = defaultdict(lambda: defaultdict(int))
        layer_status = defaultdict(lambda: defaultdict(int))

        for result in self.health_checker.health_status.values():
            status_counts[result.status.value] += 1
            region_status[result.region.value][result.status.value] += 1
            layer_status[result.layer_type.value][result.status.value] += 1

        last_check = max(
            (r.timestamp for r in self.health_checker.health_status.values()), default=datetime.now(),
        ).isoformat()

        return {
            "recovery_history": self.recovery_history[-50:],  # Last 50 recovery operations
            "replication_status": self.replicator.get_replication_status(),
            "health_summary": {
                "total_components": len(self.health_checker.health_status),
                "status_counts": dict(status_counts),
                "region_status": {k: dict(v) for k, v in region_status.items()},
                "layer_status": {k: dict(v) for k, v in layer_status.items()},
                "last_check": last_check,
            },
            "registered_components": len(self.health_checker.component_registry),
        }


class DistributedStateManager:
    """Main distributed state management system."""

    def __init__(self, primary_region: Region = Region.US_EAST):
        self.primary_region = primary_region
        self.replica_regions = [Region.US_WEST, Region.EUROPE, Region.ASIA]

        # Initialize components
        self.replicator = MultiRegionReplicator(primary_region, self.replica_regions)
        self.health_checker = HealthChecker()
        self.disaster_recovery = DisasterRecoveryManager(self.replicator, self.health_checker)

        # Add storage backends
        for region in [primary_region] + self.replica_regions:
            self.replicator.add_storage_backend(region, InMemoryStateStorage())

        self._running = False

    async def start(self):
        """Start distributed state management."""
        try:
            asyncio.get_event_loop()
        except RuntimeError:    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation    # guardian: Runtime errors should be prevented with proper validation
            asyncio.set_event_loop(asyncio.new_event_loop())
        await self.replicator.start_replication()
        await self.health_checker.start_health_checks()
        await self.disaster_recovery.start_recovery_monitoring()
        self._running = True
        logger.info("Started distributed state management")

    async def stop(self):
        """Stop distributed state management."""
        await self.replicator.stop_replication()
        await self.health_checker.stop_health_checks()
        await self.disaster_recovery.stop_recovery_monitoring()
        self._running = False
        logger.info("Stopped distributed state management")

    def register_component(self, component_id: str, region: Region, layer_type: LayerType, endpoint: str):
        """Register component for state management."""
        self.health_checker.register_component(component_id, region, layer_type, endpoint)

    async def store_layer_state(self, layer_type: LayerType, state_data: dict[str, Any]) -> str:
        """Store layer state."""
        snapshot_id = f"layer_state_{layer_type.value}_{int(time.time())}"

        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            state_type=StateType.CACHE_STATE,
            layer_type=layer_type,
            region=self.primary_region,
            timestamp=datetime.now(),
            data=state_data,
            checksum="",  # Will be auto-calculated in __post_init__
        )

        success = await self.replicator.store_state(snapshot)
        if success:
            return snapshot_id
        else:
            raise Exception(f"Failed to store layer state for {layer_type}")

    async def retrieve_layer_state(
        self, layer_type: LayerType, snapshot_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve layer state."""
        if snapshot_id:
            snapshot = await self.replicator.retrieve_state(snapshot_id)
        else:
            # Get latest snapshot for layer
            storage = self.replicator.storage_backends.get(self.primary_region)
            if storage:
                snapshots = await storage.list_snapshots(
                    state_type=StateType.CACHE_STATE, layer_type=layer_type,
                )
                snapshot = snapshots[0] if snapshots else None
            else:
                snapshot = None

        return snapshot.data if snapshot and snapshot.verify_integrity() else None

    async def create_system_backup(self) -> str:
        """Create complete system backup."""
        backup_data = {}

        for layer_type in LayerType:
            layer_state = await self.retrieve_layer_state(layer_type)
            if layer_state:
                backup_data[layer_type.value] = layer_state

        return await self.disaster_recovery.create_backup(
            StateType.CONFIGURATION_STATE,
            LayerType.REDIS_EXACT_MATCH,  # Use any layer as container
            backup_data,
        )

    async def restore_system_backup(self, backup_id: str) -> bool:
        """Restore complete system from backup."""
        return await self.disaster_recovery.restore_from_backup(backup_id)

    def get_system_status(self) -> dict[str, Any]:
        """Get overall system status."""
        return {
            "running": self._running,
            "primary_region": self.primary_region.value,
            "replica_regions": [r.value for r in self.replica_regions],
            "recovery_status": self.disaster_recovery.get_recovery_status(),
        }
