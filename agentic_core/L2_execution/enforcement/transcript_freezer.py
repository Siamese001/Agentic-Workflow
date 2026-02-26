from __future__ import annotations

from typing import Any, MutableSequence


class TranscriptMutationViolation(Exception):
    """Raised when an attempt is made to mutate a frozen execution transcript."""


class FrozenTranscript(MutableSequence[Any]):
    """A read-only wrapper around a transcript that raises an error on mutation."""

    def __init__(self, transcript_data: list[Any]):
        self._data = tuple(transcript_data)  # Store as an immutable tuple

    def __getitem__(self, index: int) -> Any:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def _raise_violation(self, *args: Any, **kwargs: Any) -> None:
        raise TranscriptMutationViolation(
            "Cannot mutate a frozen transcript. It has been sealed for digest computation."
        )

    # Override all mutating methods to raise an error
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
