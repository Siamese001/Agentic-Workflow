"""S3B Incident RCA Engine — full payload constructor.

Constructs an `IncidentRCA` packet matching the v7 spec (lines 683-741)
with first_bad_span localization, 16 root-cause classes, failure chain,
drift cluster map, and confidence/uncertainty bands.

Reference: ``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
lines 683-741 (S3B spec).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)


class RootCauseClass(str, Enum):
    """16 root-cause classes from spec lines 711-726."""

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
class IncidentRCA:
    """v7 S3B output packet (spec lines 728-741)."""

    incident_id: str
    failure_chain: tuple[str, ...]  # ordered span_ids leading to failure
    first_bad_span: str | None
    root_cause_class: RootCauseClass
    drift_cluster_map: Mapping[str, tuple[str, ...]]  # cluster -> example incident_ids
    affected_surfaces: tuple[str, ...]
    proposed_fix_surface: str | None
    evidence_links: tuple[str, ...]
    confidence: float  # 0.0..1.0
    uncertainty_markers: tuple[str, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class IncidentEvidence:
    """Input contract for ``IncidentRCAEngine.investigate``."""

    incident_id: str
    spans: Sequence[Mapping[str, Any]]  # ordered, each with 'span_id', 'status', etc.
    eval_record_id: str
    drift_flags: Sequence[str] = ()
    cluster_examples: Mapping[str, Sequence[str]] | None = None
    evidence_links: Sequence[str] = ()
    suspected_class: RootCauseClass | None = None


# Heuristic mapping from observed defect signals to root-cause classes.
_DEFECT_SIGNAL_TO_CLASS: tuple[tuple[str, RootCauseClass], ...] = (
    ("route_thrash", RootCauseClass.ROUTE_MISS),
    ("cache_false_hit", RootCauseClass.CACHE_FALSE_HIT),
    ("retrieval_recall_gap", RootCauseClass.RETRIEVAL_RECALL_GAP),
    ("rerank_precision_gap", RootCauseClass.RERANK_PRECISION_GAP),
    ("graph_context_gap", RootCauseClass.GRAPH_CONTEXT_GAP),
    ("prompt_slot_order", RootCauseClass.PROMPT_SLOT_ORDER_ERROR),
    ("instruction_conflict", RootCauseClass.INSTRUCTION_CONFLICT),
    ("tool_arg_schema", RootCauseClass.TOOL_ARG_SCHEMA_ERROR),
    ("provider_drift", RootCauseClass.PROVIDER_DRIFT),
    ("policy_threshold", RootCauseClass.POLICY_THRESHOLD_ERROR),
    ("rubric_calibration", RootCauseClass.RUBRIC_CALIBRATION_ERROR),
    ("hitl_gate", RootCauseClass.HITL_GATE_ERROR),
    ("uwg_scope", RootCauseClass.UWG_SCOPE_ERROR),
    ("replay_integrity", RootCauseClass.REPLAY_INTEGRITY_ERROR),
    ("evidence_lineage_loss", RootCauseClass.EVIDENCE_LINEAGE_LOSS),
)


def classify_defects(defect_signals: Sequence[str]) -> RootCauseClass:
    """Map a list of defect signals to a root-cause class.

    Uses first-match against the canonical signal map. If no match, returns
    ``UNKNOWN_ROOT_CAUSE`` — which is a legitimate spec output (line 1272).
    """
    signal_set = {s.lower() for s in defect_signals}
    for token, klass in _DEFECT_SIGNAL_TO_CLASS:
        if any(token in s for s in signal_set):
            return klass
    return RootCauseClass.UNKNOWN_ROOT_CAUSE


def localize_first_bad_span(spans: Sequence[Mapping[str, Any]]) -> str | None:
    """Return the first span whose status is not OK.

    Spans must be in temporal order. ``status`` field accepted values include
    ``"OK"``, ``"FAIL"``, ``"ERROR"``, ``"DENIED"``, ``"TIMEOUT"``, ``"DRIFT"``.
    """
    for span in spans:
        status = str(span.get("status", "OK")).upper()
        if status not in ("OK", "PASS", "SUCCESS"):
            sp_id = span.get("span_id")
            if sp_id is None:
                return None
            return str(sp_id)
    return None


class IncidentRCAEngine:
    """v7 S3B engine — produce actionable RCA packets.

    This engine does NOT itself emit a KPI; localization is tracked by
    ``pattern_synthesizer.PatternSynthesizer`` (S3C) which publishes
    ``ROOT_CAUSE_LOCALIZATION_RATE``. This engine produces the artifact;
    the synthesizer aggregates them.
    """

    def __init__(self) -> None:
        self._packets_built: int = 0
        self._packets_with_first_bad: int = 0
        self._unknown_class_count: int = 0

    def investigate(self, evidence: IncidentEvidence) -> IncidentRCA:
        first_bad = localize_first_bad_span(evidence.spans)
        if first_bad is not None:
            self._packets_with_first_bad += 1

        # Build failure chain: span_ids from start until (and including) first_bad.
        chain: list[str] = []
        for span in evidence.spans:
            sp_id = span.get("span_id")
            if sp_id is None:
                continue
            chain.append(str(sp_id))
            if first_bad is not None and str(sp_id) == first_bad:
                break

        # Classify root cause (spec-supplied takes precedence; else heuristic).
        if evidence.suspected_class is not None:
            klass = evidence.suspected_class
        else:
            klass = classify_defects(evidence.drift_flags)
        if klass is RootCauseClass.UNKNOWN_ROOT_CAUSE:
            self._unknown_class_count += 1

        # Drift-cluster map normalized to tuple values.
        clusters_in: Mapping[str, Sequence[str]] = evidence.cluster_examples or {}
        clusters_out = {k: tuple(v) for k, v in clusters_in.items()}

        # Affected surfaces — derived from spans + drift flags.
        affected = sorted(
            {str(span.get("surface")) for span in evidence.spans
             if span.get("surface")}
        )

        # Confidence: heuristic — high if we localized + classified;
        # medium if either; low if neither.
        if first_bad is not None and klass is not RootCauseClass.UNKNOWN_ROOT_CAUSE:
            confidence = 0.85
        elif first_bad is not None or klass is not RootCauseClass.UNKNOWN_ROOT_CAUSE:
            confidence = 0.55
        else:
            confidence = 0.20

        # Uncertainty markers: explicit list when we couldn't pin facts.
        uncertainty: list[str] = []
        if first_bad is None:
            uncertainty.append("first_bad_span_unresolved")
        if klass is RootCauseClass.UNKNOWN_ROOT_CAUSE:
            uncertainty.append("root_cause_unresolved")
        if not evidence.evidence_links:
            uncertainty.append("evidence_links_empty")

        # Reason codes mirror the drift_flags input verbatim for traceability.
        reason_codes = tuple(evidence.drift_flags)

        # Proposed fix surface: take the first affected surface, if any.
        proposed = affected[0] if affected else None

        self._packets_built += 1
        return IncidentRCA(
            incident_id=evidence.incident_id,
            failure_chain=tuple(chain),
            first_bad_span=first_bad,
            root_cause_class=klass,
            drift_cluster_map=clusters_out,
            affected_surfaces=tuple(affected),
            proposed_fix_surface=proposed,
            evidence_links=tuple(evidence.evidence_links),
            confidence=confidence,
            uncertainty_markers=tuple(uncertainty),
            reason_codes=reason_codes,
        )

    @property
    def counters(self) -> tuple[int, int, int]:
        """Return ``(packets, packets_with_first_bad_span, unknown_class)``."""
        return (
            self._packets_built,
            self._packets_with_first_bad,
            self._unknown_class_count,
        )

    def reset(self) -> None:
        self._packets_built = 0
        self._packets_with_first_bad = 0
        self._unknown_class_count = 0


__all__ = [
    "RootCauseClass",
    "IncidentRCA",
    "IncidentEvidence",
    "IncidentRCAEngine",
    "classify_defects",
    "localize_first_bad_span",
]
