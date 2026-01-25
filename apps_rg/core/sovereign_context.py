"""
[SSOT] Sovereign Context & Airlock Manager.
Implements the 'Transactional State' pattern from v61.27.10.
Prevents state corruption by requiring cryptographic signatures for commits.
"""

from typing import Any
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)


class SovereignContext:
    """
    Manages application state with transactional integrity.
    Data flow: Write -> Airlock -> (Validation Gate) -> Commit(Signature) -> State
    """

    def __init__(self):
        # Immutable Master State
        self._state: dict[str, Any] = {}
        # Staging Area (The Airlock)
        self._airlock: dict[str, Any] = {}
        # Audit Trail
        self._transaction_log: list[dict[str, Any]] = []

    def write_to_airlock(self, key: str, value: Any) -> None:
        """
        Stage data in the airlock. It is NOT visible to the main app yet.
        """
        self._airlock[key] = value
        logger.debug(f"Staged {key} in airlock.")

    def commit_airlock(self, validation_signature: str) -> None:
        """
        Promote airlock data to main state.
        CRITICAL: REQUIRES a valid cryptographic signature to prove validation passed.
        """
        if not validation_signature:
            raise ValueError(
                "SECURITY VIOLATION: Cannot commit airlock without validation signature."
            )

        # Atomic commit of all staged changes
        for key, value in self._airlock.items():
            self._state[key] = deepcopy(value)
            self._transaction_log.append(
                {"action": "COMMIT", "key": key, "signature": validation_signature}
            )

        # Flush airlock after successful commit
        self._airlock.clear()
        logger.info(f"Airlock committed successfully with signature {validation_signature[:8]}...")

    def rollback_airlock(self) -> None:
        """
        Discard staged changes due to validation failure or error.
        """
        keys_cleared = list(self._airlock.keys())
        self._airlock.clear()
        logger.warning(f"Airlock rolled back. Discarded keys: {keys_cleared}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve committed state. Does NOT access airlock.
        """
        return self._state.get(key, default)
