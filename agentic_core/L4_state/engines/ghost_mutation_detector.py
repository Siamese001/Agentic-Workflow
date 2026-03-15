from __future__ import annotations

import uuid
from typing import Any, NamedTuple

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_writes_through,
)

_emit_dispatches_healing_run("p1", "ghost_mutation_detector", "L4")
_emit_routes_through("p1", "ghost_mutation_detector", "L4")
_emit_escalates_to_human("p1", "ghost_mutation_detector", "L4")
_emit_reads_policy_state("p1", "ghost_mutation_detector", "L4")

ExecutionTranscript = list[dict[str, Any]]


class GhostMutationViolation(Exception):
    """Raised when a state mutation is detected that was not recorded in the transcript."""

    def __init__(self, message: str, diff: list[str]):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "GhostMutationViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "GhostMutationViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "GhostMutationViolation.__init__")
        self.message = message
        self.diff = diff
        super().__init__(f"{message} Diff: {diff}")


class ReconciliationResult(NamedTuple):
    """The result of a state reconciliation operation."""

    is_consistent: bool
    violation: GhostMutationViolation | None = None


def _deep_diff(before: Any, after: Any, path: str = "") -> list[str]:
    """Recursively diffs two dictionaries and returns a list of differences."""
    diffs = []
    if isinstance(before, dict) and isinstance(after, dict):
        all_keys = set(before.keys()) | set(after.keys())
        for key in sorted(all_keys):
            new_path = f"{path}.{key}" if path else key
            if key not in before:
                diffs.append(f"Key added: {new_path}")
            elif key not in after:
                diffs.append(f"Key removed: {new_path}")
            elif before[key] != after[key]:
                diffs.extend(_deep_diff(before[key], after[key], new_path))
    elif before != after:
        diffs.append(f"Value changed at {path}: from '{before}' to '{after}'")
    return diffs


def detect_ghost_mutations(
    state_before: dict[str, Any], state_after: dict[str, Any], transcript: ExecutionTranscript
) -> ReconciliationResult:
    """
    Detects hidden state mutations by comparing before/after snapshots against a transcript.

    This function enforces Guarantee #15 by performing a deep diff between the state
    before and after an operation and ensuring that all detected changes are accounted
    for in the official execution transcript. Any un-audited change is a "ghost mutation".

    Args:
        state_before: A snapshot of the system state before the operation.
        state_after: A snapshot of the system state after the operation.
        transcript: The official record of all mutations that were supposed to happen.

    Returns:
        A ReconciliationResult indicating if the state is consistent.
    """
    _emit_writes_through(str(uuid.uuid4()), "Module.detect_ghost_mutations", "L4_STATE")
    expected_state_after = state_before.copy()
    for mutation in transcript:
        if mutation.get("operation") == "set_value":
            key = mutation.get("key")
            value = mutation.get("value")
            if key:
                expected_state_after[key] = value
    diff = _deep_diff(expected_state_after, state_after)
    if diff:
        violation = GhostMutationViolation(
            "Ghost mutation detected: State changed in ways not recorded in the transcript.", diff=diff
        )
        return ReconciliationResult(is_consistent=False, violation=violation)
    return ReconciliationResult(is_consistent=True)
