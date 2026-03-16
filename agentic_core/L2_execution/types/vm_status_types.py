from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "vm_status_types")
emit_determinism_digest("p0", "vm_status_types")

_emit_dispatches_healing_run("p1", "vm_status_types", "L2")
_emit_routes_through("p1", "vm_status_types", "L2")
_emit_escalates_to_human("p1", "vm_status_types", "L2")
_emit_reads_policy_state("p1", "vm_status_types", "L2")

_emit_applies_guardrail("p0", "vm_status_types", "p0_governance")
_emit_snapshots_state("p0", "vm_status_types", "state_snapshot")

"Types and models for FirecrackerManager."
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "VmInstance.is_expired")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VmInstance.is_expired".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        current_time: Any = current_time or get_clock().now_epoch()
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
