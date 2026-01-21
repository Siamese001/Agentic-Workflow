"""Resource Manager - Handles file handles, connections, and resource cleanup.

This module provides centralized resource management with automatic cleanup,
connection pooling, and prevention of resource leaks.
"""

import asyncio
import logging
import shutil
import weakref
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
import aiofiles
import aiofiles.os
from pathlib import Path

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
    cleanup_callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResourceManager:
    """Manages system resources with automatic cleanup."""

    def __init__(self, name: str = "default", max_resources: int = 1000):
        """Initialize the resource manager.

        Args:
            name: Manager name for logging
            max_resources: Maximum number of resources to track
        """
        self.name = name
        self.max_resources = max_resources

        # Resource tracking
        self._resources: Dict[str, ResourceInfo] = {}
        self._resource_counter = 0
        self._lock = threading.Lock()

        # Connection pools
        self._connection_pools: Dict[str, Any] = {}

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        logger.debug(f"Initialized ResourceManager: {name}")

    async def start(self) -> None:
        """Start the resource manager."""
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

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Clean up all resources
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
        cleanup_callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
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
                # Force cleanup of oldest unused resources
                self._force_cleanup()

            resource_id = self.generate_resource_id()

            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                created_at=time.time(),
                last_used=time.time(),
                cleanup_callback=cleanup_callback,
                metadata=metadata or {}
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

            # Call cleanup callback
            if resource_info.cleanup_callback:
                try:
                    if asyncio.iscoroutinefunction(resource_info.cleanup_callback):
                        # Schedule async cleanup
                        asyncio.create_task(resource_info.cleanup_callback())
                    else:
                        resource_info.cleanup_callback()
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
        cutoff_time = time.time() - 300  # 5 minutes
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
                await asyncio.sleep(60)  # Cleanup every minute

                # Clean up resources unused for 10 minutes
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
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    @contextmanager
    def managed_file(self, file_path: Union[str, Path], mode: str = 'r'):
        """Context manager for managed file operations.

        Args:
            file_path: Path to the file
            mode: File mode

        Yields:
            File handle
        """
        resource_id = self.register_resource(
            ResourceType.FILE_HANDLE,
            metadata={"path": str(file_path), "mode": mode}
        )

        try:
            with open(file_path, mode) as f:
                self.update_last_used(resource_id)
                yield f
        finally:
            self.unregister_resource(resource_id)

    @asynccontextmanager
    async def managed_async_file(self, file_path: Union[str, Path], mode: str = 'r'):
        """Context manager for managed async file operations.

        Args:
            file_path: Path to the file
            mode: File mode

        Yields:
            Async file handle
        """
        resource_id = self.register_resource(
            ResourceType.FILE_HANDLE,
            metadata={"path": str(file_path), "mode": mode}
        )

        try:
            async with aiofiles.open(file_path, mode) as f:
                self.update_last_used(resource_id)
                yield f
        finally:
            self.unregister_resource(resource_id)

    @asynccontextmanager
    async def atomic_write(self, file_path: Union[str, Path], temp_suffix: str = ".tmp"):
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
            metadata={"temp_path": str(temp_path), "target_path": str(file_path)}
        )

        try:
            yield temp_path

            # Verify file exists and is not empty
            if not temp_path.exists():
                raise IOError(f"Temporary file was not created: {temp_path}")

            if temp_path.stat().st_size == 0 and file_path.exists():
                raise IOError("Refusing to overwrite with empty file")

            # Atomic move
            await aiofiles.os.replace(str(temp_path), str(file_path))

            logger.debug(f"Atomically wrote {file_path}")

        except Exception:
            # Cleanup on failure
            try:
                await aiofiles.os.remove(temp_path)
            except Exception:
                pass
            raise
        finally:
            self.unregister_resource(resource_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get resource manager statistics.

        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = {
                "name": self.name,
                "total_resources": len(self._resources),
                "max_resources": self.max_resources,
                "resources_by_type": {}
            }

            for resource_info in self._resources.values():
                resource_type = resource_info.resource_type.value
                stats["resources_by_type"][resource_type] = (
                    stats["resources_by_type"].get(resource_type, 0) + 1
                )

            return stats


# Global resource manager registry
_managers: Dict[str, ResourceManager] = {}
_manager_lock = threading.Lock()


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
            # Note: Caller should call start() when ready
            _managers[name] = manager
        return _managers[name]


async def shutdown_all_managers() -> None:
    """Shutdown all resource managers."""
    with _manager_lock:
        for manager in _managers.values():
            await manager.stop()
        _managers.clear()


# Connection pool for LLM clients
class ConnectionPool:
    """Simple connection pool for reusing connections."""

    def __init__(self, name: str, max_connections: int = 10):
        """Initialize the connection pool.

        Args:
            name: Pool name
            max_connections: Maximum connections
        """
        self.name = name
        self.max_connections = max_connections
        self._connections: List[Any] = []
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
                # Try to get from pool
                connection = self._available.get_nowait()
                return connection
            except asyncio.QueueEmpty:
                # Create new connection
                return await create_func()

    async def return_connection(self, connection: Any) -> None:
        """Return a connection to the pool.

        Args:
            connection: Connection to return
        """
        try:
            self._available.put_nowait(connection)
        except asyncio.QueueFull:
            # Pool is full, discard connection
            pass

    async def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._available.empty():
            try:
                connection = self._available.get_nowait()
                if hasattr(connection, 'close'):
                    if asyncio.iscoroutinefunction(connection.close):
                        await connection.close()
                    else:
                        connection.close()
            except asyncio.QueueEmpty:
                break
