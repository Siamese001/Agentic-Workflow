"""V7 6A.S1C Observer Compliance Recorder.

Produces ``ObserverComplianceReceipt`` records proving that 6A operated under
the read-only observer law (no L4 writes, no BUS U publishes, no live
runtime mutations). The actual enforcement is provided by
``surface_isolation_validator``; this module is the receipt + KPI surface.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6A S1C "OBSERVER LAW".

KPI surface
-----------
Publishes ``OBSERVER_LAW_VIOLATION_COUNT`` (running count of denied write
attempts; expected to be zero). Threshold: EQ 0.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ObserverComplianceReceipt:
    """Receipt proving observer-law compliance for one ingest pass."""

    pass_id: str
    touched_surfaces: tuple[str, ...]
    denied_write_attempts: tuple[str, ...]
    isolation_status: str  # "clean" | "violations_detected"
    timestamp: float


@dataclass
class _State:
    violation_count: int = 0
    receipts: list[ObserverComplianceReceipt] = field(default_factory=list)


class ObserverComplianceRecorder:
    """Record observer-law receipts and emit OBSERVER_LAW_VIOLATION_COUNT."""

    def __init__(self) -> None:
        self._state = _State()

    def record(
        self,
        *,
        pass_id: str,
        touched_surfaces: tuple[str, ...],
        denied_write_attempts: tuple[str, ...] = (),
    ) -> ObserverComplianceReceipt:
        """Record one ingest-pass receipt.

        Each entry in ``denied_write_attempts`` increments the violation
        counter — denial is itself the proof of breach (an attempt was made
        even if it was blocked).
        """
        is_clean = not denied_write_attempts
        receipt = ObserverComplianceReceipt(
            pass_id=pass_id,
            touched_surfaces=tuple(touched_surfaces),
            denied_write_attempts=tuple(denied_write_attempts),
            isolation_status="clean" if is_clean else "violations_detected",
            timestamp=time.time(),
        )
        self._state.receipts.append(receipt)
        self._state.violation_count += len(denied_write_attempts)
        return receipt

    @property
    def violation_count(self) -> int:
        return self._state.violation_count

    @property
    def receipts(self) -> tuple[ObserverComplianceReceipt, ...]:
        return tuple(self._state.receipts)

    def reset(self) -> None:
        self._state = _State()

    def publish_kpi_sample(self, board: Any) -> None:
        """Publish ``OBSERVER_LAW_VIOLATION_COUNT``. Never raises."""
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            board.record(V7KPISample(
                name=V7KPIName.OBSERVER_LAW_VIOLATION_COUNT,
                value=float(self._state.violation_count),
                timestamp=time.time(),
                source="observer_compliance_recorder",
                metadata={"receipts": len(self._state.receipts)},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break ingest
            logger.warning(
                "v7_kpi_observer_law_violation_count_failed: %s", exc
            )


__all__ = ["ObserverComplianceReceipt", "ObserverComplianceRecorder"]
