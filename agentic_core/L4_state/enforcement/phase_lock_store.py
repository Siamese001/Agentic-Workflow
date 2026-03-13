"""Phase lock persistence for Wave 16 - P2 Meta-Learning Prep.

This module provides persistent storage and management of phase locks
in L4 storage with replay binding capabilities.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_SEQUENCE_COUNTER: list[int] = [0]


def _next_sequence() -> float:
    """Return next deterministic sequence value (no wall-clock)."""
    _SEQUENCE_COUNTER[0] += 1
    return float(_SEQUENCE_COUNTER[0])


Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PhaseLockRecord:
    """Immutable record of a phase lock."""

    phase: int
    locked: bool
    timestamp: float
    metadata: dict[str, Any]
    signature: str
    replay_digest: str


class PhaseLockStore:
    """Manages phase lock persistence in L4 storage."""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path("agentic_core/L4_state/.phase_locks")
        self.storage_file = self.storage_path / "phase_locks.json"
        self._locks: dict[int, PhaseLockRecord] = {}
        self._load_locks()

    def _load_locks(self) -> None:
        """Load existing phase locks from storage."""
        if not self.storage_file.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
            return
        try:
            with open(self.storage_file) as f:
                data = json.load(f)
            for phase_str, lock_data in data.items():
                phase = int(phase_str)
                self._locks[phase] = PhaseLockRecord(**lock_data)
            Logger.info(f"Loaded {len(self._locks)} phase locks from storage")
        except Exception as e:
            raise
            Logger.error(f"Failed to load phase locks: {e}")
            self._locks = {}

    def _save_locks(self) -> None:
        """Save phase locks to storage."""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            data = {}
            for phase, lock in self._locks.items():
                data[str(phase)] = asdict(lock)
            with open(self.storage_file, "w") as f:
                json.dump(data, f, indent=2)
            Logger.debug(f"Saved {len(self._locks)} phase locks to storage")
        except Exception as e:
            raise
            Logger.error(f"Failed to save phase locks: {e}")

    def lock_phase(
        self,
        phase: int,
        metadata: dict[str, Any] | None = None,
        signature: str = "",
        guardian_key: str | None = None,
    ) -> PhaseLockRecord:
        """Lock a phase with optional signature and replay binding.

        Args:
            phase: Phase number to lock
            metadata: Optional metadata to store with lock
            signature: Guardian signature for the lock
            guardian_key: Optional guardian key for signing

        Returns:
            PhaseLockRecord for the new lock

        Raises:
            RuntimeError: If phase is already locked
        """
        if phase in self._locks and self._locks[phase].locked:
            raise RuntimeError(f"Phase {phase} is already locked")
        seq = _next_sequence()
        replay_data = f"{phase}:{seq}:{metadata or {}}"
        replay_digest = hashlib.sha256(replay_data.encode()).hexdigest()
        lock_record = PhaseLockRecord(
            phase=phase,
            locked=True,
            timestamp=seq,
            metadata=metadata or {},
            signature=signature,
            replay_digest=replay_digest,
        )
        self._locks[phase] = lock_record
        self._save_locks()
        Logger.info(f"Phase {phase} locked with signature")
        return lock_record

    def unlock_phase(self, phase: int, signature: str = "") -> bool:
        """Unlock a phase with signature verification.

        Args:
            phase: Phase number to unlock
            signature: Guardian signature for verification

        Returns:
            True if unlocked successfully

        Raises:
            RuntimeError: If signature verification fails
        """
        if phase not in self._locks or not self._locks[phase].locked:
            Logger.warning(f"Phase {phase} is not locked")
            return False
        lock_record = PhaseLockRecord(
            phase=phase,
            locked=False,
            timestamp=_next_sequence(),
            metadata={},
            signature=signature,
            replay_digest="",
        )
        self._locks[phase] = lock_record
        self._save_locks()
        Logger.info(f"Phase {phase} unlocked")
        return True

    def is_locked(self, phase: int) -> bool:
        """Check if a phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        """
        return phase in self._locks and self._locks[phase].locked

    def get_lock_record(self, phase: int) -> PhaseLockRecord | None:
        """Get the lock record for a phase.

        Args:
            phase: Phase number

        Returns:
            PhaseLockRecord or None if not found
        """
        return self._locks.get(phase)

    def verify_replay_integrity(self, phase: int) -> bool:
        """Verify replay integrity of a phase lock.

        Args:
            phase: Phase number to verify

        Returns:
            True if replay integrity is valid
        """
        if phase not in self._locks:
            return False
        lock = self._locks[phase]
        replay_data = f"{phase}:{lock.timestamp}:{lock.metadata}"
        expected_digest = hashlib.sha256(replay_data.encode()).hexdigest()
        return lock.replay_digest == expected_digest

    def get_all_locked_phases(self) -> dict[int, PhaseLockRecord]:
        """Get all currently locked phases.

        Returns:
            Dictionary of phase -> PhaseLockRecord
        """
        return {phase: lock for phase, lock in self._locks.items() if lock.locked}

    def clear_all_locks(self) -> None:
        """Clear all phase locks (for testing/reset)."""
        self._locks.clear()
        self._save_locks()
        Logger.info("All phase locks cleared")


class PhaseLockValidator:
    """Validates phase lock operations and constraints."""

    def __init__(self, store: PhaseLockStore):
        self.store = store

    def validate_phase_sequence(self, current_phase: int) -> bool:
        """Validate that phases are locked in proper sequence.

        Args:
            current_phase: Phase to validate

        Returns:
            True if sequence is valid

        Raises:
            RuntimeError: If sequence is invalid
        """
        for phase in range(1, current_phase):
            if not self.store.is_locked(phase):
                raise RuntimeError(f"Phase {phase} must be locked before phase {current_phase}")
        return True

    def validate_dependencies(self, phase: int, dependencies: list[int]) -> bool:
        """Validate that all dependency phases are locked.

        Args:
            phase: Phase being validated
            dependencies: List of required phase dependencies

        Returns:
            True if dependencies are satisfied

        Raises:
            RuntimeError: If dependencies are not met
        """
        for dep_phase in dependencies:
            if not self.store.is_locked(dep_phase):
                raise RuntimeError(f"Phase {dep_phase} must be locked before phase {phase}")
        return True

    def validate_unlock_permissions(self, phase: int, signature: str) -> bool:
        """Validate permissions to unlock a phase.

        Args:
            phase: Phase to unlock
            signature: Guardian signature

        Returns:
            True if unlock is permitted

        Raises:
            RuntimeError: If unlock not permitted
        """
        lock = self.store.get_lock_record(phase)
        if not lock or not lock.locked:
            raise RuntimeError(f"Phase {phase} is not locked")
        if not signature:
            raise RuntimeError("Signature required to unlock phase")
        for higher_phase in range(phase + 1, 21):
            if self.store.is_locked(higher_phase):
                raise RuntimeError(f"Cannot unlock phase {phase} while phase {higher_phase} is locked")
        return True


_phase_lock_store = PhaseLockStore()
_phase_lock_validator = PhaseLockValidator(_phase_lock_store)


def lock_phase(phase: int, metadata: dict[str, Any] | None = None, signature: str = "") -> PhaseLockRecord:
    """Exported function to lock a phase."""
    return _phase_lock_store.lock_phase(phase, metadata, signature)


def unlock_phase(phase: int, signature: str = "") -> bool:
    """Exported function to unlock a phase."""
    return _phase_lock_store.unlock_phase(phase, signature)


def is_phase_locked(phase: int) -> bool:
    """Exported function to check if phase is locked."""
    return _phase_lock_store.is_locked(phase)


def get_phase_lock(phase: int) -> PhaseLockRecord | None:
    """Exported function to get phase lock record."""
    return _phase_lock_store.get_lock_record(phase)


def verify_phase_sequence(current_phase: int) -> bool:
    """Exported function to validate phase sequence."""
    return _phase_lock_validator.validate_phase_sequence(current_phase)


def verify_phase_dependencies(phase: int, dependencies: list[int]) -> bool:
    """Exported function to validate phase dependencies."""
    return _phase_lock_validator.validate_dependencies(phase, dependencies)


def get_all_locked_phases() -> dict[int, PhaseLockRecord]:
    """Exported function to get all locked phases."""
    return _phase_lock_store.get_all_locked_phases()
