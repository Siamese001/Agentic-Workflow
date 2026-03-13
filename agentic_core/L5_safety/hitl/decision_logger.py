"""Addendum 6.3: Deterministic HITL Decision Logger.

Format (no timestamps in key fields):
    HITL_DECISION_N:
    Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D

Rule: No wall-clock timestamps in key fields (determinism requirement).
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
_DEFAULT_LOG_PATH = Path("artifacts/hitl/decisions.jsonl")
_LOCK = threading.Lock()


@dataclass
class HITLDecision:
    """Single HITL decision record. No timestamps in key fields."""

    decision_number: int
    agent: str
    file: str
    violation: str
    proposed: str
    decision: str
    reviewer_signature: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_log_line(self) -> str:
        """Format as the canonical HITL_DECISION_N line."""
        return f"HITL_DECISION_{self.decision_number}: Agent={self.agent} | File={self.file} | Violation={self.violation} | Proposed={self.proposed} | Decision={self.decision}"

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)


class HITLDecisionLogger:
    """Logger for HITL decisions using deterministic format."""

    def __init__(self, log_path: Path | None = None) -> None:
        self._path = log_path or _DEFAULT_LOG_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._counter = 0
        self._records: list[HITLDecision] = []

    def log(
        self,
        agent: str,
        file: str,
        violation: str,
        proposed: str,
        decision: str,
        reviewer_signature: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> HITLDecision:
        """Log a HITL decision. Returns the created record."""
        with _LOCK:
            self._counter += 1
            record = HITLDecision(
                decision_number=self._counter,
                agent=agent,
                file=file,
                violation=violation,
                proposed=proposed,
                decision=decision,
                reviewer_signature=reviewer_signature,
                metadata=metadata or {},
            )
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(record.to_jsonl() + "\n")
            except OSError as exc:
                logger.warning("HITLDecisionLogger: write failed: %s", exc)
            self._records.append(record)
        logger.info(record.to_log_line())
        return record

    def all_records(self) -> list[HITLDecision]:
        with _LOCK:
            return list(self._records)

    def count(self) -> int:
        with _LOCK:
            return self._counter


_DEFAULT_LOGGER: HITLDecisionLogger | None = None


def get_decision_logger(path: Path | None = None) -> HITLDecisionLogger:
    global _DEFAULT_LOGGER
    if _DEFAULT_LOGGER is None:
        _DEFAULT_LOGGER = HITLDecisionLogger(log_path=path)
    return _DEFAULT_LOGGER


__all__ = ["HITLDecision", "HITLDecisionLogger", "get_decision_logger"]
