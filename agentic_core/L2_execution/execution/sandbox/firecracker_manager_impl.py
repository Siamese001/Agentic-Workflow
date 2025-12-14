"""Implementation for firecracker_manager."""
import logging


logger = logging.getLogger(__name__)
# from .firecracker_manager_types import *  # Star import removed

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

    def __init__(self, provider: VMProvider=VMProvider.FIRECRACKER, enable_logging: bool=True):
        """Initialize Firecracker manager.

        Args:
            provider: VM provider
            enable_logging: Enable logging
        """
        self.provider = provider
        self.enable_logging = enable_logging
        self._instances: Dict[str, VMInstance] = {}
        if self.enable_logging:
            logger.info('firecracker_manager_initialized', extra={'provider': provider.value})

    async def create_vm(self, config: VMConfig) -> VMInstance:
        """Create a new micro-VM.

        Args:
            config: VM configuration

        Returns:
            VMInstance
        """
        if config.vm_id in self._instances:
            raise ValueError(f'VM {config.vm_id} already exists')
        instance = VMInstance(vm_id=config.vm_id,
            config=config,
            status=VMStatus.CREATING,
            created_at=time.time())
        self._instances[config.vm_id] = instance
        try:
            if self.provider == VMProvider.FIRECRACKER:
                await self._create_firecracker_vm(instance)
            elif self.provider == VMProvider.E2B:
                await self._create_e2b_vm(instance)
            elif self.provider == VMProvider.DOCKER:
                await self._create_docker_vm(instance)
            else:
                instance.status = VMStatus.RUNNING
                instance.endpoint = 'local://sandbox'
            if self.enable_logging:
                logger.info('vm_created',
                    extra={'vm_id': config.vm_id,
                    'provider': self.provider.value,
                    'status': instance.status.value})
        except Exception as e:
            instance.status = VMStatus.FAILED
            instance.metadata['error'] = str(e)
            if self.enable_logging:
                logger.error('vm_creation_failed',
                    extra={'vm_id': config.vm_id,
                    'error': str(e)},
                    exc_info=True)
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
            if self.provider == VMProvider.FIRECRACKER:
                await self._terminate_firecracker_vm(instance)
            elif self.provider == VMProvider.E2B:
                await self._terminate_e2b_vm(instance)
            elif self.provider == VMProvider.DOCKER:
                await self._terminate_docker_vm(instance)
            instance.status = VMStatus.TERMINATED
            if instance.config.auto_teardown:
                del self._instances[vm_id]
            if self.enable_logging:
                logger.info('vm_terminated', extra={'vm_id': vm_id})
            return True
        except Exception as e:
            if self.enable_logging:
                logger.error('vm_termination_failed',
                    extra={'vm_id': vm_id,
                    'error': str(e)},
                    exc_info=True)
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
        expired = [vm_id for vm_id,
            instance in self._instances.items() if instance.is_expired(current_time)]
        count = 0
        for vm_id in expired:
            if await self.terminate_vm(vm_id):
                count += 1
        if count > 0 and self.enable_logging:
            logger.info('expired_vms_cleaned', extra={'count': count})
        return count

    async def _create_firecracker_vm(self, instance: VMInstance) -> None:
        """Create Firecracker VM.

        Simplified stub - production should use Firecracker SDK.

        Args:
            instance: VM instance to create
        """
        instance.status = VMStatus.RUNNING
        instance.endpoint = f'firecracker://{instance.vm_id}'
        instance.metadata['simulated'] = True

    async def _create_e2b_vm(self, instance: VMInstance) -> None:
        """Create E2B VM.

        Simplified stub - production should use E2B SDK.

        Args:
            instance: VM instance to create
        """
        instance.status = VMStatus.RUNNING
        instance.endpoint = f'e2b://{instance.vm_id}'
        instance.metadata['simulated'] = True

    async def _create_docker_vm(self, instance: VMInstance) -> None:
        """Create Docker container as VM fallback.

        Args:
            instance: VM instance to create
        """
        try:
            result = subprocess.run(['docker',
                'run',
                '-d',
                '--name',
                instance.vm_id,
                '--cpus',
                str(instance.config.cpu_count),
                '--memory',
                f'{instance.config.memory_mb}m',
                '--network',
                'none' if not instance.config.network_enabled else 'bridge',
                'python:3.11-slim',
                'sleep',
                str(instance.config.timeout_seconds)],
                capture_output=True,
                text=True,
                check=True)
            container_id = result.stdout.strip()
            instance.status = VMStatus.RUNNING
            instance.endpoint = f'docker://{container_id}'
            instance.metadata['container_id'] = container_id
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Docker container creation failed: {e.stderr}')

    async def _terminate_firecracker_vm(self, instance: VMInstance) -> None:
        """Terminate Firecracker VM."""
        pass

    async def _terminate_e2b_vm(self, instance: VMInstance) -> None:
        """Terminate E2B VM."""
        pass

    async def _terminate_docker_vm(self, instance: VMInstance) -> None:
        """Terminate Docker container."""
        container_id = instance.metadata.get('container_id')
        if container_id:
            try:
                subprocess.run(['docker',
                    'rm',
                    '-f',
                    container_id],
                    capture_output=True,
                    check=True)
            except subprocess.CalledProcessError:
                pass

def create_firecracker_manager(provider: VMProvider=VMProvider.FIRECRACKER) -> FirecrackerManager:
    """Factory function to create Firecracker manager.

    Args:
        provider: VM provider

    Returns:
        FirecrackerManager instance
    """
    return FirecrackerManager(provider=provider)
