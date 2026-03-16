"""FreezeStateReader -- reads L2 freeze state and gates meta-learning pipeline.

GAP-014: When L2 freeze is active (FREEZ), the meta-learning pipeline must not
run.  This module provides the FreezeStateReader protocol and a concrete
JsonFileBackedFreezeReader that reads from runtime_state.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

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

_emit_applies_guardrail("p0", "freeze_gate", "p0_governance")
_emit_reads_policy_state("p0", "freeze_gate", "policy_binding")
_emit_snapshots_state("p0", "freeze_gate", "state_snapshot")
emit_replay_key("p0", "freeze_gate")
emit_determinism_digest("p0", "freeze_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class FreezeStateReader(Protocol):
    """Protocol: report whether the system is currently frozen."""

    def is_frozen(self) -> bool:
        """Return True if meta-learning should be suppressed due to freeze."""
        ...


class JsonFileBackedFreezeReader:
    """Read freeze state from runtime_state.json.

    The file is read once per is_frozen() call so that state changes on disk
    are reflected without restarting the process.  This is consistent with
    the existing FileBackedConfigProvider behaviour.

    Freeze is declared active when any of the following is true in the JSON:
      - Top-level "freeze" key is truthy.
      - Top-level "status" == "FREEZ".
      - Nested "l2_freeze" key under "flags" is truthy.
    """

    def __init__(self, runtime_state_path: Path) -> None:
        self._path = runtime_state_path

    def is_frozen(self) -> bool:
        """Return True if the runtime state file declares a freeze."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "JsonFileBackedFreezeReader.is_frozen")

        try:
            text = self._path.read_text(encoding="utf-8", errors="replace")
            data: dict = json.loads(text)
        except (OSError, json.JSONDecodeError):
            return False
        if data.get("freeze"):
            return True
        if str(data.get("status", "")).upper() == "FREEZ":
            return True
        flags = data.get("flags", {})
        if isinstance(flags, dict) and flags.get("l2_freeze"):
            return True
        return False


class StaticFreezeReader:
    """Deterministic in-memory freeze reader for tests."""

    def __init__(self, frozen: bool = False) -> None:
        self._frozen = frozen

    def is_frozen(self) -> bool:
        return self._frozen


__all__ = ["FreezeStateReader", "JsonFileBackedFreezeReader", "StaticFreezeReader"]
