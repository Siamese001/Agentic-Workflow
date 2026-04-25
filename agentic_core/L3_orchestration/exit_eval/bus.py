"""BUS P / BUS T emission.

Per grader_composition_spec §7, every gate emits one row to BUS P per run
containing aggregate + dimension_vector. BUS T captures the full
trajectory; this module emits rows in the BUS-P-compatible shape and
delegates persistence to a caller-supplied sink.

By H8 fail-mode matrix, a BUS write failure routes the run to X3B with
``AUDIT_UNAVAILABLE`` — this module raises; callers fail-close.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable


class BusWriteError(RuntimeError):
    """BUS write sink failed. Caller must fail-close per H8."""


@dataclass(frozen=True)
class BusRow:
    """One gate's bus P record.

    Shape matches grader_composition_spec §7 exactly. Extra keys may be
    added via ``extras``; downstream consumers ignore unknown keys.
    """

    run_id: str
    gate: str
    rubric_version: str
    composition: str
    aggregate_score: float | None
    aggregate_threshold: float | None
    passed: bool
    abstain: bool
    dimension_vector: tuple[dict[str, Any], ...]
    reason_codes: tuple[str, ...]
    track: str
    trajectory_class: str
    extras: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize as a single JSON-line record."""
        payload = {
            "run_id": self.run_id,
            "gate": self.gate,
            "rubric_version": self.rubric_version,
            "composition": self.composition,
            "aggregate_score": self.aggregate_score,
            "aggregate_threshold": self.aggregate_threshold,
            "passed": self.passed,
            "abstain": self.abstain,
            "dimension_vector": list(self.dimension_vector),
            "reason_codes": list(self.reason_codes),
            "track": self.track,
            "trajectory_class": self.trajectory_class,
        }
        payload.update(self.extras)
        return json.dumps(payload, sort_keys=True)


class BusEmitter:
    """Emits bus rows through an injected sink.

    Sink is any callable ``(BusRow) -> None``. This decouples the
    evaluation framework from the concrete persistence layer (JSONL file,
    Kafka topic, OTel span, ledger write, etc.).
    """

    def __init__(self, sink: Callable[[BusRow], None]) -> None:
        self._sink = sink

    def emit(self, row: BusRow) -> None:
        try:
            self._sink(row)
        except (OSError, RuntimeError) as exc:
            raise BusWriteError(f"BUS sink failed: {exc}") from exc

    def emit_many(self, rows: Iterable[BusRow]) -> None:
        for row in rows:
            self.emit(row)


def jsonl_sink(path: str | Path) -> Callable[[BusRow], None]:
    """File-backed sink that appends one JSON line per row.

    Returns a callable suitable for ``BusEmitter(sink)``. Uses
    ``encoding="utf-8"`` per constitutional §all-file-io requirement.
    """
    target = Path(path)

    def _write(row: BusRow) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(row.to_json())
            fh.write("\n")

    return _write


def memory_sink() -> tuple[Callable[[BusRow], None], list[BusRow]]:
    """In-memory sink for testing. Returns (sink, captured_rows_list)."""
    captured: list[BusRow] = []

    def _capture(row: BusRow) -> None:
        captured.append(row)

    return _capture, captured


__all__ = ["BusEmitter", "BusRow", "BusWriteError", "jsonl_sink", "memory_sink"]
