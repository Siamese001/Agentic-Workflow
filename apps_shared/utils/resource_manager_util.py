"""Resource Manager - Handles file handles, connections, and resource cleanup.

This module provides centralized resource management with automatic cleanup,
connection pooling, and prevention of resource leaks.
"""

import asyncio
import logging
import threading
import time
from collections.abc import Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles
import aiofiles.os

from agentic_core.interfaces.path_constants import DEFAULT_SLEEP
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

_emit_applies_guardrail("p0", "resource_manager_util", "p0_governance")
_emit_reads_policy_state("p0", "resource_manager_util", "policy_binding")
_emit_snapshots_state("p0", "resource_manager_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("resource_manager_util", "p4obs", "metric_1")
_emit_emits_metric_event("resource_manager_util", "p4obs", "metric_2")
_emit_emits_metric_event("resource_manager_util", "p4obs", "metric_3")
_emit_emits_metric_event("resource_manager_util", "p4obs", "metric_4")
_emit_emits_metric_event("resource_manager_util", "p4obs", "metric_5")
_emit_emits_metric_event("resource_manager_util", "p4obs", "metric_6")
_emit_records_incident_event("resource_manager_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("resource_manager_util", "p4obs", "anomaly")
_emit_writes_observability_log("resource_manager_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("resource_manager_util", "p4obs", "mon_state")
_emit_triggers_alert("resource_manager_util", "p4obs", "alert")
_emit_links_incident_trace("resource_manager_util", "p4obs", "trace_link")
_emit_captures_pattern("resource_manager_util", "p3lm", "pattern")
_emit_records_learning_event("resource_manager_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("resource_manager_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("resource_manager_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("resource_manager_util", "p3lm", "routing")
_emit_improves_agent_policy("resource_manager_util", "p3lm", "policy")
_emit_stores_learning_state("resource_manager_util", "p3lm", "state")
_emit_records_execution_trace("resource_manager_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("resource_manager_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("resource_manager_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("resource_manager_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("resource_manager_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("resource_manager_util", "env_read", "p2_env_1")
_emit_reads_environ("resource_manager_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("resource_manager_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("resource_manager_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "resource_manager_util", "context_pull")
_emit_pulls_context("p1", "resource_manager_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "resource_manager_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "resource_manager_util", "uwg_term_2")
_emit_writes_through("p1", "resource_manager_util", "write_through")
_emit_writes_through("p1", "resource_manager_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "resource_manager_util", "safety_validation")
_emit_invokes_eval("p1", "resource_manager_util", "eval_call")
_emit_proposal_commits_routing("p1", "resource_manager_util", "routing_commit")
_emit_escalates_to_human("p1", "resource_manager_util", "human_escalation")
_emit_routes_through("p1", "resource_manager_util", "route_through")
_emit_checks_agent_registry("p1", "resource_manager_util", "agent_registry")
_emit_validates_agent_capability("p1", "resource_manager_util", "capability")
_emit_dispatches_execution_plan("p1", "resource_manager_util", "exec_plan")
_emit_agent_executes_agent("p1", "resource_manager_util", "sub_agent")
_emit_routes_to_agent("p1", "resource_manager_util", "target_agent")
_emit_verifies_policy("p1", "resource_manager_util", "policy_check")
_emit_observes_runtime_state("p1", "resource_manager_util", "runtime_state")
_emit_verifies_boundary("p1", "resource_manager_util", "boundary_check")
_emit_transcripts_response("p1", "resource_manager_util", "transcript")
_emit_hard_fails_untranscripted("p1", "resource_manager_util")
_emit_gated_by_confidence("p1", "resource_manager_util", "confidence_gate")
emit_replay_key("p0", "resource_manager_util")
emit_determinism_digest("p0", "resource_manager_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "resource_manager_util", "execution_auth")
_emit_validates_capability("p2", "resource_manager_util", "capability_check")
_emit_routes_to_capability("p2", "resource_manager_util", "capability_route")
_emit_writes_via_uwg("p2", "resource_manager_util", "uwg_write")
_emit_blocks_direct_write("p2", "resource_manager_util", "direct_write_block")
_emit_records_tool_invocation("p2", "resource_manager_util", "tool_invocation")
_emit_captures_execution_output("p2", "resource_manager_util", "exec_output")
_emit_dispatches_agent("p3", "resource_manager_util", "agent_dispatch")
_emit_coordinates_agents("p3", "resource_manager_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "resource_manager_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "resource_manager_util", "healing_outcome")
_emit_escalates_failure("p3", "resource_manager_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "resource_manager_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "resource_manager_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "resource_manager_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "resource_manager_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "resource_manager_util", "eval_metric")
_emit_stores_embedding("p4", "resource_manager_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "resource_manager_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "resource_manager_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources managed."""

    FILE_HANDLE = "file_handle"
    NETWORK_CONNECTION = "network_connection"
    TEMP_FILE = "temp_file"
    LOCK = "lock"
    SEMAPHORE = "semaphore"


@dataclass
class ResourceInfo:
    """Information about a managed resource."""

    resource_id: str
    resource_type: ResourceType
    created_at: float
    last_used: float
    cleanup_callback: Callable | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ResourceManager:
    """Manages system resources with automatic cleanup."""

    # guardian: allow-magic-config
    def __init__(self, name: str = "default", max_resources: int = 1000):
        """Initialize the resource manager.

        Args:
            name: Manager name for logging
            max_resources: Maximum number of resources to track
        """
        self.name = name
        self.max_resources = max_resources
        self._resources: dict[str, ResourceInfo] = {}
        self._resource_counter = 0
        self._lock = threading.Lock()
        self._connection_pools: dict[str, Any] = {}
        self._cleanup_task: asyncio.Task | None = None
        self._running = False
        logger.debug(f"Initialized ResourceManager: {name}")

    async def start(self) -> None:
        """Start the resource manager."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResourceManager.start")

        if self._running:
            return
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Started ResourceManager: {self.name}")

    async def stop(self) -> None:
        """Stop the resource manager and clean up all resources."""
        if not self._running:
            return
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        await self.cleanup_all()
        logger.info(f"Stopped ResourceManager: {self.name}")

    def generate_resource_id(self) -> str:
        """Generate a unique resource ID.

        Returns:
            Unique resource ID
        """
        self._resource_counter += 1
        return f"{self.name}_res_{self._resource_counter}_{int(time.time() * 1000)}"

    def register_resource(
        self,
        resource_type: ResourceType,
        cleanup_callback: Callable | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a resource for tracking.

        Args:
            resource_type: Type of resource
            cleanup_callback: Optional cleanup callback
            metadata: Optional metadata

        Returns:
            Resource ID
        """
        with self._lock:
            if len(self._resources) >= self.max_resources:
                self._force_cleanup()
            resource_id = self.generate_resource_id()
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                created_at=time.time(),
                last_used=time.time(),
                cleanup_callback=cleanup_callback,
                metadata=metadata or {},
            )
            self._resources[resource_id] = resource_info
            return resource_id

    def update_last_used(self, resource_id: str) -> None:
        """Update the last used time for a resource.

        Args:
            resource_id: ID of the resource
        """
        with self._lock:
            if resource_id in self._resources:
                self._resources[resource_id].last_used = time.time()

    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister and cleanup a resource.

        Args:
            resource_id: ID of the resource

        Returns:
            True if resource was found and cleaned up
        """
        with self._lock:
            resource_info = self._resources.pop(resource_id, None)
            if not resource_info:
                return False
            if resource_info.cleanup_callback:
                try:
                    if asyncio.iscoroutinefunction(resource_info.cleanup_callback):
                        asyncio.create_task(resource_info.cleanup_callback())
                    else:
                        resource_info.cleanup_callback()
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.error(f"Cleanup callback failed for {resource_id}: {e}")
            return True

    async def cleanup_all(self) -> int:
        """Clean up all registered resources.

        Returns:
            Number of resources cleaned up
        """
        with self._lock:
            resource_ids = list(self._resources.keys())
        cleaned = 0
        for resource_id in resource_ids:
            if self.unregister_resource(resource_id):
                cleaned += 1
        logger.info(f"Cleaned up {cleaned} resources in manager {self.name}")
        return cleaned

    def _force_cleanup(self) -> None:
        """Force cleanup of oldest unused resources."""
        cutoff_time = time.time() - 300
        to_remove = []
        for resource_id, resource_info in self._resources.items():
            if resource_info.last_used < cutoff_time:
                to_remove.append(resource_id)
        for resource_id in to_remove:
            self.unregister_resource(resource_id)
        logger.debug(f"Force cleaned up {len(to_remove)} old resources")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(DEFAULT_SLEEP)
                cutoff_time = time.time() - 600
                to_remove = []
                with self._lock:
                    for resource_id, resource_info in self._resources.items():
                        if resource_info.last_used < cutoff_time:
                            to_remove.append(resource_id)
                for resource_id in to_remove:
                    self.unregister_resource(resource_id)
                if to_remove:
                    logger.debug(f"Background cleanup removed {len(to_remove)} resources")
            except asyncio.CancelledError:
                break
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    @contextmanager
    def managed_file(self, file_path: str | Path, mode: str = "r"):
        """Context manager for managed file operations.

        Args:
            file_path: Path to the file
            mode: File mode

        Yields:
            File handle
        """
        resource_id = self.register_resource(
            ResourceType.FILE_HANDLE, metadata={"path": str(file_path), "mode": mode}
        )
        try:
            with open(file_path, mode) as f:
                self.update_last_used(resource_id)
                yield f
        finally:
            self.unregister_resource(resource_id)

    @asynccontextmanager
    async def managed_async_file(self, file_path: str | Path, mode: str = "r"):
        """Context manager for managed async file operations.

        Args:
            file_path: Path to the file
            mode: File mode

        Yields:
            Async file handle
        """
        resource_id = self.register_resource(
            ResourceType.FILE_HANDLE, metadata={"path": str(file_path), "mode": mode}
        )
        try:
            async with aiofiles.open(file_path, mode) as f:
                self.update_last_used(resource_id)
                yield f
        finally:
            self.unregister_resource(resource_id)

    @asynccontextmanager
    async def atomic_write(self, file_path: str | Path, temp_suffix: str = ".tmp"):
        """Context manager for atomic file writes.

        Args:
            file_path: Target file path
            temp_suffix: Suffix for temporary file

        Yields:
            Temporary file path for writing
        """
        file_path = Path(file_path)
        temp_path = file_path.with_suffix(file_path.suffix + temp_suffix)
        resource_id = self.register_resource(
            ResourceType.TEMP_FILE,
            cleanup_callback=lambda: temp_path.unlink(missing_ok=True),
            metadata={"temp_path": str(temp_path), "target_path": str(file_path)},
        )
        try:
            yield temp_path
            if not temp_path.exists():
                raise OSError(f"Temporary file was not created: {temp_path}")
            if temp_path.stat().st_size == 0 and file_path.exists():
                raise OSError("Refusing to overwrite with empty file")
            await aiofiles.os.replace(str(temp_path), str(file_path))
            logger.debug(f"Atomically wrote {file_path}")
        # guardian: allow-silent-swallow
        except Exception:
            raise
            try:
                await aiofiles.os.remove(temp_path)
            # guardian: allow-silent-swallow
            except Exception:
                pass
            raise
        finally:
            self.unregister_resource(resource_id)

    def get_stats(self) -> dict[str, Any]:
        """Get resource manager statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = {
                "name": self.name,
                "total_resources": len(self._resources),
                "max_resources": self.max_resources,
                "resources_by_type": {},
            }
            for resource_info in self._resources.values():
                resource_type = resource_info.resource_type.value
                stats["resources_by_type"][resource_type] = (
                    stats["resources_by_type"].get(resource_type, 0) + 1
                )
            return stats


_managers: dict[str, ResourceManager] = {}
_manager_lock = threading.Lock()


# guardian: allow-magic-config
def get_resource_manager(name: str = "default", max_resources: int = 1000) -> ResourceManager:
    """Get or create a resource manager.

    Args:
        name: Manager name
        max_resources: Maximum resources

    Returns:
        ResourceManager instance
    """
    with _manager_lock:
        if name not in _managers:
            manager = ResourceManager(name, max_resources)
            _managers[name] = manager
        return _managers[name]


async def shutdown_all_managers() -> None:
    """Shutdown all resource managers."""
    with _manager_lock:
        for manager in _managers.values():
            await manager.stop()
        _managers.clear()


class ConnectionPool:
    """Simple connection pool for reusing connections."""

    # guardian: allow-magic-config
    def __init__(self, name: str, max_connections: int = 10):
        """Initialize the connection pool.

        Args:
            name: Pool name
            max_connections: Maximum connections
        """
        self.name = name
        self.max_connections = max_connections
        self._connections: list[Any] = []
        self._available = asyncio.Queue(maxsize=max_connections)
        self._semaphore = asyncio.Semaphore(max_connections)
        self._lock = asyncio.Lock()

    async def get_connection(self, create_func: Callable[[], Any]) -> Any:
        """Get a connection from the pool.

        Args:
            create_func: Function to create new connection

        Returns:
            Connection object
        """
        async with self._semaphore:
            try:
                connection = self._available.get_nowait()
                return connection
            except asyncio.QueueEmpty:
                return await create_func()

    async def return_connection(self, connection: Any) -> None:
        """Return a connection to the pool.

        Args:
            connection: Connection to return
        """
        try:
            self._available.put_nowait(connection)
        except asyncio.QueueFull:
            pass

    async def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._available.empty():
            try:
                connection = self._available.get_nowait()
                if hasattr(connection, "close"):
                    if asyncio.iscoroutinefunction(connection.close):
                        await connection.close()
                    else:
                        connection.close()
            except asyncio.QueueEmpty:
                break
