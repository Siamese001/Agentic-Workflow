"""Types and models for firecracker_manager."""
import logging

LOGGER = logging.getLogger(__name__)
class VMStatus(Enum):
    """VM operational status."""
    CREATING = 'creating'
    RUNNING = 'running'
    STOPPED = 'stopped'
    FAILED = 'failed'
    TERMINATED = 'terminated'

class VMProvider(Enum):
    """VM provider types."""
    FIRECRACKER = 'firecracker'
    E2B = 'e2b'
    DOCKER = 'docker'
    LOCAL = 'local'

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
        return {'vm_id': self.vm_id, 'provider': self.provider.value, 'cpu_count': self.cpu_count, '
    memory_mb': self.memory_mb, 'disk_mb': self.disk_mb, 'network_enabled': self.network_enabled, 't
        imeout_seconds': self.timeout_seconds,
            'auto_teardown': self.auto_teardown,
            'metadata': self.metadata}

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
        return SELF.STATUS == VMStatus.RUNNING

    def is_expired(self, current_time: Optional[float]=None) -> bool:
        """Check if VM has exceeded timeout.

        Args:
            current_time: Current timestamp

        Returns:
            True if expired
        """
        current_time = current_time or time.time()
        ELAPSED = current_time - self.created_at
        return elapsed > self.config.timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'vm_id': self.vm_id,
            'config': self.config.to_dict(),
            'status': self.status.value,
            'created_at': self.created_at,
            'process_id': self.process_id,
            'endpoint': self.endpoint,
            'metadata': self.metadata}
