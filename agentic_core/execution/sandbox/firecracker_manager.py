"""Firecracker Micro-VM Manager.

Phase 3 - Pillar 14: Execution Sandbox (Hardened Ephemeral)
Integration layer for Firecracker/E2B micro-VM system.

Firecracker provides:
- Lightweight virtualization (microseconds startup)
- Strong isolation
- Minimal attack surface
- Resource limits
"""

import logging
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VMStatus(Enum):
    """VM operational status."""
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    TERMINATED = "terminated"


class VMProvider(Enum):
    """VM provider types."""
    FIRECRACKER = "firecracker"
    E2B = "e2b"
    DOCKER = "docker"
    LOCAL = "local"


@dataclass
class VMConfig:
    """Configuration for micro-VM."""
    vm_id: str
    provider: VMProvider = VMProvider.FIRECRACKER
    cpu_count: int = 1
    memory_mb: int = 512
    disk_mb: int = 1024
    network_enabled: bool = False
    timeout_seconds: int = 300
    auto_teardown: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vm_id": self.vm_id,
            "provider": self.provider.value,
            "cpu_count": self.cpu_count,
            "memory_mb": self.memory_mb,
            "disk_mb": self.disk_mb,
            "network_enabled": self.network_enabled,
            "timeout_seconds": self.timeout_seconds,
            "auto_teardown": self.auto_teardown,
            "metadata": self.metadata,
        }


