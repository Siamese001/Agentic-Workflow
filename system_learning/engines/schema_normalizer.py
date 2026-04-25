"""V7 6A.S1B Schema Normalizer.

Converts heterogeneous runtime exhaust into a canonical
``NormalizedEvidenceRecord`` with bound lineage refs and stratified terminal
status. Read-only: never mutates source artifacts.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6A S1B "NORMALIZE EVIDENCE".

KPI surface
-----------
Publishes ``EVIDENCE_FIELD_COMPLETENESS`` (ratio of records that carried all
required fields) via ``publish_kpi_sample``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping

logger = logging.getLogger(__name__)


# Required canonical fields per v7 S1B "BINDS" + "NORMALIZES" lists.
REQUIRED_FIELDS: frozenset[str] = frozenset({
    "trace_id",
    "run_id",
    "replay_key",
    "policy_hash",
    "prompt_hash",
    "context_hash",
    "route_id",
    "artifact_digest",
    "terminal_status",
})


# Allowed terminal-status strata per v7 S1B "STRATIFIES".
TERMINAL_STATUS: frozenset[str] = frozenset({
    "normal_success",
    "degraded_success",
    "safe_abstain",
    "denied_unsafe_request",
    "rerouted_request",
    "hitl_escalated",
    "tool_failure",
    "model_failure",
    "grounding_failure",
    "policy_failure",
    "replay_failure",
    "schema_failure",
    "unresolved_unknown",
})


@dataclass(frozen=True)
class NormalizedEvidenceRecord:
    """Canonical evidence shape consumed by 6A S1D and 6B graders."""

    trace_id: str
    run_id: str
    replay_key: str
    policy_hash: str
    prompt_hash: str
    context_hash: str
    route_id: str
    artifact_digest: str
    terminal_status: str
    canonical_fields: Mapping[str, Any]
    evidence_gaps: tuple[str, ...]
    normalization_warnings: tuple[str, ...]
    eval_ready: bool


@dataclass
class _Counters:
    total: int = 0
    complete: int = 0


class SchemaNormalizer:
    """Normalize raw runtime exhaust into ``NormalizedEvidenceRecord``."""

    def __init__(self) -> None:
        self._counters = _Counters()

    def normalize(self, raw: Mapping[str, Any]) -> NormalizedEvidenceRecord:
        """Normalize a single raw exhaust record.

        ``raw`` is a free-shape mapping. Missing required fields are reported
        in ``evidence_gaps`` and ``eval_ready`` is set to False.
        """
        gaps: list[str] = []
        warnings: list[str] = []
        canonical: dict[str, Any] = {}

        for key in REQUIRED_FIELDS:
            value = raw.get(key)
            if value is None or value == "":
                gaps.append(key)
                canonical[key] = ""
            else:
                canonical[key] = str(value)

        terminal = canonical.get("terminal_status", "")
        if terminal and terminal not in TERMINAL_STATUS:
            warnings.append(f"unknown_terminal_status:{terminal}")

        eval_ready = not gaps
        self._counters.total += 1
        if eval_ready:
            self._counters.complete += 1

        return NormalizedEvidenceRecord(
            trace_id=canonical["trace_id"],
            run_id=canonical["run_id"],
            replay_key=canonical["replay_key"],
            policy_hash=canonical["policy_hash"],
            prompt_hash=canonical["prompt_hash"],
            context_hash=canonical["context_hash"],
            route_id=canonical["route_id"],
            artifact_digest=canonical["artifact_digest"],
            terminal_status=terminal,
            canonical_fields=canonical,
            evidence_gaps=tuple(gaps),
            normalization_warnings=tuple(warnings),
            eval_ready=eval_ready,
        )

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(complete, total)``."""
        return (self._counters.complete, self._counters.total)

    def reset(self) -> None:
        self._counters = _Counters()

    def publish_kpi_sample(self, board: Any) -> None:
        """Publish ``EVIDENCE_FIELD_COMPLETENESS`` to ``board``. Never raises."""
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )
            import time  # noqa: PLC0415

            if self._counters.total == 0:
                ratio = 0.0
            else:
                ratio = self._counters.complete / self._counters.total
            sample = V7KPISample(
                name=V7KPIName.EVIDENCE_FIELD_COMPLETENESS,
                value=ratio,
                timestamp=time.time(),
                source="schema_normalizer",
                metadata={"complete": self._counters.complete,
                          "total": self._counters.total},
            )
            board.record(sample)
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break ingest
            logger.warning("v7_kpi_evidence_field_completeness_failed: %s", exc)


__all__ = [
    "NormalizedEvidenceRecord",
    "REQUIRED_FIELDS",
    "TERMINAL_STATUS",
    "SchemaNormalizer",
]
