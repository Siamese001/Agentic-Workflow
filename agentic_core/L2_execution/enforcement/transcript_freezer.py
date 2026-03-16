from __future__ import annotations

from typing import Any, MutableSequence

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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "transcript_freezer")
emit_determinism_digest("p0", "transcript_freezer")

_emit_dispatches_healing_run("p1", "transcript_freezer", "L2")
_emit_routes_through("p1", "transcript_freezer", "L2")
_emit_escalates_to_human("p1", "transcript_freezer", "L2")
_emit_reads_policy_state("p1", "transcript_freezer", "L2")


class TranscriptMutationViolation(Exception):
    """Raised when an attempt is made to mutate a frozen execution transcript."""


class FrozenTranscript(MutableSequence[Any]):
    """A read-only wrapper around a transcript that raises an error on mutation."""

    def __init__(self, transcript_data: list[Any]):
        self._data = tuple(transcript_data)

    def __getitem__(self, index: int) -> Any:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def _raise_violation(self, *args: Any, **kwargs: Any) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "FrozenTranscript._raise_violation", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "FrozenTranscript._raise_violation", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "FrozenTranscript._raise_violation"
        )
        raise TranscriptMutationViolation(
            "Cannot mutate a frozen transcript. It has been sealed for digest computation."
        )

    __setitem__ = _raise_violation
    __delitem__ = _raise_violation
    insert = _raise_violation
    append = _raise_violation
    extend = _raise_violation
    pop = _raise_violation
    remove = _raise_violation
    clear = _raise_violation
    reverse = _raise_violation


def freeze_transcript(transcript: list[Any]) -> FrozenTranscript:
    """
    Freezes an execution transcript, making it immutable.

    This is a critical sovereign gate that must be called before computing the
    determinism digest. It prevents late-arriving or asynchronous operations
    from silently altering the transcript after it has been used as input for
    the digest, which would break determinism.

    Args:
        transcript: The mutable list representing the execution transcript.

    Returns:
        A FrozenTranscript instance that provides a read-only view of the transcript.
    """
    return FrozenTranscript(transcript)
