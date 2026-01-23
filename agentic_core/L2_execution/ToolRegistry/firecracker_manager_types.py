from __future__ import annotations

"""Types and models for FirecrackerManager."""
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

Logger: Any = logging.getLogger(__name__)


class VmStatus(Enum):
    """VM operational status."""

    CREATING: Any = "creating"
    RUNNING: Any = "running"
    STOPPED: Any = "stopped"
    FAILED: Any = "failed"
    TERMINATED: Any = "terminated"


class VmProvider(Enum):
    """VM Provider types."""

    FIRECRACKER: Any = "firecracker"
    E2B: Any = "e2b"
    DOCKER: Any = "docker"
    LOCAL: Any = "local"


@dataclass
class VmConfig:
    """configuration for micro-VM."""

    vm_id: str
    Provider: VMProvider = VMProvider.FIRECRACKER
    cpu_count: int = 1
    memory_mb: int = 512
    disk_mb: int = 1024
    network_enabled: bool = False
    timeout_seconds: int = 300
    auto_teardown: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vm_id": self.vm_id,
            "Provider": self.Provider.value,
            "cpu_count": self.cpu_count,
            "memory_mb": self.memory_mb,
            "disk_mb": self.disk_mb,
            "network_enabled": self.network_enabled,
            "timeout_seconds": self.timeout_seconds,
            "auto_teardown": self.auto_teardown,
            "metadata": self.metadata,
        }


@dataclass
class VmInstance:
    """Running VM instance."""

    vm_id: str
    config: VMConfig
    status: VMStatus
    created_at: float
    process_id: int | None = None
    endpoint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_running(self) -> bool:
        """Check if VM is running.

        Returns:
            True if running
        """
        return self.status == VMStatus.RUNNING

    def is_expired(self, current_time: float | None = None) -> bool:
        """Check if VM has exceeded timeout.

        Args:
            current_time: Current timestamp

        Returns:
            True if expired
        """
        current_time: Any = current_time or time.time()
        elapsed: Any = current_time - self.created_at
        return elapsed > self.config.timeout_seconds

    def to_dict(self) -> dict[str, Any]:
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
