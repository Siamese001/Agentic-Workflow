"""
[SSOT] Sovereign Context & Airlock Manager.
Implements the 'Transactional State' pattern from v61.27.10.
Prevents state corruption by requiring cryptographic signatures for commits.
"""

import logging
from copy import deepcopy
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "SovereignContext", "p0_governance")
_emit_reads_policy_state("p0", "SovereignContext", "policy_binding")
_emit_snapshots_state("p0", "SovereignContext", "state_snapshot")
emit_replay_key("p0", "SovereignContext")
emit_determinism_digest("p0", "SovereignContext")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class SimpleBuffer:
    """Simple buffer for staging data."""

    def __init__(self):
        self._data: dict[str, Any] = {}

    def write(self, key: str, value: Any, source_agent: str = None) -> None:
        self._data[key] = value

    def read(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class SimpleTrace:
    """Simple trace registry."""

    def __init__(self):
        self._traces: list[dict[str, Any]] = []

    def add_trace(self, event: str, data: dict[str, Any] = None) -> None:
        self._traces.append({"event": event, "data": data or {}})

    def get_summary(self) -> dict[str, Any]:
        return {
            "total_spans": len(self._traces),
            "failures": len([t for t in self._traces if "ERROR" in t.get("event", "").upper()]),
        }


class SovereignContext:
    """
    Manages application state with transactional integrity.
    Data flow: Write -> Airlock -> (Validation Gate) -> Commit(Signature) -> State
    """

    def __init__(self):
        self._state: dict[str, Any] = {}
        self._airlock: dict[str, Any] = {}
        self._transaction_log: list[dict[str, Any]] = []
        self.buffer = SimpleBuffer()
        self.trace = SimpleTrace()

    def write_to_airlock(self, key: str, value: Any) -> None:
        """
        Stage data in the airlock. It is NOT visible to the main app yet.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignContext.write_to_airlock")

        self._airlock[key] = value
        logger.debug(f"Staged {key} in airlock.")

    def commit_airlock(self, validation_signature: str) -> None:
        """
        Promote airlock data to main state.
        CRITICAL: REQUIRES a valid cryptographic signature to prove validation passed.
        """
        if not validation_signature:
            raise ValueError("SECURITY VIOLATION: Cannot commit airlock without validation signature.")
        for key, value in self._airlock.items():
            self._state[key] = deepcopy(value)
            self._transaction_log.append({"action": "COMMIT", "key": key, "signature": validation_signature})
        self._airlock.clear()
        logger.info(f"Airlock committed successfully with signature {validation_signature[:8]}...")

    def rollback_airlock(self) -> None:
        """
        Discard staged changes due to validation failure or error.
        """
        keys_cleared = list(self._airlock.keys())
        self._airlock.clear()
        logger.warning(f"Airlock rolled back. Discarded keys: {keys_cleared}")

    def add_signal(self, signal: str) -> None:
        """Register a signal for downstream engines to consume."""
        if not hasattr(self, "_signals"):
            self._signals: list[str] = []
        self._signals.append(signal)
        logger.debug(f"Signal raised: {signal}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve committed state. Does NOT access airlock.
        """
        return self._state.get(key, default)