@dataclass
class VMInstance:
    """Running VM instance."""
    vm_id: str
    config: VMConfig
    status: VMStatus
    created_at: float
    process_id: Optional[int] = None
    endpoint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_running(self) -> bool:
        """Check if VM is running.
        
        Returns:
            True if running
        """
        return self.status == VMStatus.RUNNING
    
    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Check if VM has exceeded timeout.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            True if expired
        """
        current_time = current_time or time.time()
        elapsed = current_time - self.created_at
        return elapsed > self.config.timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vm_id": self.vm_id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "created_at": self.created_at,
            "process_id": self.process_id,
            "endpoint": self.endpoint,
            "metadata": self.metadata,
        }


class FirecrackerManager:
    """Manager for Firecracker micro-VMs.
    
    Provides:
    - VM lifecycle management
    - Resource isolation
    - Network isolation
    - Automatic cleanup
    
    Simplified implementation for Phase 3.
    Production should use full Firecracker/E2B SDK.
    """
    
    def __init__(
        self,
        provider: VMProvider = VMProvider.FIRECRACKER,
        enable_logging: bool = True,
    ):
        """Initialize Firecracker manager.
        
        Args:
            provider: VM provider
            enable_logging: Enable logging
        """
        self.provider = provider
        self.enable_logging = enable_logging
        
        self._instances: Dict[str, VMInstance] = {}
        
        if self.enable_logging:
            logger.info(
                "firecracker_manager_initialized",
                extra={"provider": provider.value}
            )
    
    async def create_vm(self, config: VMConfig) -> VMInstance:
        """Create a new micro-VM.
        
        Args:
            config: VM configuration
            
        Returns:
            VMInstance
        """
        if config.vm_id in self._instances:
            raise ValueError(f"VM {config.vm_id} already exists")
        
        instance = VMInstance(
            vm_id=config.vm_id,
            config=config,
            status=VMStatus.CREATING,
            created_at=time.time(),
        )
        
        self._instances[config.vm_id] = instance
        
        try:
            # Create VM based on provider
            if self.provider == VMProvider.FIRECRACKER:
                await self._create_firecracker_vm(instance)
            elif self.provider == VMProvider.E2B:
                await self._create_e2b_vm(instance)
            elif self.provider == VMProvider.DOCKER:
                await self._create_docker_vm(instance)
            else:
                # Local fallback (no actual VM)
                instance.status = VMStatus.RUNNING
                instance.endpoint = "local://sandbox"
            
            if self.enable_logging:
                logger.info(
                    "vm_created",
                    extra={
                        "vm_id": config.vm_id,
                        "provider": self.provider.value,
                        "status": instance.status.value,
                    }
                )
        
        except Exception as e:
            instance.status = VMStatus.FAILED
            instance.metadata["error"] = str(e)
            
            if self.enable_logging:
                logger.error(
                    "vm_creation_failed",
                    extra={
                        "vm_id": config.vm_id,
                        "error": str(e),
                    },
                    exc_info=True,
                )
            
            raise
        
        return instance
    
    async def terminate_vm(self, vm_id: str) -> bool:
        """Terminate a micro-VM.
        
        Args:
            vm_id: VM identifier
            
        Returns:
            True if terminated successfully
        """
        instance = self._instances.get(vm_id)
        if not instance:
            return False
        
        try:
            # Terminate based on provider
            if self.provider == VMProvider.FIRECRACKER:
                await self._terminate_firecracker_vm(instance)
            elif self.provider == VMProvider.E2B:
                await self._terminate_e2b_vm(instance)
            elif self.provider == VMProvider.DOCKER:
                await self._terminate_docker_vm(instance)
            
            instance.status = VMStatus.TERMINATED
            
            # Remove from instances if auto-teardown
            if instance.config.auto_teardown:
                del self._instances[vm_id]
            
            if self.enable_logging:
                logger.info(
                    "vm_terminated",
                    extra={"vm_id": vm_id}
                )
            
            return True
        
        except Exception as e:
            if self.enable_logging:
                logger.error(
                    "vm_termination_failed",
                    extra={
                        "vm_id": vm_id,
                        "error": str(e),
                    },
                    exc_info=True,
                )
            return False
    
    def get_vm(self, vm_id: str) -> Optional[VMInstance]:
        """Get VM instance.
        
        Args:
            vm_id: VM identifier
            
        Returns:
            VMInstance or None
        """
        return self._instances.get(vm_id)
    
    def list_vms(self, status: Optional[VMStatus] = None) -> List[VMInstance]:
        """List all VMs.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of VM instances
        """
        instances = list(self._instances.values())
        
        if status:
            instances = [i for i in instances if i.status == status]
        
        return instances
    
    async def cleanup_expired(self) -> int:
        """Cleanup expired VMs.
        
        Returns:
            Number of VMs cleaned up
        """
        current_time = time.time()
        expired = [
            vm_id for vm_id, instance in self._instances.items()
            if instance.is_expired(current_time)
        ]
        
        count = 0
        for vm_id in expired:
            if await self.terminate_vm(vm_id):
                count += 1
        
        if count > 0 and self.enable_logging:
            logger.info(
                "expired_vms_cleaned",
                extra={"count": count}
            )
        
        return count
    
    async def _create_firecracker_vm(self, instance: VMInstance) -> None:
        """Create Firecracker VM.
        
        Simplified stub - production should use Firecracker SDK.
        
        Args:
            instance: VM instance to create
        """
        # In production: Use Firecracker API
        # For now: Simulate creation
        instance.status = VMStatus.RUNNING
        instance.endpoint = f"firecracker://{instance.vm_id}"
        instance.metadata["simulated"] = True
    
    async def _create_e2b_vm(self, instance: VMInstance) -> None:
        """Create E2B VM.
        
        Simplified stub - production should use E2B SDK.
        
        Args:
            instance: VM instance to create
        """
        # In production: Use E2B SDK
        # For now: Simulate creation
        instance.status = VMStatus.RUNNING
        instance.endpoint = f"e2b://{instance.vm_id}"
        instance.metadata["simulated"] = True
    
    async def _create_docker_vm(self, instance: VMInstance) -> None:
        """Create Docker container as VM fallback.
        
        Args:
            instance: VM instance to create
        """
        # Use Docker as fallback
        try:
            # Create isolated container
            result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", instance.vm_id,
                    "--cpus", str(instance.config.cpu_count),
                    "--memory", f"{instance.config.memory_mb}m",
                    "--network", "none" if not instance.config.network_enabled else "bridge",
                    "python:3.11-slim",
                    "sleep", str(instance.config.timeout_seconds),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            
            container_id = result.stdout.strip()
            instance.status = VMStatus.RUNNING
            instance.endpoint = f"docker://{container_id}"
            instance.metadata["container_id"] = container_id
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker container creation failed: {e.stderr}")
    
    async def _terminate_firecracker_vm(self, instance: VMInstance) -> None:
        """Terminate Firecracker VM."""
        # In production: Use Firecracker API
        pass
    
    async def _terminate_e2b_vm(self, instance: VMInstance) -> None:
        """Terminate E2B VM."""
        # In production: Use E2B SDK
        pass
    
    async def _terminate_docker_vm(self, instance: VMInstance) -> None:
        """Terminate Docker container."""
        container_id = instance.metadata.get("container_id")
        if container_id:
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_id],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                pass


def create_firecracker_manager(
    provider: VMProvider = VMProvider.FIRECRACKER,
) -> FirecrackerManager:
    """Factory function to create Firecracker manager.
    
    Args:
        provider: VM provider
        
    Returns:
        FirecrackerManager instance
    """
    return FirecrackerManager(provider=provider)
