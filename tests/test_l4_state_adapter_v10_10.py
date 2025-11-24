# FILE: tests/test_l4_state_adapter_v10_10.py

"""Focused tests for L4 state adapter helpers in v10_10.

Covers:
  - _prune_memory: bounded retention for messages and RAG history.
  - record_correction_event: guarded correction_journal append.

These tests use small local dataclasses to keep the checks focused on
behavior rather than the full WorkflowState schema. The helpers are
implemented in a duck-typed way, so this remains representative of real
usage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from l4 import _prune_memory, record_correction_event  # type: ignore[import]


@dataclass
class FakeStateNoMemory:
    """State without any of the optional memory fields.

    Used to confirm that helpers are strict no-ops when the expected
    attributes are not present on the state object.
    """

    value: int = 0


@dataclass
class FakeStateWithMemory:
    """State exposing the optional memory/journal fields L4 operates on."""

    messages: List[Any] = field(default_factory=list)
    rag_history: List[Any] = field(default_factory=list)
    correction_journal: List[Dict[str, Any]] = field(default_factory=list)


def test_prune_memory_no_relevant_fields_is_noop() -> None:
    state = FakeStateNoMemory(value=1)

    new_state = _prune_memory(state)  # type: ignore[arg-type]

    # No messages/RAG fields -> helper should return the original state
    # object without attempting to mutate or re-wrap it.
    assert new_state is state
    assert new_state.value == 1


def test_prune_memory_trims_messages_and_rag_history() -> None:
    # Create a state with more entries than the hard cap to ensure
    # truncation logic is exercised.
    state = FakeStateWithMemory(
        messages=list(range(300)),
        rag_history=list(range(300)),
    )

    new_state = _prune_memory(state)  # type: ignore[arg-type]

    # Original state must not be mutated in-place.
    assert new_state is not state

    # Messages are truncated from the front, keeping the most recent items.
    assert len(new_state.messages) == 200
    assert new_state.messages[0] == 100
    assert new_state.messages[-1] == 299

    # RAG history is also truncated to the same bound.
    assert len(new_state.rag_history) == 200
    assert new_state.rag_history[0] == 100
    assert new_state.rag_history[-1] == 299


def test_record_correction_event_no_journal_field_is_noop() -> None:
    state = FakeStateNoMemory(value=2)

    new_state = record_correction_event(  # type: ignore[arg-type]
        state,
        surface="l3.self_correction",
        message="example",
        metadata={"severity": 1},
        ctx=None,
    )

    # Without a correction_journal attribute, this helper must be a
    # schema-safe no-op.
    assert new_state is state
    assert new_state.value == 2


def test_record_correction_event_appends_entry_to_journal() -> None:
    state = FakeStateWithMemory()

    new_state = record_correction_event(  # type: ignore[arg-type]
        state,
        surface="l3.self_correction",
        message="bad_draft_detected",
        metadata={"severity": 2, "kind": "test"},
        ctx=None,
    )

    # The state may be replaced rather than mutated; always inspect the
    # returned instance.
    assert isinstance(new_state, FakeStateWithMemory)

    assert len(new_state.correction_journal) == 1
    entry = new_state.correction_journal[0]

    assert entry["surface"] == "l3.self_correction"
    assert entry["message"] == "bad_draft_detected"
    # Metadata should be materialized into a plain dict and preserved.
    assert entry["metadata"] == {"severity": 2, "kind": "test"}
