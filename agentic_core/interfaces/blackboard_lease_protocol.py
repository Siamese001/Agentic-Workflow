"""
IBlackboardLeaseVerifierProtocol — Protocol for healing-lease verification.

Zero-Ambiguity Standard: Protocol interface only. The previous version of
this file inlined a 250-line secure-filesystem implementation
(read_file/write_file/move_file/delete_file/...) that had zero production
consumers via this import path; that implementation has been removed.
Filesystem operations live in their L2 home; this module exposes only the
Protocol contract.

The Protocol is consumed by L4_state blackboard implementations and by any
L2 helper that needs to verify an agent holds a HealingLease before
mutating a file.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IBlackboardLeaseVerifier(Protocol):
    """Contract for components that verify HealingLease ownership.

    Implementations (e.g., the L4 blackboard) must answer two questions:
      - Does ``agent_id`` currently hold a HealingLease for ``file_path``?
      - Record a security event with the given metadata.
    """

    def verify_healing_lease(self, agent_id: str, file_path: str) -> bool: ...

    def log_security_event(
        self,
        agent_id: str,
        event_type: str,
        file_path: str,
        details: dict[str, Any] | None = None,
    ) -> None: ...


class SandboxViolationError(Exception):
    """Raised when a file operation violates sandbox constraints."""


class HealingLeaseError(Exception):
    """Raised when an agent attempts to write without holding the HealingLease."""


class PreservationViolationError(Exception):
    """Raised when a write operation would delete too much content."""


__all__ = [
    "IBlackboardLeaseVerifier",
    "SandboxViolationError",
    "HealingLeaseError",
    "PreservationViolationError",
]
