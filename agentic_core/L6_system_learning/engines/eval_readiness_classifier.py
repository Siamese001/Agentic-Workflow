"""V7 6A.S1D Eval Readiness Classifier.

Decides whether a ``NormalizedEvidenceRecord`` is ready for 6B grading.
Outputs one of four verdicts and emits an ``EvalReadinessReceipt``.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6A S1D "EVIDENCE READINESS GATE".

KPI surface
-----------
Publishes ``EVAL_READINESS_COVERAGE`` (ratio of records that reached
READY_FOR_6B or PARTIAL_BUT_SCORABLE) to a board via ``publish_kpi_sample``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .schema_normalizer import NormalizedEvidenceRecord

logger = logging.getLogger(__name__)


class ReadinessVerdict(str, Enum):
    """Per v7 S1D "DECIDES"."""

    READY_FOR_6B = "READY_FOR_6B"
    PARTIAL_BUT_SCORABLE = "PARTIAL_BUT_SCORABLE"
    HOLD_FOR_MISSING_EVIDENCE = "HOLD_FOR_MISSING_EVIDENCE"
    NON_EVALUABLE_PACKET = "NON_EVALUABLE_PACKET"


@dataclass(frozen=True)
class EvalReadinessReceipt:
    """Receipt produced by the readiness gate."""

    record_trace_id: str
    record_run_id: str
    verdict: ReadinessVerdict
    missing_fields: tuple[str, ...]
    notes: str


# Fields that, when missing, downgrade past READY_FOR_6B but may still be
# "PARTIAL_BUT_SCORABLE" (per v7 S1D "PARTIAL_BUT_SCORABLE" semantics).
_PARTIAL_OK_FIELDS: frozenset[str] = frozenset({
    "context_hash",
    "artifact_digest",
})

# Fields whose absence renders the packet non-evaluable.
_NON_EVALUABLE_FIELDS: frozenset[str] = frozenset({
    "trace_id",
    "run_id",
    "replay_key",
})


class EvalReadinessClassifier:
    """Classify normalized evidence into 6B readiness verdicts."""

    def __init__(self) -> None:
        self._total: int = 0
        self._ready_or_partial: int = 0

    def classify(
        self, record: NormalizedEvidenceRecord
    ) -> EvalReadinessReceipt:
        """Return a verdict for ``record`` and update internal counters."""
        self._total += 1
        gaps = set(record.evidence_gaps)

        if gaps & _NON_EVALUABLE_FIELDS:
            verdict = ReadinessVerdict.NON_EVALUABLE_PACKET
            note = (
                f"non-evaluable: missing {sorted(gaps & _NON_EVALUABLE_FIELDS)}"
            )
        elif not gaps:
            verdict = ReadinessVerdict.READY_FOR_6B
            note = "all required fields present"
            self._ready_or_partial += 1
        elif gaps <= _PARTIAL_OK_FIELDS:
            verdict = ReadinessVerdict.PARTIAL_BUT_SCORABLE
            note = f"partial: missing {sorted(gaps)} (scorable subset)"
            self._ready_or_partial += 1
        else:
            verdict = ReadinessVerdict.HOLD_FOR_MISSING_EVIDENCE
            note = f"hold: missing {sorted(gaps)}"

        return EvalReadinessReceipt(
            record_trace_id=record.trace_id,
            record_run_id=record.run_id,
            verdict=verdict,
            missing_fields=tuple(sorted(gaps)),
            notes=note,
        )

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(ready_or_partial, total)``."""
        return (self._ready_or_partial, self._total)

    def reset(self) -> None:
        self._total = 0
        self._ready_or_partial = 0

    def publish_kpi_sample(self, board: Any) -> None:
        """Publish ``EVAL_READINESS_COVERAGE``. Never raises."""
        try:
            from .v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )
            import time  # noqa: PLC0415

            ratio = (
                self._ready_or_partial / self._total
                if self._total > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.EVAL_READINESS_COVERAGE,
                value=ratio,
                timestamp=time.time(),
                source="eval_readiness_classifier",
                metadata={"ready_or_partial": self._ready_or_partial,
                          "total": self._total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break ingest
            logger.warning("v7_kpi_eval_readiness_coverage_failed: %s", exc)


__all__ = [
    "ReadinessVerdict",
    "EvalReadinessReceipt",
    "EvalReadinessClassifier",
]
