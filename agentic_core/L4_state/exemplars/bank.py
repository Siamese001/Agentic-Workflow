"""Exemplar bank core types \u2014 W4 RH4.1.

An ``ExemplarBank`` is an in-memory store of few-shot examples keyed by
``task_class`` (a free-form string label such as ``"rfp_section_draft"`` or
``"judge_score_pairwise"``). The gateway's E0 slot composition consumes
records from this bank via the retriever.

W4 scope:
- Dataclass + store only. No file loading yet (that's W4.a follow-up).
- No embedding-based selection (W7).
- No integration with GoldenContextMixin (W5/W6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass(frozen=True)
class ExemplarRecord:
    """Single few-shot example.

    Attributes
    ----------
    exemplar_id:
        Stable identifier for this example; used in provenance logging.
    task_class:
        Free-form string label grouping examples for a single task type.
    input_text:
        The ``User`` turn the model would see.
    output_text:
        The ideal ``Assistant`` turn for that input.
    tags:
        Keyword hints used by the static retriever for similarity scoring.
    metadata:
        Optional provenance / authoring metadata. MUST NOT carry routing,
        safety, execution, or auth fields (validated at insert time).
    """

    exemplar_id: str
    task_class: str
    input_text: str
    output_text: str
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # Mirrors the E0 slot-security invariant from authority_validator.
    _FORBIDDEN_METADATA: tuple[str, ...] = (
        "route_mode",
        "safety_threshold",
        "execution_tier",
        "auth_token",
    )

    def __post_init__(self) -> None:
        if not self.exemplar_id:
            raise ValueError("exemplar_id must not be empty")
        if not self.task_class:
            raise ValueError("task_class must not be empty")
        if not self.input_text or not self.output_text:
            raise ValueError("input_text and output_text must be non-empty")
        for key in self._FORBIDDEN_METADATA:
            if key in self.metadata:
                raise ValueError(
                    f"ExemplarRecord metadata cannot carry {key!r} per E0 invariant"
                )


class ExemplarBank:
    """Thread-safe in-memory exemplar store keyed by task_class.

    Typical usage::

        bank = ExemplarBank()
        bank.add(ExemplarRecord(
            exemplar_id="ex-001",
            task_class="rfp_section_draft",
            input_text="Draft a security section for a SOC2 RFP.",
            output_text="# Security\\n\\nOur controls...",
            tags=("rfp", "security", "soc2"),
        ))
        examples = bank.by_class("rfp_section_draft")
    """

    def __init__(self) -> None:
        self._store: dict[str, list[ExemplarRecord]] = {}
        self._lock = Lock()

    def add(self, record: ExemplarRecord) -> None:
        """Insert a record. Silently deduplicates by exemplar_id per class."""
        with self._lock:
            bucket = self._store.setdefault(record.task_class, [])
            if any(existing.exemplar_id == record.exemplar_id for existing in bucket):
                return
            bucket.append(record)

    def by_class(self, task_class: str) -> tuple[ExemplarRecord, ...]:
        """Return all records for ``task_class`` (empty tuple if none)."""
        with self._lock:
            return tuple(self._store.get(task_class, ()))

    def count(self, task_class: str | None = None) -> int:
        """Count records in the given class, or total if None."""
        with self._lock:
            if task_class is None:
                return sum(len(v) for v in self._store.values())
            return len(self._store.get(task_class, ()))

    def task_classes(self) -> tuple[str, ...]:
        """Return all known task_class labels in insertion order."""
        with self._lock:
            return tuple(self._store.keys())

    def clear(self) -> None:
        """Remove all records. Used by tests."""
        with self._lock:
            self._store.clear()


__all__ = ["ExemplarBank", "ExemplarRecord"]
