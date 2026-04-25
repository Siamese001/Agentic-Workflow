"""V7 6C.S3C Pattern Synthesizer + S3B First-Bad-Span Localizer.

Distinguishes one-off incidents from systemic patterns and localizes the
first failing span in a trajectory.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
sections 6C S3B "INCIDENT RCA" and 6C S3C "PATTERN SYNTHESIS".

KPI surface
-----------
``ROOT_CAUSE_LOCALIZATION_RATE`` — ratio of incidents localized to a
``first_bad_span`` plus a ``root_cause_class`` (>= 0.90 to be green).
"""

from __future__ import annotations

import logging
import time
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

logger = logging.getLogger(__name__)


class RootCauseClass(str, Enum):
    """Per v7 S3B "ROOT CAUSE CLASSES"."""

    ROUTE_MISS = "ROUTE_MISS"
    CACHE_FALSE_HIT = "CACHE_FALSE_HIT"
    RETRIEVAL_RECALL_GAP = "RETRIEVAL_RECALL_GAP"
    RERANK_PRECISION_GAP = "RERANK_PRECISION_GAP"
    GRAPH_CONTEXT_GAP = "GRAPH_CONTEXT_GAP"
    PROMPT_SLOT_ORDER_ERROR = "PROMPT_SLOT_ORDER_ERROR"
    INSTRUCTION_CONFLICT = "INSTRUCTION_CONFLICT"
    TOOL_ARG_SCHEMA_ERROR = "TOOL_ARG_SCHEMA_ERROR"
    PROVIDER_DRIFT = "PROVIDER_DRIFT"
    POLICY_THRESHOLD_ERROR = "POLICY_THRESHOLD_ERROR"
    RUBRIC_CALIBRATION_ERROR = "RUBRIC_CALIBRATION_ERROR"
    HITL_GATE_ERROR = "HITL_GATE_ERROR"
    UWG_SCOPE_ERROR = "UWG_SCOPE_ERROR"
    REPLAY_INTEGRITY_ERROR = "REPLAY_INTEGRITY_ERROR"
    EVIDENCE_LINEAGE_LOSS = "EVIDENCE_LINEAGE_LOSS"
    UNKNOWN_ROOT_CAUSE = "UNKNOWN_ROOT_CAUSE"


@dataclass(frozen=True)
class TraceSpan:
    """Minimal span shape consumed by the localizer."""

    span_id: str
    parent_span_id: str | None
    surface: str
    status: str  # "ok" | "error" | "warn"
    error_class: str | None = None
    started_at: float = 0.0


class FirstBadSpanLocalizer:
    """Walk a span tree and return the earliest non-ok span."""

    def localize(self, spans: Iterable[TraceSpan]) -> TraceSpan | None:
        bad = [s for s in spans if s.status != "ok"]
        if not bad:
            return None
        # Earliest by start time. Ties broken by span_id for determinism.
        return sorted(bad, key=lambda s: (s.started_at, s.span_id))[0]


@dataclass(frozen=True)
class IncidentRCA:
    """Per-incident RCA bundle per v7 S3B "OUTPUT"."""

    incident_id: str
    first_bad_span_id: str | None
    root_cause_class: RootCauseClass
    failure_chain: tuple[str, ...]
    affected_surfaces: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class PatternSynthesisRecord:
    """Output of pattern synthesis per v7 S3C."""

    pattern_id: str
    incident_count: int
    examples: tuple[str, ...]
    counterexamples: tuple[str, ...]
    affected_surfaces: tuple[str, ...]
    blast_radius_estimate: int
    confidence_band: str
    proposed_action_class: str  # one of S3D draft types


class PatternSynthesizer:
    """Cluster incidents and emit ``PatternSynthesisRecord``s."""

    def __init__(self) -> None:
        self._localized: int = 0
        self._total_incidents: int = 0

    def synthesize(
        self, incidents: Iterable[IncidentRCA]
    ) -> tuple[PatternSynthesisRecord, ...]:
        incs = list(incidents)
        # Group by (root_cause_class, primary_surface).
        groups: dict[tuple[RootCauseClass, str], list[IncidentRCA]] = {}
        for inc in incs:
            self._total_incidents += 1
            if (inc.first_bad_span_id is not None
                    and inc.root_cause_class is not RootCauseClass.UNKNOWN_ROOT_CAUSE):
                self._localized += 1
            primary_surface = inc.affected_surfaces[0] if inc.affected_surfaces else ""
            key = (inc.root_cause_class, primary_surface)
            groups.setdefault(key, []).append(inc)

        records: list[PatternSynthesisRecord] = []
        for (rc_class, surface), members in groups.items():
            count = len(members)
            avg_confidence = sum(m.confidence for m in members) / count
            # blast-radius estimator: union of surfaces across incidents.
            all_surfaces: Counter = Counter()
            for m in members:
                all_surfaces.update(m.affected_surfaces)
            band = ("high" if avg_confidence >= 0.75
                    else "medium" if avg_confidence >= 0.4
                    else "low")
            action_class = (
                "LOCAL_PATCH" if count == 1
                else "THRESHOLD_CHANGE" if count <= 3
                else "POLICY_CLARIFICATION" if rc_class is RootCauseClass.POLICY_THRESHOLD_ERROR
                else "RUBRIC_UPDATE" if rc_class is RootCauseClass.RUBRIC_CALIBRATION_ERROR
                else "HOLD_FOR_MORE_EVIDENCE" if rc_class is RootCauseClass.UNKNOWN_ROOT_CAUSE
                else "RETRIEVAL_PROFILE_UPDATE" if rc_class in {
                    RootCauseClass.RETRIEVAL_RECALL_GAP,
                    RootCauseClass.RERANK_PRECISION_GAP,
                    RootCauseClass.CACHE_FALSE_HIT,
                }
                else "PROMPT_UPDATE" if rc_class in {
                    RootCauseClass.PROMPT_SLOT_ORDER_ERROR,
                    RootCauseClass.INSTRUCTION_CONFLICT,
                }
                else "TOOL_CONTRACT_TIGHTENING" if rc_class is RootCauseClass.TOOL_ARG_SCHEMA_ERROR
                else "GOLDEN_SET_ADDITION"
            )
            records.append(PatternSynthesisRecord(
                pattern_id=f"{rc_class.value}::{surface}",
                incident_count=count,
                examples=tuple(m.incident_id for m in members[:3]),
                counterexamples=(),
                affected_surfaces=tuple(s for s, _ in all_surfaces.most_common()),
                blast_radius_estimate=sum(all_surfaces.values()),
                confidence_band=band,
                proposed_action_class=action_class,
            ))
        return tuple(records)

    @property
    def localization_counters(self) -> tuple[int, int]:
        """Return ``(localized, total_incidents)``."""
        return (self._localized, self._total_incidents)

    def reset(self) -> None:
        self._localized = 0
        self._total_incidents = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._localized / self._total_incidents
                if self._total_incidents > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.ROOT_CAUSE_LOCALIZATION_RATE,
                value=ratio,
                timestamp=time.time(),
                source="pattern_synthesizer",
                metadata={"localized": self._localized,
                          "total": self._total_incidents},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break synth
            logger.warning("v7_kpi_root_cause_localization_failed: %s", exc)


__all__ = [
    "RootCauseClass",
    "TraceSpan",
    "FirstBadSpanLocalizer",
    "IncidentRCA",
    "PatternSynthesisRecord",
    "PatternSynthesizer",
]
