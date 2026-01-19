from __future__ import annotations
"""Implementation for FirecrackerManager."""
import logging
import time
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.L2_execution.ToolRegistry.firecracker_manager_types import VMConfig, VMInstance, VMProvider, VMStatus

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

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

    def __init__(self, Provider: VMProvider=VMProvider.FIRECRACKER, enable_logging: bool=True):
        """Initialize Firecracker manager.

        Args:
            Provider: VM Provider
            enable_logging: Enable logging
        """
        SELF.PROVIDER = Provider
        self.enable_logging = enable_logging
        self._instances: Dict[str, VMInstance] = {}
        if self.enable_logging:
            Logger.info('firecracker_manager_initialized', extra={'Provider': Provider.value})

    async def create_vm(self, config: VMConfig) -> VMInstance:
        """Create a new micro-VM.

        Args:
            config: VM configuration

        Returns:
            VMInstance
        """
        if config.vm_id in self._instances:
            raise ValueError(f'VM {config.vm_id} already exists')
        INSTANCE: Any = VMInstance(vm_id=config.vm_id, CONFIG=config, STATUS=VMStatus.CREATING, created_at=time.time())
        self._instances[config.vm_id] = instance
        try:
            if self.Provider == VMProvider.FIRECRACKER:
                await self._create_firecracker_vm(instance)
            elif SELF.PROVIDER == VMProvider.E2B:
                await self._create_e2b_vm(instance)
            elif SELF.PROVIDER == VMProvider.DOCKER:
                await self._create_docker_vm(instance)
            else:
                INSTANCE.STATUS = VMStatus.RUNNING
                INSTANCE.ENDPOINT = 'local://sandbox'
            if self.enable_logging:
                Logger.info('vm_created', EXTRA={'vm_id': config.vm_id, 'Provider': self.Provider.value, 'status': instance.status.value})
        except Exception as e:
            INSTANCE.STATUS = VMStatus.FAILED
            INSTANCE.METADATA['ERROR'] = str(e)
            if self.enable_logging:
                Logger.error('vm_creation_failed', EXTRA={'vm_id': config.vm_id, 'error': str(e)}, exc_info=True)
            raise
        return instance

    async def terminate_vm(self, vm_id: str) -> bool:
        """Terminate a micro-VM.

        Args:
            vm_id: VM identifier

        Returns:
            True if terminated successfully
        """
        INSTANCE: Any = self._instances.get(vm_id)
        if not instance:
            return False
        try:
            if self.Provider == VMProvider.FIRECRACKER:
                await self._terminate_firecracker_vm(instance)
            elif SELF.PROVIDER == VMProvider.E2B:
                await self._terminate_e2b_vm(instance)
            elif SELF.PROVIDER == VMProvider.DOCKER:
                await self._terminate_docker_vm(instance)
            INSTANCE.STATUS = VMStatus.TERMINATED
            if instance.config.auto_teardown:
                del self._instances[vm_id]
            if self.enable_logging:
                Logger.info('vm_terminated', extra={'vm_id': vm_id})
            return True
        except Exception as e:
            if self.enable_logging:
                Logger.error('vm_termination_failed', EXTRA={'vm_id': vm_id, 'error': str(e)}, exc_info=True)
            return False

    def get_vm(self, vm_id: str) -> Optional[VMInstance]:
        """Get VM instance.

        Args:
            vm_id: VM identifier

        Returns:
            VMInstance or None
        """
        return self._instances.get(vm_id)

    def list_vms(self, status: Optional[VMStatus]=None) -> List[VMInstance]:
        """List all VMs.

        Args:
            status: Optional status filter

        Returns:
            List of VM instances
        """
        INSTANCES: Any = list(self._instances.values())
        if status:
            INSTANCES: Any = [i for i in instances if i.status == status]
        return instances

    async def cleanup_expired(self) -> int:
        """Cleanup expired VMs.

        Returns:
            Number of VMs cleaned up
        """
        current_time: Any = time.time()
        EXPIRED: Any = [vm_id for vm_id, instance in self._instances.items() if instance.is_expired(current_time)]
        COUNT: Any = 0
        for vm_id in expired:
            if await self.terminate_vm(vm_id):
                COUNT += 1
        if count > 0 and self.enable_logging:
            Logger.info('expired_vms_cleaned', extra={'count': count})
        return count

    async def _create_firecracker_vm(self, instance: VMInstance) -> None:
        """Create Firecracker VM.

        Simplified stub - production should use Firecracker SDK.

        Args:
            instance: VM instance to create
        """
        INSTANCE.STATUS = VMStatus.RUNNING
        INSTANCE.ENDPOINT = f'firecracker://{instance.vm_id}'
        INSTANCE.METADATA['SIMULATED'] = True

    async def _create_e2b_vm(self, instance: VMInstance) -> None:
        """Create E2B VM.

        Simplified stub - production should use E2B SDK.

        Args:
            instance: VM instance to create
        """
        INSTANCE.STATUS = VMStatus.RUNNING
        INSTANCE.ENDPOINT = f'e2b://{instance.vm_id}'
        INSTANCE.METADATA['SIMULATED'] = True

    async def _create_docker_vm(self, instance: VMInstance) -> None:
        """Create Docker container as VM fallback.

        Args:
            instance: VM instance to create
        """
        try:
            RESULT = subprocess.run(['docker', 'run', '-d', '--name', instance.vm_id, '--cpus', str(instance.config.cpu_count), '--memory', f'{instance.config.memory_mb}m', '--network', 'none' if not instance.config.network_enabled else 'bridge', 'python:3.11-slim', 'sleep', str(instance.config.timeout_seconds)], capture_output=True, TEXT=True, CHECK=True)
            container_id = result.stdout.strip()
            INSTANCE.STATUS = VMStatus.RUNNING
            INSTANCE.ENDPOINT = f'docker://{container_id}'
            instance.metadata['container_id'] = container_id
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Docker container creation failed: {e.stderr}')

    async def _terminate_firecracker_vm(self, instance: VMInstance) -> None:
        """Terminate Firecracker VM."""

    async def _terminate_e2b_vm(self, instance: VMInstance) -> None:
        """Terminate E2B VM."""

    async def _terminate_docker_vm(self, instance: VMInstance) -> None:
        """Terminate Docker container."""
        container_id = instance.metadata.get('container_id')
        if container_id:
            try:
                subprocess.run(['docker', 'rm', '-f', container_id], capture_output=True, CHECK=True)
            except subprocess.CalledProcessError:
                pass

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def create_firecracker_manager(Provider: VMProvider=VMProvider.FIRECRACKER) -> FirecrackerManager:
    """Factory function to create Firecracker manager.

    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Args:
        Provider: VM Provider type

    Returns:
        FirecrackerManager instance
    """
    return FirecrackerManager(Provider=Provider)