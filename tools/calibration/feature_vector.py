"""Canonical calibration-signal contract for L0 routing paths.

W0.P1 deposit. Encodes the Part 2 Calibration Signal Matrix from
``.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` as typed
dataclasses + a fixture loader. No behavior wiring — W3 will consume
these types when features flow into the router.

Fixture file shape (JSON):

.. code-block:: json

    {
      "path": "R1B",
      "description": "...",
      "signal": "cosine_similarity",
      "invert_score": false,
      "records": [
        {"score": 0.99, "label": true, "namespace": "rg", "notes": "..."},
        ...
      ]
    }

``invert_score`` defaults to ``False``. When ``True`` (R5 abstain), a LOW
score is the positive class — the sweep inverts comparisons accordingly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

PathSignal = Literal["R1A", "R1B", "R3", "R5", "C0"]
"""The five paths this harness calibrates. Mirrors ``L0Route`` enum in
``agentic_core.L0_routing.types.routing_artifact_types`` but intentionally
duplicated here so the harness has zero dependency on live L0 code."""


@dataclass(frozen=True)
class FixtureRecord:
    """One labeled calibration datum.

    Fields:
        score: Decision signal in [0.0, 1.0]. Exact semantics vary per
            path — see the fixture's ``signal`` field.
        label: Ground-truth positive class. ``True`` means "this score
            SHOULD cause the gate to fire" (respecting ``invert_score``).
        namespace: Optional per-tenant / per-agent-class scope.
        notes: Free-text rationale for the label (human rater note).
    """

    score: float
    label: bool
    namespace: str = ""
    notes: str = ""


@dataclass(frozen=True)
class CalibrationFixture:
    """A loaded fixture file."""

    path: PathSignal
    description: str
    signal: str
    invert_score: bool
    records: tuple[FixtureRecord, ...] = field(default_factory=tuple)

    def by_namespace(self, namespace: str) -> tuple[FixtureRecord, ...]:
        """Return only records for ``namespace`` (empty string = no filter)."""
        if not namespace:
            return self.records
        return tuple(r for r in self.records if r.namespace == namespace)

    def namespaces(self) -> tuple[str, ...]:
        """Return the sorted unique namespaces present in the fixture."""
        seen = {r.namespace for r in self.records if r.namespace}
        return tuple(sorted(seen))


def load_fixture(path: Path | str) -> CalibrationFixture:
    """Load a fixture file from disk.

    Raises:
        FileNotFoundError: path does not exist.
        ValueError: file is not valid JSON or missing required fields.
    """
    fixture_path = Path(path)
    if not fixture_path.is_file():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    with fixture_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Fixture root must be an object, got {type(data).__name__}")

    required = {"path", "signal", "records"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"Fixture {fixture_path} missing required fields: {sorted(missing)}")

    path_value = data["path"]
    if path_value not in ("R1A", "R1B", "R3", "R5", "C0"):
        raise ValueError(f"Fixture {fixture_path}: invalid path {path_value!r}")

    records_raw = data["records"]
    if not isinstance(records_raw, list):
        raise ValueError(f"Fixture {fixture_path}: 'records' must be a list")

    records: list[FixtureRecord] = []
    for idx, rec in enumerate(records_raw):
        if not isinstance(rec, dict):
            raise ValueError(f"Fixture {fixture_path} record[{idx}]: not an object")
        score = rec.get("score")
        label = rec.get("label")
        if not isinstance(score, (int, float)):
            raise ValueError(f"Fixture {fixture_path} record[{idx}]: 'score' must be numeric")
        if not isinstance(label, bool):
            raise ValueError(f"Fixture {fixture_path} record[{idx}]: 'label' must be bool")
        if not 0.0 <= float(score) <= 1.0:
            raise ValueError(
                f"Fixture {fixture_path} record[{idx}]: 'score' must be in [0,1], got {score}",
            )
        records.append(
            FixtureRecord(
                score=float(score),
                label=bool(label),
                namespace=str(rec.get("namespace", "")),
                notes=str(rec.get("notes", "")),
            ),
        )

    return CalibrationFixture(
        path=path_value,  # type: ignore[arg-type]
        description=str(data.get("description", "")),
        signal=str(data["signal"]),
        invert_score=bool(data.get("invert_score", False)),
        records=tuple(records),
    )


__all__ = [
    "CalibrationFixture",
    "FixtureRecord",
    "PathSignal",
    "load_fixture",
]
