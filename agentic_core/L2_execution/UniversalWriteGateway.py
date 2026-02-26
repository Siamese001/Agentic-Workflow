"""Universal Write Gateway — Single mutation authority for all writes.

Enforces write permissions, records mutations, and supports replay mode
for deterministic simulation without actual side-effects.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MutationRecord:
    """Immutable record of a write operation for audit trails."""
    timestamp: str
    operation: str  # "write", "append", "delete", "rename", etc.
    path: str
    data_hash: str | None = None
    size_bytes: int | None = None
    permitted: bool = True
    replay_mode: bool = False


@dataclass
class SimulationResult:
    """Result of a simulated write operation in replay mode."""
    operation: str
    path: str
    would_succeed: bool
    simulated_size: int
    simulated_hash: str
    replay_mode: bool = True


class UniversalWriteGateway:
    """Single mutation authority for all FS/DB/vector writes.

    Enforces write permissions, records mutations, and supports replay mode
    for deterministic simulation.
    """

    def __init__(self, replay_mode: bool = False):
        self.replay_mode = replay_mode
        self._write_permissions: dict[str, bool] = {}
        self._mutation_ledger: list[MutationRecord] = []
        self._allowed_paths: set[str] = {
            # Allow writes to specific directories
            "artifacts/",
            "docs/reports/",
            "logs/",
            "temp/",
            ".cache/",
        }
        self._blocked_extensions = {
            # Block direct writes to executable files
            ".exe", ".dll", ".so", ".dylib",
            ".py", ".js", ".ts", ".jsx", ".tsx",
        }

    def check_write_permission(self, path: str, operation: str = "write") -> bool:
        """Check if write operation is permitted."""
        if self.replay_mode:
            return True  # All writes allowed in replay mode (will be simulated)

        # Check if path is in allowed directories
        path_normalized = str(Path(path).as_posix())
        for allowed in self._allowed_paths:
            if path_normalized.startswith(allowed):
                return True

        # Check if trying to write blocked file extension
        ext = Path(path).suffix.lower()
        if ext in self._blocked_extensions:
            return False

        # Default to blocked unless explicitly allowed
        return self._write_permissions.get(path_normalized, False)

    def record_mutation(
        self,
        path: str,
        operation: str,
        data: str | bytes | None = None,
        permitted: bool | None = None
    ) -> MutationRecord:
        """Record mutation for audit trail."""
        if permitted is None:
            permitted = self.check_write_permission(path, operation)

        data_hash = None
        size_bytes = None
        if data is not None:
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = data
            data_hash = hashlib.sha256(data_bytes).hexdigest()
            size_bytes = len(data_bytes)

        record = MutationRecord(
            timestamp=hashlib.sha256(os.urandom(16)).hexdigest()[:16],
            operation=operation,
            path=str(Path(path).as_posix()),
            data_hash=data_hash,
            size_bytes=size_bytes,
            permitted=permitted,
            replay_mode=self.replay_mode
        )
        self._mutation_ledger.append(record)
        return record

    def simulate_write(
        self,
        path: str,
        operation: str,
        data: str | bytes | None = None
    ) -> SimulationResult:
        """Simulate write operation in replay mode."""
        if not self.replay_mode:
            raise RuntimeError("simulate_write called outside replay mode")

        would_succeed = self.check_write_permission(path, operation)
        simulated_size = 0
        simulated_hash = ""

        if data is not None:
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = data
            simulated_size = len(data_bytes)
            simulated_hash = hashlib.sha256(data_bytes).hexdigest()

        return SimulationResult(
            operation=operation,
            path=str(Path(path).as_posix()),
            would_succeed=would_succeed,
            simulated_size=simulated_size,
            simulated_hash=simulated_hash,
            replay_mode=True
        )

    def grant_write_permission(self, path: str) -> None:
        """Grant write permission for a specific path."""
        if self.replay_mode:
            return  # No permission changes in replay mode
        self._write_permissions[str(Path(path).as_posix())] = True

    def revoke_write_permission(self, path: str) -> None:
        """Revoke write permission for a specific path."""
        if self.replay_mode:
            return  # No permission changes in replay mode
        self._write_permissions[str(Path(path).as_posix())] = False

    def get_mutation_ledger(self) -> list[MutationRecord]:
        """Get immutable copy of mutation ledger."""
        return list(self._mutation_ledger)

    def clear_mutation_ledger(self) -> None:
        """Clear mutation ledger (for testing only)."""
        if self.replay_mode:
            return  # No ledger changes in replay mode
        self._mutation_ledger.clear()

    def get_write_stats(self) -> dict[str, Any]:
        """Get statistics about write operations."""
        total = len(self._mutation_ledger)
        permitted = sum(1 for r in self._mutation_ledger if r.permitted)
        blocked = total - permitted
        return {
            "total_mutations": total,
            "permitted_mutations": permitted,
            "blocked_mutations": blocked,
            "replay_mode": self.replay_mode,
            "allowed_paths": list(self._allowed_paths),
            "write_permissions": dict(self._write_permissions)
        }


# Global gateway instance
_global_gateway: UniversalWriteGateway | None = None


def get_write_gateway() -> UniversalWriteGateway:
    """Get the global write gateway instance."""
    global _global_gateway
    if _global_gateway is None:
        _global_gateway = UniversalWriteGateway()
    return _global_gateway


def set_write_gateway(gateway: UniversalWriteGateway) -> None:
    """Set the global write gateway instance (for testing)."""
    global _global_gateway
    _global_gateway = gateway


def reset_write_gateway() -> None:
    """Reset the global write gateway (for testing)."""
    global _global_gateway
    _global_gateway = None
