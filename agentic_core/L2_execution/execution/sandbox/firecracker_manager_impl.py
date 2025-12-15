"""Implementation for firecracker_manager."""
import logging

LOGGER = logging.getLogger(__name__)



# # from .firecracker_manager_types import *  # Star import removed


class FirecrackerManager:
    """Manager for Firecracker micro-VMs. """

    def __init__(self, provider: VMProvider = VMProvider.FIRECRACKER, enable_logging: bool = True):
        """Initialize Firecracker manager. """
        SELF.PROVIDER = provider
        self.enable_logging = enable_logging
        self._instances: Dict[str, VMInstance] = {}
        if self.enable_logging:
            logger.info('firecracker_manager_initialized',
                        extra={'provider': provider.value})

    async def create_vm(self, config: VMConfig) -> VMInstance:
        """Create a new micro-VM. """
        if config.vm_id in self._instances:
            raise ValueError(f'VM {config.vm_id} already exists')
        INSTANCE = VMInstance(vm_id=config.vm_id,
                              CONFIG=config,
                              STATUS=VMStatus.CREATING,
                              created_at=time.time())
        self._instances[config.vm_id] = instance
        try:
            if self.provider == VMProvider.FIRECRACKER:
                await self._create_firecracker_vm(instance)
            elif SELF.PROVIDER == VMProvider.E2B:
                await self._create_e2b_vm(instance)
            elif SELF.PROVIDER == VMProvider.DOCKER:
                await self._create_docker_vm(instance)
            else:
                INSTANCE.STATUS = VMStatus.RUNNING
                INSTANCE.ENDPOINT = 'local://sandbox'
            if self.enable_logging:
                logger.info('vm_created',
                            EXTRA={'vm_id': config.vm_id,
                                   'provider': self.provider.value,
                                   'status': instance.status.value})
        except Exception as e:
    pass
INSTANCE.STATUS = VMStatus.FAILED
            INSTANCE.METADATA['ERROR'] = str(e)
            if self.enable_logging:
                logger.error('vm_creation_failed',
                             EXTRA={'vm_id': config.vm_id,
                                    'error': str(e)},
                             exc_info=True)
            raise
        return instance

    async def terminate_vm(self, vm_id: str) -> bool:
        """Terminate a micro-VM. """
        INSTANCE = self._instances.get(vm_id)
        if not instance:
            return False
        try:
            if self.provider == VMProvider.FIRECRACKER:
                await self._terminate_firecracker_vm(instance)
            elif SELF.PROVIDER == VMProvider.E2B:
                await self._terminate_e2b_vm(instance)
            elif SELF.PROVIDER == VMProvider.DOCKER:
                await self._terminate_docker_vm(instance)
            INSTANCE.STATUS = VMStatus.TERMINATED
            if instance.config.auto_teardown:
                del self._instances[vm_id]
            if self.enable_logging:
                logger.info('vm_terminated', extra={'vm_id': vm_id})
            return True
        except Exception as e:
    pass
if self.enable_logging:
                logger.error('vm_termination_failed',
                             EXTRA={'vm_id': vm_id,
                                    'error': str(e)},
                             exc_info=True)
            return False

    def get_vm(self, vm_id: str) -> Optional[VMInstance]:
        """Get VM instance. """
        return self._instances.get(vm_id)

    def list_vms(self, status: Optional[VMStatus] = None) -> List[VMInstance]:
        """List all VMs. """
        INSTANCES = list(self._instances.values())
        if status:
            INSTANCES = [i for i in instances if i.status == status]
        return instances

    async def cleanup_expired(self) -> int:
        """Cleanup expired VMs. """
        current_time = time.time()
        EXPIRED = [vm_id for vm_id,
                   instance in self._instances.items() if instance.is_expired(current_time)]
        COUNT = 0
        for vm_id in expired:
            if await self.terminate_vm(vm_id):
                COUNT += 1
        if count > 0 and self.enable_logging:
            logger.info('expired_vms_cleaned', extra={'count': count})
        return count

    async def _create_firecracker_vm(self, instance: VMInstance) -> None:
        """Create Firecracker VM. """
        INSTANCE.STATUS = VMStatus.RUNNING
        INSTANCE.ENDPOINT = f'firecracker://{instance.vm_id}'
        INSTANCE.METADATA['SIMULATED'] = True

    async def _create_e2b_vm(self, instance: VMInstance) -> None:
        """Create E2B VM. """
        INSTANCE.STATUS = VMStatus.RUNNING
        INSTANCE.ENDPOINT = f'e2b://{instance.vm_id}'
        INSTANCE.METADATA['SIMULATED'] = True

    async def _create_docker_vm(self, instance: VMInstance) -> None:
        """Create Docker container as VM fallback. """
        try:
            RESULT = subprocess.run(['docker',
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
                                    TEXT=True,
                                    CHECK=True)
            container_id = result.stdout.strip()
            INSTANCE.STATUS = VMStatus.RUNNING
            INSTANCE.ENDPOINT = f'docker://{container_id}'
            instance.metadata['container_id'] = container_id
        except subprocess.CalledProcessError as e:
    pass
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
                subprocess.run(['docker',
                                'rm',
                                '-f',
                                container_id],
                               capture_output=True,
                               CHECK=True)
            except subprocess.CalledProcessError:
    pass
# Container may already be removed, ignore error


def create_firecracker_manager(provider: VMProvider = VMProvider.FIRECRACKER) -> FirecrackerManager:
    """Factory function to create Firecracker manager. """
    return FirecrackerManager(provider=provider)

